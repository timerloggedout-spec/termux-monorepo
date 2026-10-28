"""APK cross-reference toolkit tests — stdlib pytest, no network.

Builds a synthetic APK in-test (binary AXML manifest + minimal DEX
string table + assets + a google-services.json carrying a dummy secret
value that must NEVER survive extraction) and exercises acquire /
extract / classify / cross-validate / findings-render end to end.
"""
import hashlib
import io
import json
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ops.web_adapter_foundry import apk_xref as ax  # noqa: E402

SECRET = "AIzaDUMMY-SECRET-VALUE-DO-NOT-LEAK"


# ------------------------------------------------------------ AXML build

def _pool(strings):
    offsets, blob = [], b""
    for s in strings:
        offsets.append(len(blob))
        enc = s.encode("utf-16-le")
        blob += struct.pack("<H", len(s)) + enc + b"\x00\x00"
    header_size = 28
    strings_start = header_size + 4 * len(strings)
    size = strings_start + len(blob)
    out = struct.pack("<HHIIIIII", 0x0001, header_size, size, len(strings),
                      0, 0, strings_start, 0)
    out += b"".join(struct.pack("<I", o) for o in offsets) + blob
    return out


def _start(strings, tag, attrs):
    idx = {s: i for i, s in enumerate(strings)}
    body = struct.pack("<IIHHHHHH", 0xFFFFFFFF, idx[tag], 20, 20,
                       len(attrs), 0, 0, 0)
    for name, value in attrs:
        if isinstance(value, int):
            raw, vtype, data = 0xFFFFFFFF, 0x10, value
        elif isinstance(value, bool):
            raw, vtype, data = 0xFFFFFFFF, 0x12, int(value)
        else:
            raw, vtype, data = idx[value], 0x03, idx[value]
        body += struct.pack("<IIIHBBI", 0xFFFFFFFF, idx[name], raw, 8, 0,
                            vtype, data)
    return struct.pack("<HHIII", 0x0102, 16, 16 + len(body), 0, 0xFFFFFFFF) + body


def _end(strings, tag):
    idx = {s: i for i, s in enumerate(strings)}
    return struct.pack("<HHIII II", 0x0103, 16, 24, 0, 0xFFFFFFFF,
                       0xFFFFFFFF, idx[tag])


def build_axml():
    strings = ["manifest", "package", "com.example.aitools", "versionCode",
               "versionName", "1.4.2", "uses-sdk", "minSdkVersion",
               "targetSdkVersion", "uses-permission", "name",
               "android.permission.INTERNET", "android.permission.CAMERA",
               "application", "activity", ".MainActivity", "exported",
               "intent-filter", "data", "scheme", "https", "host",
               "app.example.com", "meta-data", "com.example.flag"]
    parts = [_pool(strings)]
    parts.append(_start(strings, "manifest", [("package", "com.example.aitools"),
                                              ("versionCode", 42),
                                              ("versionName", "1.4.2")]))
    parts.append(_start(strings, "uses-sdk", [("minSdkVersion", 24),
                                              ("targetSdkVersion", 34)]))
    parts.append(_end(strings, "uses-sdk"))
    for perm in ("android.permission.INTERNET", "android.permission.CAMERA"):
        parts.append(_start(strings, "uses-permission", [("name", perm)]))
        parts.append(_end(strings, "uses-permission"))
    parts.append(_start(strings, "application", []))
    parts.append(_start(strings, "activity", [("name", ".MainActivity"),
                                              ("exported", 1)]))
    parts.append(_start(strings, "intent-filter", []))
    parts.append(_start(strings, "data", [("scheme", "https"),
                                          ("host", "app.example.com")]))
    parts.append(_end(strings, "data"))
    parts.append(_end(strings, "intent-filter"))
    parts.append(_end(strings, "activity"))
    parts.append(_start(strings, "meta-data", [("name", "com.example.flag")]))
    parts.append(_end(strings, "meta-data"))
    parts.append(_end(strings, "application"))
    parts.append(_end(strings, "manifest"))
    body = b"".join(parts)
    total = 8 + len(body)
    return struct.pack("<HHI", 0x0003, 8, total) + body


def build_dex(strings):
    ids_size = len(strings)
    data_off = 0x70 + 4 * ids_size
    offsets, blob = [], b""
    for s in strings:
        offsets.append(data_off + len(blob))
        enc = s.encode("utf-8")
        assert len(enc) < 128
        blob += bytes([len(enc)]) + enc + b"\x00"
    header = bytearray(0x70)
    header[0:8] = b"dex\n035\x00"
    struct.pack_into("<I", header, 0x20, data_off + len(blob))  # file_size
    struct.pack_into("<I", header, 0x24, 0x70)                  # header_size
    struct.pack_into("<I", header, 0x28, 0x12345678)            # endian
    struct.pack_into("<I", header, 0x38, ids_size)
    struct.pack_into("<I", header, 0x3C, 0x70)
    return bytes(header) + b"".join(struct.pack("<I", o) for o in offsets) + blob


DEX_STRINGS = [
    "https://api.openai.com/v1/chat/completions",
    "https://api.example.com/api/items",
    "llama.cpp",
    "gemma-2b-it",
    "FirebaseAnalytics",
    "okhttp3.OkHttpClient",
]


def build_apk(path):
    gs = {"project_info": {"project_id": "example-proj"},
          "client": [{"api_key": [{"current_key": SECRET}]}]}
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("AndroidManifest.xml", build_axml())
        zf.writestr("classes.dex", build_dex(DEX_STRINGS))
        zf.writestr("assets/model.gguf", b"\x00gguf")
        zf.writestr("google-services.json", json.dumps(gs))
        zf.writestr("lib/arm64-v8a/libllama.so", b"\x7fELF")
    return path


# ------------------------------------------------------------------ tests

def test_axml_and_dex_parsers(tmp_path):
    apk = build_apk(tmp_path / "app.apk")
    ext = ax.extract_apk(apk)
    man = ext["manifest"]
    assert man["package_id"] == "com.example.aitools"
    assert man["version_name"] == "1.4.2" and man["version_code"] == 42
    assert man["min_sdk"] == 24 and man["target_sdk"] == 34
    assert man["permissions"] == ["android.permission.CAMERA",
                                  "android.permission.INTERNET"]
    assert man["components"][0]["name"] == ".MainActivity"
    assert ext["hosts"] and "api.openai.com" in ext["hosts"]
    assert "api.example.com" in ext["hosts"]
    assert "/v1/chat/completions" in ext["api_routes"]
    assert "/api/items" in ext["api_routes"]
    assert ext["file"]["sha256"] == hashlib.sha256(
        Path(apk).read_bytes()).hexdigest()


def test_provider_config_never_leaks_secret_values(tmp_path):
    apk = build_apk(tmp_path / "app.apk")
    ext = ax.extract_apk(apk)
    assert SECRET not in json.dumps(ext)
    cfg = ext["provider_configs"][0]
    assert cfg["provider"] == "google-firebase"
    assert cfg["project_id"] == "example-proj"
    assert "current_key" in cfg["keys_present"]


def test_classification(tmp_path):
    apk = build_apk(tmp_path / "app.apk")
    cls = ax.extract_apk(apk)["classification"]
    assert "ai-client" in cls["classes"]
    assert "local-inference" in cls["classes"]  # llama.cpp + gguf
    assert "openai" in cls["providers"]
    assert "google-firebase" in cls["providers"]
    assert "firebase-analytics" in cls["trackers"]
    assert "https://app.example.com" in cls["routes"]["deeplinks"]
    assert "provider:openai" in cls["tags"]


def _claims(**over):
    base = {"schema": ax.CLAIMS_SCHEMA, "target_id": "aitools",
            "package_id": "com.example.aitools",
            "hosts": ["api.example.com", "api.ghost.example"],
            "endpoints": ["https://api.example.com/api/items",
                          "https://api.example.com/api/ghost"],
            "providers": ["openai", "mistral"],
            "permissions": ["android.permission.INTERNET"],
            "features": [{"name": "llama.cpp bundling",
                          "any_of": ["llama.cpp"]}],
            "claims_to_check": ["100% on your hardware / pure local",
                                "Bundles llama.cpp with Gemma"]}
    base.update(over)
    return base


def test_cross_validate_both_directions(tmp_path):
    apk = build_apk(tmp_path / "app.apk")
    ext = ax.extract_apk(apk)
    res = ax.cross_validate(ext, _claims())
    r2a = "\n".join(res["divergences_repo_to_apk"])
    a2r = "\n".join(res["divergences_apk_to_repo"])
    assert "api.ghost.example" in r2a          # claimed host absent
    assert "/api/ghost" in r2a                 # claimed endpoint absent
    assert "mistral" in r2a                    # claimed provider absent
    assert "api.openai.com" in a2r             # artifact host unclaimed
    assert "firebase-analytics" in a2r         # tracker unclaimed
    assert "android.permission.CAMERA" in a2r  # permission unclaimed
    assert res["verdict"] == "divergences-found"
    outcomes = {c["claim"]: c["outcome"] for c in res["claims_checked"]}
    assert outcomes["100% on your hardware / pure local"] == "contradicted"
    assert outcomes["Bundles llama.cpp with Gemma"] == "supported"


def test_cross_validate_match(tmp_path):
    apk = build_apk(tmp_path / "app.apk")
    ext = ax.extract_apk(apk)
    claims = _claims(
        hosts=ext["hosts"],
        endpoints=[e["url"] for e in ext["endpoints"]],
        providers=[p["id"] for p in ext["providers"]],
        permissions=ext["manifest"]["permissions"],
        features=[], claims_to_check=[])
    # trackers/signals are artifact findings by design; claim them too
    claims["trackers"] = [t["id"] for t in ext["trackers"]]
    res = ax.cross_validate(ext, claims)
    leftover = [d for d in res["divergences_apk_to_repo"]
                if not d.startswith("signal:")]
    assert res["divergences_repo_to_apk"] == []
    assert leftover == []


def test_findings_record_and_markdown_shape(tmp_path):
    apk = build_apk(tmp_path / "app.apk")
    ext = ax.extract_apk(apk)
    res = ax.cross_validate(ext, _claims())
    rec = ax.build_findings_record(
        target_id="aitools", xref_issue="#2064",
        submitter="reverse-engineering-toolkits{test}",
        extraction=ext, xref=res, artifact_source="github-releases")
    assert rec["schema"] == "apk-xref/v1" and rec["kind"] == "findings"
    assert rec["verdict"] == "divergences-found"
    assert rec["artifact_version"] == "1.4.2 (build 42)"
    assert ext["file"]["sha256"] in rec["notes"]
    md = ax.render_findings_markdown(rec)
    headings = [ln[4:] for ln in md.splitlines() if ln.startswith("### ")]
    assert headings == [h for h, _ in ax._FINDING_HEADINGS]
    assert "Divergences — repo to APK" in headings  # form label verbatim


def test_no_artifact_record():
    rec = ax.build_findings_record(
        target_id="nope", xref_issue="#9999",
        submitter="reverse-engineering-toolkits{test}",
        artifact_source="none-known",
        sources_checked=["github-releases: no APK asset published",
                         "f-droid: checked"])
    assert rec["verdict"] == "no-artifact-found"
    assert rec["package_id"] == ""
    assert "f-droid" in rec["notes"]


def test_scan_repo_tree(tmp_path):
    src = tmp_path / "repo"
    (src / "app").mkdir(parents=True)
    (src / "app" / "AndroidManifest.xml").write_text(
        '<manifest package="com.example.aitools">'
        '<uses-permission android:name="android.permission.INTERNET"/>'
        "</manifest>")
    (src / "app" / "api.py").write_text(
        'URL = "https://api.example.com/api/items"\n# uses openai\n')
    claims = ax.scan_repo_tree(src)
    assert claims["package_id"] == "com.example.aitools"
    assert claims["hosts"] == ["api.example.com"]
    assert "android.permission.INTERNET" in claims["permissions"]
    assert "openai" in claims["providers"]


# ------------------------------------------------------------- acquisition

def _fake_fetch(mapping):
    def fetch(url):
        if url in mapping:
            v = mapping[url]
            return v if isinstance(v, bytes) else json.dumps(v).encode()
        raise OSError(f"404 {url}")
    return fetch


def test_acquire_github_and_fdroid(tmp_path):
    apk_bytes = build_apk(tmp_path / "src.apk").read_bytes()
    gh = _fake_fetch({
        "https://api.github.com/repos/o/r/releases?per_page=30": [
            {"tag_name": "v1.4.2", "name": "rel", "published_at": "2026-10-01",
             "assets": [{"name": "app.apk",
                         "browser_download_url": "https://dl.example/app.apk"}]}],
        "https://dl.example/app.apk": apk_bytes})
    got = ax.acquire({"sources": ["github-releases"], "repo": "o/r"},
                     tmp_path / "out", fetch=gh)
    assert got["status"] == "acquired"
    assert got["version"] == "v1.4.2"
    assert got["sha256"] == hashlib.sha256(apk_bytes).hexdigest()

    fd = _fake_fetch({
        "https://f-droid.org/api/v1/packages/com.example.aitools": {
            "packages": [{"versionName": "1.0", "versionCode": 7,
                          "apkName": "com.example.aitools_7.apk"},
                         {"versionName": "1.4.2", "versionCode": 42}]},
        "https://f-droid.org/repo/com.example.aitools_42.apk": apk_bytes})
    got = ax.acquire({"sources": ["f-droid"],
                      "package_id": "com.example.aitools"},
                     tmp_path / "out2", fetch=fd)
    assert got["status"] == "acquired" and got["build"] == 42


def test_acquire_no_artifact_and_play_refusal(tmp_path):
    empty = _fake_fetch({
        "https://api.github.com/repos/o/r/releases?per_page=30": [
            {"tag_name": "v1", "assets": [{"name": "src.zip",
                                           "browser_download_url": "x"}]}]})
    got = ax.acquire({"sources": ["github-releases"], "repo": "o/r"},
                     tmp_path / "out", fetch=empty)
    assert got["status"] == "no-artifact-found"
    assert any("no APK asset" in c for c in got["sources_checked"])
    try:
        ax.download_artifact(
            {"download_url": "https://play.google.com/store/apps/x.apk",
             "asset_name": "x.apk"}, tmp_path)
        raise AssertionError("play download must be refused")
    except ValueError as e:
        assert "Play" in str(e)
