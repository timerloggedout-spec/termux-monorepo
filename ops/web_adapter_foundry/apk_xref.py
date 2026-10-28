#!/usr/bin/env python3
"""APK <-> repo cross-reference toolkit — Web Adapter Foundry utility belt.

The utility belt for the APK cross-reference category (template set:
docs/ops/APK-XREF-TEMPLATES.md, PR #2140; wave briefs #2064-#2123).
Four stages, stdlib only, no Play scraping:

  1. acquire   — fetch a published APK from GitHub Releases, Gitea
                 Releases or F-Droid metadata, with provenance
                 (source, version, build, sha256). A source that has
                 no APK yields a no-artifact-found evidence record,
                 never a substitute build.
  2. extract   — parse the artifact itself: binary AndroidManifest.xml
                 (package, version, permissions, components, deep
                 links), DEX string tables (endpoints/hosts actually
                 embedded), assets, native libs, embedded provider
                 configs and tracker signatures. Where a standard tool
                 (aapt/apktool) is available in CI it can corroborate,
                 but nothing here depends on one: the parsers below are
                 the portable floor that runs anywhere Python 3.10+ runs.
  3. classify  — deterministic tags (class, providers, routes) from
                 apk_signatures.json, so findings land consistently.
  4. xref      — cross-validate against the paired repo brief's claims
                 in BOTH directions and emit the findings record in
                 the apk-xref/v1 shape the cross-reference findings
                 form carries (headings match the form exactly, so the
                 apk-xref intake parser re-reads the markdown losslessly).

Credentials discipline: provider config files contribute provider ids
and key NAMES only; secret values are never extracted or recorded.

CLI:
  apk_xref.py acquire  --source github-releases --repo owner/name --out DIR
  apk_xref.py acquire  --source f-droid --package-id com.example.app --out DIR
  apk_xref.py extract  app.apk --out extraction.json
  apk_xref.py scan-repo PATH --out claims.json
  apk_xref.py xref     --extraction extraction.json --claims claims.json \
                       --target-id aihub --xref-issue '#2064' \
                       --submitter 'reverse-engineering-toolkits{...}' \
                       --out report.json --markdown report.md
  apk_xref.py no-artifact --target-id x --xref-issue '#9999' \
                       --sources-checked github-releases f-droid --out r.json
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import struct
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTRACTION_SCHEMA = "apk-extraction/v1"
CLAIMS_SCHEMA = "apk-claims/v1"
RECORD_SCHEMA = "apk-xref/v1"
ARTIFACT_SOURCES = ("github-releases", "gitea-releases", "f-droid",
                    "google-play", "direct-apk", "other-store", "none-known")
VERDICTS = ("match", "divergences-found", "no-artifact-found")
LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1", "10.0.2.2")
URL_RE = re.compile(r"(?:https?|wss?)://[^\s\"'<>\)\],;\\]+")
API_PATH_RE = re.compile(r"^/(?:api|v\d+|graphql|rest|auth|oauth)(?:/[\w\-./{}:$~]*)?$")
PACKAGE_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z0-9_]+)+$")


def load_signatures(path: str | Path | None = None) -> dict:
    p = Path(path) if path else HERE / "apk_signatures.json"
    return json.loads(p.read_text(encoding="utf-8"))


def host_matches(host: str, pattern: str) -> bool:
    host, pattern = host.lower(), pattern.lower()
    if pattern.startswith("*."):
        return host == pattern[2:] or host.endswith(pattern[1:])
    return host == pattern or host.endswith("." + pattern)


def is_local_host(host: str) -> bool:
    return host in LOCAL_HOSTS or host.startswith("192.168.") or host.startswith("10.")


# ------------------------------------------------------------ binary AXML
# Minimal Android binary XML reader: string pool + start/end elements.
# Attribute values are decoded for the typed forms the manifest uses
# (string, int, bool, reference, float, dimension/enum-as-int).

def _u16(b: bytes, o: int) -> int:
    return struct.unpack_from("<H", b, o)[0]


def _u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def _read_string_pool(b: bytes, off: int) -> list[str]:
    _, _, _, count, _styles, flags, strings_start, _ = struct.unpack_from(
        "<HHIIIIII", b, off)
    utf8 = bool(flags & 0x100)
    base = off + strings_start
    out: list[str] = []
    for i in range(count):
        so = off + 28 + i * 4
        pos = base + _u32(b, so)
        if utf8:
            # two u8/varint lengths (chars, bytes) precede the bytes
            p = pos
            for _ in range(2):
                ln = b[p]
                p += 1
                if ln & 0x80:
                    p += 1
            end = b.index(b"\x00", p)
            out.append(b[p:end].decode("utf-8", errors="replace"))
        else:
            ln = _u32(b, pos) if False else _u16(b, pos)
            p = pos + 2
            if ln & 0x8000:
                ln = ((ln & 0x7FFF) << 16) | _u16(b, p)
                p += 2
            out.append(b[p:p + ln * 2].decode("utf-16-le", errors="replace"))
    return out


def _attr_value(strings: list[str], raw: int, vtype: int, data: int) -> object:
    if raw != 0xFFFFFFFF and raw < len(strings):
        return strings[raw]
    if vtype == 0x03 and data < len(strings):  # string
        return strings[data]
    if vtype == 0x12:  # boolean
        return data != 0
    if vtype in (0x10, 0x11):  # int dec / hex
        return data
    if vtype == 0x01:  # reference
        return f"@{data:08x}"
    return data


def parse_axml(data: bytes) -> list[dict]:
    """Return a flat event list: {tag, attrs} for each start element,
    in document order, with a 'depth' and 'parent' tag attached."""
    if len(data) < 8 or _u32(data, 0) & 0xFFFF != 0x0003:
        raise ValueError("not a binary Android XML file")
    strings: list[str] = []
    events: list[dict] = []
    stack: list[str] = []
    off = 8
    while off + 8 <= len(data):
        ctype, _hsize, csize = struct.unpack_from("<HHI", data, off)
        if csize <= 0:
            break
        if ctype == 0x0001:
            strings = _read_string_pool(data, off)
        elif ctype == 0x0102:  # start element
            ns, name = struct.unpack_from("<II", data, off + 16)
            attr_start, attr_size, attr_count = struct.unpack_from(
                "<HHH", data, off + 24)
            attrs: dict[str, object] = {}
            abase = off + 16 + attr_start
            for i in range(attr_count):
                ao = abase + i * attr_size
                _ans, aname, araw = struct.unpack_from("<III", data, ao)
                vtype = data[ao + 15]
                vdata = _u32(data, ao + 16)
                key = strings[aname] if aname < len(strings) else f"?{aname}"
                attrs[key] = _attr_value(strings, araw, vtype, vdata)
            tag = strings[name] if name < len(strings) else f"?{name}"
            events.append({"tag": tag, "attrs": attrs,
                           "depth": len(stack),
                           "parent": stack[-1] if stack else None})
            stack.append(tag)
        elif ctype == 0x0103:  # end element
            if stack:
                stack.pop()
        off += csize
    return events


def manifest_from_axml(data: bytes) -> dict:
    events = parse_axml(data)
    man: dict = {"package_id": "", "version_name": "", "version_code": None,
                 "min_sdk": None, "target_sdk": None, "permissions": [],
                 "components": [], "meta_data": [], "deeplinks": [],
                 "app_label": ""}
    current_filter: dict | None = None
    for ev in events:
        tag, at = ev["tag"], ev["attrs"]
        if tag == "manifest":
            man["package_id"] = str(at.get("package", ""))
            man["version_name"] = str(at.get("versionName", ""))
            vc = at.get("versionCode")
            man["version_code"] = vc if isinstance(vc, int) else None
        elif tag == "uses-sdk":
            man["min_sdk"] = at.get("minSdkVersion")
            man["target_sdk"] = at.get("targetSdkVersion")
        elif tag in ("uses-permission", "uses-permission-sdk-23"):
            n = at.get("name")
            if n and n not in man["permissions"]:
                man["permissions"].append(str(n))
        elif tag in ("activity", "activity-alias", "service", "receiver", "provider"):
            comp = {"kind": tag, "name": str(at.get("name", ""))}
            if tag == "provider" and at.get("authorities"):
                comp["authorities"] = str(at["authorities"])
            if at.get("exported") is not None:
                comp["exported"] = at["exported"]
            man["components"].append(comp)
            current_filter = None
        elif tag == "meta-data":
            if at.get("name"):
                man["meta_data"].append(str(at["name"]))
        elif tag == "intent-filter":
            current_filter = {"schemes": [], "hosts": [], "actions": []}
            man["deeplinks"].append(current_filter)
        elif tag == "data" and current_filter is not None:
            if at.get("scheme"):
                current_filter["schemes"].append(str(at["scheme"]))
            if at.get("host"):
                current_filter["hosts"].append(str(at["host"]))
        elif tag == "action" and current_filter is not None:
            if at.get("name"):
                current_filter["actions"].append(str(at["name"]))
    man["deeplinks"] = [d for d in man["deeplinks"] if d["schemes"] or d["hosts"]]
    man["permissions"].sort()
    return man


# ------------------------------------------------------------------- DEX

def _uleb128(b: bytes, pos: int) -> tuple[int, int]:
    result, shift = 0, 0
    while True:
        byte = b[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, pos
        shift += 7


def dex_strings(data: bytes) -> list[str]:
    """All strings from one DEX file's string_ids table (MUTF-8)."""
    if len(data) < 0x70 or not data.startswith(b"dex\n"):
        raise ValueError("not a DEX file")
    size, off = _u32(data, 0x38), _u32(data, 0x3C)
    out: list[str] = []
    for i in range(size):
        pos = _u32(data, off + i * 4)
        _ln, pos = _uleb128(data, pos)
        end = data.index(b"\x00", pos)
        out.append(data[pos:end].decode("utf-8", errors="replace"))
    return out


# ------------------------------------------------------------- extraction

def _clean_url(u: str) -> str:
    return u.rstrip(".,;:!?'\"")


def scan_text_for_endpoints(texts: list[str], source: str) -> tuple[list[dict], set[str]]:
    endpoints: dict[tuple[str, str], dict] = {}
    hosts: set[str] = set()
    for t in texts:
        for m in URL_RE.finditer(t or ""):
            url = _clean_url(m.group(0))
            try:
                p = urllib.parse.urlsplit(url)
            except ValueError:
                continue
            if not p.hostname:
                continue
            host = p.hostname.lower()
            hosts.add(host)
            path = p.path or "/"
            key = (host, path)
            if key not in endpoints:
                endpoints[key] = {"url": f"{p.scheme}://{host}{path}",
                                  "host": host, "path": path, "source": source}
    return sorted(endpoints.values(), key=lambda e: (e["host"], e["path"])), hosts


def _match_signatures(sigs: list[dict], hosts: set[str], corpus_lower: str,
                      entries: list[str]) -> list[dict]:
    found: list[dict] = []
    for sig in sigs:
        evidence: list[str] = []
        for pat in sig.get("hosts", []):
            for h in hosts:
                if host_matches(h, pat):
                    evidence.append(f"host:{h}")
        for marker in sig.get("string_markers", []):
            if marker.lower() in corpus_lower:
                evidence.append(f"string:{marker}")
        for cf in sig.get("config_files", []):
            if any(e == cf or e.endswith("/" + cf) for e in entries):
                evidence.append(f"config:{cf}")
        if evidence:
            found.append({"id": sig["id"], "category": sig.get("category", ""),
                          "evidence": sorted(set(evidence))})
    return sorted(found, key=lambda f: f["id"])


def _provider_configs(zf: zipfile.ZipFile, entries: list[str]) -> list[dict]:
    """Embedded provider config files: ids + key NAMES only, never values."""
    out: list[dict] = []
    for name in entries:
        base = name.rsplit("/", 1)[-1]
        if base not in ("google-services.json", "agconnect-services.json"):
            continue
        try:
            doc = json.loads(zf.read(name).decode("utf-8", errors="replace"))
        except Exception:
            out.append({"file": name, "provider": "google-firebase",
                        "parse": "failed"})
            continue
        rec: dict = {"file": name, "provider": "google-firebase"}
        info = doc.get("project_info") or {}
        if info.get("project_id"):
            rec["project_id"] = info["project_id"]  # public app identifier
        key_names: set[str] = set()

        def walk(o: object) -> None:
            if isinstance(o, dict):
                for k, v in o.items():
                    key_names.add(k)
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(doc)
        rec["keys_present"] = sorted(key_names)  # names only — values withheld
        out.append(rec)
    return out


def extract_apk(path: str | Path, signatures: dict | None = None,
                include_corpus: bool = True) -> dict:
    """Static extraction from the artifact as published. Raises on a
    non-APK input; absence handling belongs to acquire/no-artifact."""
    sigs = signatures or load_signatures()
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        entries = zf.namelist()
        if "AndroidManifest.xml" not in entries:
            raise ValueError("no AndroidManifest.xml — not an APK")
        manifest = manifest_from_axml(zf.read("AndroidManifest.xml"))
        corpus: list[str] = []
        dex_files = [e for e in entries
                     if re.fullmatch(r"classes\d*\.dex", e.rsplit("/", 1)[-1])]
        for df in sorted(dex_files):
            try:
                corpus.extend(dex_strings(zf.read(df)))
            except ValueError:
                continue
        text_entries = [e for e in entries if e.lower().endswith(
            (".json", ".xml", ".properties", ".txt", ".html", ".js", ".cfg"))]
        text_blobs: list[str] = []
        for e in text_entries:
            if e == "AndroidManifest.xml" or zf.getinfo(e).file_size > 2_000_000:
                continue
            if e.rsplit("/", 1)[-1] in ("google-services.json",
                                        "agconnect-services.json"):
                continue  # provider configs: ids + key NAMES only, never raw
            try:
                text_blobs.append(zf.read(e).decode("utf-8", errors="replace"))
            except Exception:
                continue
        corpus.extend(text_blobs)
        provider_configs = _provider_configs(zf, entries)
        assets = sorted(e for e in entries if e.startswith("assets/"))
        native_libs = sorted(e for e in entries
                             if e.startswith("lib/") and e.endswith(".so"))
    corpus_lower = "\n".join(corpus).lower()
    endpoints, hosts = scan_text_for_endpoints(corpus, "dex/assets")
    for d in manifest["deeplinks"]:
        for h in d["hosts"]:
            hosts.add(h.lower())
    for sig_list in (sigs.get("providers", []), sigs.get("trackers", [])):
        for sig in sig_list:
            for pat in sig.get("hosts", []):
                base = pat[2:] if pat.startswith("*.") else pat
                if base in corpus_lower:
                    hosts.add(base)
    providers = _match_signatures(sigs.get("providers", []), hosts,
                                  corpus_lower, entries)
    trackers = _match_signatures(sigs.get("trackers", []), hosts,
                                 corpus_lower, entries)
    api_routes = sorted({e["path"] for e in endpoints
                         if API_PATH_RE.match(e["path"])})
    feature_signals: list[dict] = []
    for fs in sigs.get("feature_signals", []):
        hits = [p for p in fs["any_of"]
                if p.lower() in corpus_lower
                or any(p.lower() in a.lower() for a in assets + native_libs)]
        if hits:
            feature_signals.append({"id": fs["id"], "matched": hits})
    ext: dict = {
        "schema": EXTRACTION_SCHEMA,
        "file": {"name": Path(path).name, "size_bytes": len(raw),
                 "sha256": sha},
        "manifest": manifest,
        "entries_count": len(entries),
        "dex_files": sorted(dex_files),
        "assets": assets,
        "native_libs": native_libs,
        "hosts": sorted(hosts),
        "endpoints": endpoints,
        "api_routes": api_routes,
        "providers": providers,
        "provider_configs": provider_configs,
        "trackers": trackers,
        "feature_signals": feature_signals,
    }
    ext["classification"] = classify(ext)
    if include_corpus:
        ext["corpus"] = sorted(set(corpus))
    return ext


def classify(ext: dict) -> dict:
    """Deterministic class / provider / route tags for one extraction."""
    providers = sorted(p["id"] for p in ext.get("providers", []))
    trackers = sorted(t["id"] for t in ext.get("trackers", []))
    signals = {s["id"] for s in ext.get("feature_signals", [])}
    ai = {p["id"] for p in ext.get("providers", [])
          if (p.get("category") or "").startswith("ai")}
    classes: list[str] = []
    if ai:
        classes.append("ai-client")
    if signals & {"llama.cpp", "gguf-model", "onnx-runtime", "tflite",
                  "mediapipe", "whisper"}:
        classes.append("local-inference")
    external = [h for h in ext.get("hosts", []) if not is_local_host(h)]
    if external:
        classes.append("network-client")
    if trackers:
        classes.append("tracker-bearing")
    if "webview" in signals:
        classes.append("webview-shell")
    if not classes:
        classes.append("unclassified")
    deeplinks = sorted({f"{s}://{h}" for d in ext["manifest"]["deeplinks"]
                        for s in d["schemes"] for h in (d["hosts"] or [""])})
    tags = sorted(
        [f"class:{c}" for c in classes]
        + [f"provider:{p}" for p in providers]
        + [f"tracker:{t}" for t in trackers]
        + [f"signal:{s}" for s in sorted(signals)]
        + [f"permission:{p.rsplit('.', 1)[-1].lower()}"
           for p in ext["manifest"]["permissions"]])
    return {"classes": sorted(classes), "providers": providers,
            "trackers": trackers,
            "routes": {"api": ext.get("api_routes", []),
                       "deeplinks": deeplinks},
            "tags": tags}


# ---------------------------------------------------------- claims / xref

TEXT_EXTS = {".py", ".kt", ".kts", ".java", ".md", ".json", ".xml", ".gradle",
             ".txt", ".yml", ".yaml", ".toml", ".properties", ".js", ".ts",
             ".dart", ".rb", ".go", ".rs", ".html"}


def scan_repo_tree(root: str | Path, signatures: dict | None = None) -> dict:
    """Draft claims from the paired source tree: the repo side of the
    cross-validation (what the source itself says it does)."""
    sigs = signatures or load_signatures()
    root = Path(root)
    texts: list[str] = []
    package_id = ""
    permissions: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "node_modules", "build", ".gradle")]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix.lower() not in TEXT_EXTS or p.stat().st_size > 2_000_000:
                continue
            try:
                t = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            texts.append(t)
            if fn == "AndroidManifest.xml":
                permissions.update(re.findall(
                    r"uses-permission[^>]*android:name=\"([^\"]+)\"", t))
                m = re.search(r"package=\"([^\"]+)\"", t)
                if m:
                    package_id = m.group(1)
            if fn in ("build.gradle", "build.gradle.kts"):
                m = re.search(r"applicationId\s*=?\s*\"([^\"]+)\"", t)
                if m:
                    package_id = m.group(1)
    corpus = "\n".join(texts)
    endpoints, hosts = scan_text_for_endpoints(texts, "repo")
    providers = _match_signatures(sigs.get("providers", []), hosts,
                                  corpus.lower(), [])
    return {"schema": CLAIMS_SCHEMA, "target_id": root.name,
            "package_id": package_id,
            "hosts": sorted(hosts),
            "endpoints": sorted({e["url"] for e in endpoints}),
            "providers": sorted(p["id"] for p in providers),
            "permissions": sorted(permissions),
            "features": [], "claims_to_check": [],
            "source": "repo-scan"}


def check_claim(ext: dict, claim: str) -> dict:
    """One freeform source claim (findings-form 'claims to check') ->
    a deterministic outcome where the artifact can decide it, else
    an honest 'unchecked'."""
    low = claim.lower()
    external_hosts = [h for h in ext.get("hosts", []) if not is_local_host(h)]
    has_internet = any(p.endswith(".INTERNET")
                       for p in ext["manifest"]["permissions"])
    if any(k in low for k in ("pure local", "100% on your hardware",
                              "on your hardware", "no network", "offline",
                              "local-only", "local only", "never leaves")):
        if external_hosts or ext.get("endpoints"):
            return {"claim": claim, "outcome": "contradicted",
                    "evidence": f"artifact reaches external hosts "
                                f"{external_hosts[:5]}"
                                + ("; INTERNET permission declared"
                                   if has_internet else "")}
        if has_internet:
            return {"claim": claim, "outcome": "not-found",
                    "evidence": "no external endpoints extracted, but "
                                "INTERNET permission is declared"}
        return {"claim": claim, "outcome": "supported",
                "evidence": "no external hosts/endpoints and no INTERNET "
                            "permission in the artifact"}
    signals = {s["id"]: s for s in ext.get("feature_signals", [])}
    if "llama" in low:
        hit = signals.get("llama.cpp") or signals.get("gguf-model")
        return {"claim": claim,
                "outcome": "supported" if hit else "not-found",
                "evidence": (f"signal {hit['id']} matched {hit['matched']}"
                             if hit else "no llama.cpp/GGUF signal in artifact")}
    if "gemma" in low:
        hit = signals.get("gemma")
        return {"claim": claim,
                "outcome": "supported" if hit else "not-found",
                "evidence": ("gemma strings/assets present" if hit
                             else "no gemma reference in artifact")}
    for p in ext.get("providers", []):
        if p["id"] in low or p["id"].replace("-", " ") in low:
            return {"claim": claim, "outcome": "supported",
                    "evidence": f"provider {p['id']} detected "
                                f"({'; '.join(p['evidence'][:3])})"}
    known = {s["id"] for s in load_signatures().get("providers", [])}
    for pid in known:
        if pid in low:
            return {"claim": claim, "outcome": "not-found",
                    "evidence": f"provider {pid} not detected in artifact"}
    if "tracker" in low or "analytics" in low:
        tr = [t["id"] for t in ext.get("trackers", [])]
        return {"claim": claim,
                "outcome": "supported" if tr else "not-found",
                "evidence": f"trackers in artifact: {tr or 'none'}"}
    return {"claim": claim, "outcome": "unchecked",
            "evidence": "no deterministic artifact check for this claim; "
                        "manual review required"}


def _endpoint_key(url: str) -> tuple[str, str]:
    p = urllib.parse.urlsplit(url if "://" in url else "https://" + url)
    return ((p.hostname or "").lower(), p.path or "/")


def cross_validate(ext: dict, claims: dict) -> dict:
    """Diff both directions. claims = apk-claims/v1 (scan_repo_tree output
    or a hand-written brief claims file)."""
    repo_to_apk: list[str] = []
    apk_to_repo: list[str] = []
    man = ext["manifest"]
    if claims.get("package_id") and man["package_id"] \
            and claims["package_id"] != man["package_id"]:
        repo_to_apk.append(f"package_id: source claims "
                           f"{claims['package_id']}, artifact is "
                           f"{man['package_id']}")
    ext_hosts = set(ext.get("hosts", []))
    for h in sorted(set(claims.get("hosts", [])) - ext_hosts):
        repo_to_apk.append(f"host: {h} claimed in source, absent in artifact")
    for h in sorted(ext_hosts - set(claims.get("hosts", []))):
        apk_to_repo.append(f"host: {h} present in artifact, not claimed in source")
    ext_eps = {_endpoint_key(e["url"]) for e in ext.get("endpoints", [])}
    claim_eps = {_endpoint_key(u) for u in claims.get("endpoints", [])}
    for h, p in sorted(claim_eps - ext_eps):
        repo_to_apk.append(f"endpoint: {h}{p} claimed in source, absent in artifact")
    for h, p in sorted(ext_eps - claim_eps):
        apk_to_repo.append(f"endpoint: {h}{p} present in artifact, not claimed in source")
    ext_prov = {p["id"] for p in ext.get("providers", [])}
    for pid in sorted(set(claims.get("providers", [])) - ext_prov):
        repo_to_apk.append(f"provider: {pid} claimed in source, absent in artifact")
    for pid in sorted(ext_prov - set(claims.get("providers", []))):
        apk_to_repo.append(f"provider: {pid} present in artifact, not claimed in source")
    for perm in sorted(set(claims.get("permissions", [])) - set(man["permissions"])):
        repo_to_apk.append(f"permission: {perm} claimed in source, absent in artifact")
    for perm in sorted(set(man["permissions"]) - set(claims.get("permissions", []))):
        if claims.get("permissions"):
            apk_to_repo.append(f"permission: {perm} declared in artifact, "
                               f"not claimed in source")
    corpus = ext.get("corpus")
    searchable: str | None = None
    if corpus is not None:
        searchable = "\n".join(corpus).lower()
    else:  # corpus stripped: fall back to the structured surface
        searchable = "\n".join(
            ext.get("hosts", []) + ext.get("assets", [])
            + ext.get("native_libs", [])
            + [e["url"] for e in ext.get("endpoints", [])]).lower()
    claimed_feats: set[str] = set()
    for feat in claims.get("features", []):
        if isinstance(feat, str):
            name, pats = feat, [feat]
        else:
            name, pats = feat.get("name", "?"), feat.get("any_of", [])
        claimed_feats.add(name.lower())
        if not any(p.lower() in searchable for p in pats):
            repo_to_apk.append(f"feature: {name} claimed in source, "
                               f"no evidence in artifact")
    for t in ext.get("trackers", []):
        if t["id"] not in {str(x).lower() for x in claims.get("trackers", [])}:
            apk_to_repo.append(f"tracker: {t['id']} present in artifact, "
                               f"not claimed in source")
    for s in ext.get("feature_signals", []):
        if s["id"] not in claimed_feats and s["id"] not in claims.get("providers", []):
            apk_to_repo.append(f"signal: {s['id']} present in artifact "
                               f"({', '.join(s['matched'][:3])}), "
                               f"not claimed in source")
    checked = [check_claim(ext, c) for c in claims.get("claims_to_check", [])]
    divergences = repo_to_apk + apk_to_repo
    return {"divergences_repo_to_apk": repo_to_apk,
            "divergences_apk_to_repo": apk_to_repo,
            "claims_checked": checked,
            "verdict": "match" if not divergences else "divergences-found"}


# --------------------------------------------------------------- findings

def build_findings_record(*, target_id: str, xref_issue: str,
                          submitter: str, evidence: str = "reproduced",
                          extraction: dict | None = None,
                          xref: dict | None = None,
                          artifact_source: str = "none-known",
                          provenance: dict | None = None,
                          sources_checked: list[str] | None = None) -> dict:
    """The apk-xref/v1 findings record — keys exactly as the findings
    form / intake parser carry them; extension data rides alongside."""
    notes_lines: list[str] = []
    if extraction is not None:
        f = extraction["file"]
        notes_lines.append(f"artifact sha256: {f['sha256']} "
                           f"({f['size_bytes']} bytes, {f['name']})")
        man = extraction["manifest"]
        version = (f"{man['version_name']} (build {man['version_code']})"
                   if man["version_code"] is not None
                   else man["version_name"] or "unknown")
        record: dict = {
            "schema": RECORD_SCHEMA, "kind": "findings",
            "target_id": target_id, "xref_issue": xref_issue,
            "package_id": man["package_id"],
            "artifact_source": artifact_source,
            "artifact_version": version,
            "manifest_permissions": man["permissions"] or ["none declared"],
            "endpoints_observed":
                [e["url"] for e in extraction["endpoints"]] or ["none observed"],
            "claims_checked":
                [f"{c['claim']} — {c['outcome']}: {c['evidence']}"
                 for c in (xref or {}).get("claims_checked", [])]
                or ["none supplied"],
            "divergences_repo_to_apk":
                (xref or {}).get("divergences_repo_to_apk") or ["none found"],
            "divergences_apk_to_repo":
                (xref or {}).get("divergences_apk_to_repo") or ["none found"],
            "verdict": (xref or {}).get("verdict", "match"),
            "evidence_expectation": evidence,
            "submitter": submitter,
        }
        record["classification"] = extraction["classification"]
        record["providers"] = extraction["providers"]
        record["trackers"] = extraction["trackers"]
        record["provider_configs"] = extraction["provider_configs"]
        record["components"] = man["components"]
    else:
        record = {
            "schema": RECORD_SCHEMA, "kind": "findings",
            "target_id": target_id, "xref_issue": xref_issue,
            "package_id": "",
            "artifact_source": artifact_source,
            "artifact_version": "",
            "manifest_permissions": ["none (no artifact)"],
            "endpoints_observed": ["none (no artifact)"],
            "claims_checked": ["not evaluable — no artifact published"],
            "divergences_repo_to_apk": ["not evaluable — no artifact published"],
            "divergences_apk_to_repo": ["not evaluable — no artifact published"],
            "verdict": "no-artifact-found",
            "evidence_expectation": evidence,
            "submitter": submitter,
        }
        notes_lines.append("no-artifact-found — sources checked: "
                           + ", ".join(sources_checked or []))
    if provenance:
        notes_lines.append("provenance: " + json.dumps(provenance, sort_keys=True))
    record["notes"] = "\n".join(notes_lines)
    return record


_FINDING_HEADINGS = [
    ("Target ID", "target_id"), ("Cross-reference issue", "xref_issue"),
    ("Package ID", "package_id"), ("Artifact source", "artifact_source"),
    ("Artifact version + build", "artifact_version"),
    ("Manifest permissions", "manifest_permissions"),
    ("Endpoints actually observed", "endpoints_observed"),
    ("Source claims checked", "claims_checked"),
    ("Divergences — repo to APK", "divergences_repo_to_apk"),
    ("Divergences — APK to repo", "divergences_apk_to_repo"),
    ("Verdict", "verdict"), ("Evidence expectation met", "evidence_expectation"),
    ("Submitter Role{Moniker}", "submitter"), ("Notes", "notes"),
]


def render_findings_markdown(record: dict) -> str:
    """Markdown in the findings-form shape — the headings are the form's
    labels verbatim, so scripts/apk_xref/apk_xref_intake.py (PR #2140)
    re-parses this report into the same apk-xref/v1 record."""
    out: list[str] = []
    for heading, key in _FINDING_HEADINGS:
        out.append(f"### {heading}")
        out.append("")
        val = record.get(key, "")
        if isinstance(val, list):
            out.extend(str(v) for v in val) if val else out.append("none found")
        else:
            out.append(str(val) if str(val) else "none")
        out.append("")
    return "\n".join(out)


# ------------------------------------------------------------- acquisition

def _default_fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "apk-xref-toolkit/1 (termux-monorepo foundry)"})
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok and urllib.parse.urlsplit(url).hostname == "api.github.com":
        req.add_header("Authorization", f"Bearer {tok}")  # env only, never logged
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _fetch_json(url: str, fetch) -> object:
    return json.loads(fetch(url).decode("utf-8", errors="replace"))


def _pick_apk_asset(releases: list[dict]) -> tuple[dict, dict] | None:
    for rel in releases:
        for asset in rel.get("assets", []):
            if asset.get("name", "").lower().endswith(".apk"):
                return rel, asset
    return None


def github_release_apk(repo: str, fetch=_default_fetch) -> dict | None:
    """Latest GitHub release carrying an .apk asset, or None."""
    rels = _fetch_json(
        f"https://api.github.com/repos/{repo}/releases?per_page=30", fetch)
    if not isinstance(rels, list):
        return None
    picked = _pick_apk_asset(rels)
    if not picked:
        return None
    rel, asset = picked
    return {"source": "github-releases", "repo": repo,
            "version": rel.get("tag_name", ""), "release_name": rel.get("name", ""),
            "published_at": rel.get("published_at", ""),
            "asset_name": asset.get("name", ""),
            "download_url": asset.get("browser_download_url", "")}


def gitea_release_apk(base_url: str, repo: str, fetch=_default_fetch) -> dict | None:
    base = base_url.rstrip("/")
    rels = _fetch_json(f"{base}/api/v1/repos/{repo}/releases?limit=30", fetch)
    if not isinstance(rels, list):
        return None
    picked = _pick_apk_asset(rels)
    if not picked:
        return None
    rel, asset = picked
    return {"source": "gitea-releases", "repo": repo, "forge": base,
            "version": rel.get("tag_name", ""), "release_name": rel.get("name", ""),
            "published_at": rel.get("published_at", ""),
            "asset_name": asset.get("name", ""),
            "download_url": asset.get("browser_download_url", "")}


def fdroid_apk(package_id: str, fetch=_default_fetch) -> dict | None:
    """F-Droid metadata API (no Play scraping, ever). Highest build wins."""
    try:
        doc = _fetch_json(f"https://f-droid.org/api/v1/packages/{package_id}", fetch)
    except Exception:
        return None
    pkgs = (doc or {}).get("packages") or []
    if not pkgs:
        return None
    best = max(pkgs, key=lambda p: p.get("versionCode", 0))
    # The metadata API does not always carry apkName; the repo layout is
    # deterministic: <package_id>_<versionCode>.apk under /repo/.
    apk_name = best.get("apkName") or f"{package_id}_{best.get('versionCode')}.apk"
    prov = {"source": "f-droid", "package_id": package_id,
            "version": best.get("versionName", ""),
            "build": best.get("versionCode"),
            "asset_name": apk_name,
            "download_url": f"https://f-droid.org/repo/{apk_name}"}
    if best.get("hash"):
        prov["fdroid_hash"] = best["hash"]
        prov["fdroid_hash_type"] = best.get("hashType", "")
    return prov


def download_artifact(provenance: dict, out_dir: str | Path,
                      fetch=_default_fetch) -> dict:
    """Download + hash. Play URLs are refused outright (no Play scraping)."""
    url = provenance["download_url"]
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    if host == "play.google.com":
        raise ValueError("refused: Google Play is not an acquisition source")
    data = fetch(url)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / (provenance.get("asset_name") or "artifact.apk")
    dest.write_bytes(data)
    return {**provenance, "path": str(dest), "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def acquire(spec: dict, out_dir: str | Path, fetch=_default_fetch) -> dict:
    """Try the spec's sources in order. spec keys: source(s), repo,
    package_id, gitea_url. Returns acquired provenance (+sha256/path)
    or a no-artifact-found evidence record listing what was checked."""
    wanted = spec.get("sources") or [spec.get("source", "")]
    checked: list[str] = []
    for source in wanted:
        try:
            prov: dict | None = None
            if source == "github-releases" and spec.get("repo"):
                prov = github_release_apk(spec["repo"], fetch)
            elif source == "gitea-releases" and spec.get("repo"):
                prov = gitea_release_apk(spec.get("gitea_url", ""), spec["repo"], fetch)
            elif source == "f-droid" and spec.get("package_id"):
                prov = fdroid_apk(spec["package_id"], fetch)
            elif source == "direct-apk" and spec.get("url"):
                prov = {"source": "direct-apk",
                        "asset_name": spec["url"].rsplit("/", 1)[-1],
                        "download_url": spec["url"], "version": ""}
            else:
                checked.append(f"{source}: skipped (missing repo/package_id/url)")
                continue
            if prov is None:
                checked.append(f"{source}: no APK asset published")
                continue
            got = download_artifact(prov, out_dir, fetch)
            got["status"] = "acquired"
            got["sources_checked"] = checked + [f"{source}: APK acquired"]
            return got
            checked.append(f"{source}: checked")
        except Exception as e:  # evidence, not a crash — the brief demands it
            checked.append(f"{source}: error {type(e).__name__}: {e}")
    return {"status": "no-artifact-found", "sources_checked": checked}


# -------------------------------------------------------------------- CLI

def _dump(obj: object, out: str | None) -> None:
    text = json.dumps(obj, indent=1, sort_keys=True)
    if out:
        Path(out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="apk_xref")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("acquire")
    a.add_argument("--source", action="append", dest="sources",
                   help="repeatable: github-releases|gitea-releases|f-droid|direct-apk")
    a.add_argument("--repo", default="")
    a.add_argument("--package-id", default="")
    a.add_argument("--gitea-url", default="")
    a.add_argument("--url", default="")
    a.add_argument("--out", required=True, help="directory for the artifact")

    e = sub.add_parser("extract")
    e.add_argument("apk")
    e.add_argument("--out")
    e.add_argument("--no-corpus", action="store_true")

    s = sub.add_parser("scan-repo")
    s.add_argument("root")
    s.add_argument("--out")

    x = sub.add_parser("xref")
    x.add_argument("--extraction", required=True)
    x.add_argument("--claims", required=True)
    x.add_argument("--target-id", required=True)
    x.add_argument("--xref-issue", required=True)
    x.add_argument("--submitter", required=True)
    x.add_argument("--evidence", default="reproduced")
    x.add_argument("--artifact-source", default="none-known")
    x.add_argument("--claims-to-check", help="file, one claim per line")
    x.add_argument("--out")
    x.add_argument("--markdown")

    n = sub.add_parser("no-artifact")
    n.add_argument("--target-id", required=True)
    n.add_argument("--xref-issue", required=True)
    n.add_argument("--submitter", required=True)
    n.add_argument("--evidence", default="observed")
    n.add_argument("--artifact-source", default="none-known")
    n.add_argument("--sources-checked", nargs="+", default=[])
    n.add_argument("--out")
    n.add_argument("--markdown")

    args = ap.parse_args(argv)
    if args.cmd == "acquire":
        spec = {"sources": args.sources or [], "repo": args.repo,
                "package_id": args.package_id, "gitea_url": args.gitea_url,
                "url": args.url}
        result = acquire(spec, args.out)
        _dump(result, None)
        return 0 if result["status"] == "acquired" else 3
    if args.cmd == "extract":
        _dump(extract_apk(args.apk, include_corpus=not args.no_corpus), args.out)
        return 0
    if args.cmd == "scan-repo":
        _dump(scan_repo_tree(args.root), args.out)
        return 0
    if args.cmd == "xref":
        ext = json.loads(Path(args.extraction).read_text(encoding="utf-8"))
        claims = json.loads(Path(args.claims).read_text(encoding="utf-8"))
        if args.claims_to_check:
            claims["claims_to_check"] = [
                ln.strip() for ln in Path(args.claims_to_check)
                .read_text(encoding="utf-8").splitlines() if ln.strip()]
        result = cross_validate(ext, claims)
        prov = None
        if ext.get("provenance"):
            prov = ext["provenance"]
        record = build_findings_record(
            target_id=args.target_id, xref_issue=args.xref_issue,
            submitter=args.submitter, evidence=args.evidence,
            extraction=ext, xref=result,
            artifact_source=args.artifact_source, provenance=prov)
        _dump(record, args.out)
        if args.markdown:
            Path(args.markdown).write_text(
                render_findings_markdown(record) + "\n", encoding="utf-8")
        return 0
    if args.cmd == "no-artifact":
        record = build_findings_record(
            target_id=args.target_id, xref_issue=args.xref_issue,
            submitter=args.submitter, evidence=args.evidence,
            artifact_source=args.artifact_source,
            sources_checked=args.sources_checked)
        _dump(record, args.out)
        if args.markdown:
            Path(args.markdown).write_text(
                render_findings_markdown(record) + "\n", encoding="utf-8")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
