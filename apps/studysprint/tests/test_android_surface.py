"""Tests for the APK surface (android/, issue #4093).

Manifest/package/version coherence, the shell wiring (the WebView
loads the bundled webApp), the SDK-direct build chain, and the CI
workflow shape. The APK itself is built in Actions.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "android"
NS = "{http://schemas.android.com/apk/res/android}"


def test_manifest_package_and_version():
    tree = ET.parse(ANDROID / "AndroidManifest.xml")
    manifest = tree.getroot()
    assert manifest.get("package") == "org.timerloggedout.studysprint"
    version = (ANDROID / "VERSION").read_text().strip()
    assert manifest.get(f"{NS}versionName") == version
    assert manifest.get(f"{NS}versionCode") == "1"
    activity = manifest.find(".//activity")
    assert activity.get(f"{NS}name") == ".MainActivity"


def test_shell_loads_bundled_webapp():
    java = (ANDROID / "src" / "org" / "timerloggedout" /
            "studysprint" / "MainActivity.java").read_text()
    # #4412: the bundle loads from the reserved https origin
    # (WebViewAssetLoader pattern) -- the file:// origin's fetch
    # layer blocked the state fetch in older WebViews (#4283).
    assert ("https://appassets.androidplatform.net"
            "/assets/web/index.html") in java
    assert "appassets.androidplatform.net" in java
    assert "setJavaScriptEnabled(true)" in java
    assert "setDomStorageEnabled(true)" in java
    # the bundle it loads exists in the sibling web surface
    assert (ROOT / "web" / "index.html").exists()


def test_build_chain_complete():
    script = (ANDROID / "build.sh").read_text()
    for step in ("aapt2", "javac", "d8", "zipalign", "apksigner",
                 "build_data.py", "classes.dex"):
        assert step in script, f"build.sh missing {step}"
    assert "studysprint.apk" in script


def test_workflow_builds_and_uploads():
    wf = (ROOT.parent.parent / ".github" / "workflows" /
          "studysprint-apk.yml")
    if not wf.exists():
        # Conditional skip (D1 ruling, monorepo issue #4538): this
        # assertion's subject is the MONOREPO's CI workflow. In the
        # studysprint repo's layout (this app tree at the repo
        # root), that path legitimately does not exist — the ss
        # repo carries its own workflows — so the test skips there
        # instead of failing on an absent subject. Wherever the
        # path exists (the monorepo), every assertion below runs
        # untouched.
        pytest.skip(
            "monorepo workflow path absent in this checkout "
            "layout (studysprint repo) — the assertion binds "
            "where the workflow lives")
    text = wf.read_text()
    assert "build.sh" in text
    assert "upload-artifact" in text
    assert "apksigner verify" in text
    assert "android-34" in text and "34.0.0" in text


def test_file_chooser_wiring_for_ingest():
    java = (ANDROID / "src" / "org" / "timerloggedout" /
            "studysprint" / "MainActivity.java").read_text()
    assert "WebChromeClient" in java
    assert "onShowFileChooser" in java
    assert "onActivityResult" in java
    assert "ValueCallback" in java
    # the bundle it serves carries the ingest inputs it wires up
    html = (ROOT / "web" / "index.html").read_text()
    assert 'id="ingest-camera"' in html


# ------------------------------------------------------ RFP-D1-7 award batch
def test_signing_keystore_is_committed_and_stable():
    ks = ANDROID / "keystore" / "studysprint-dev.keystore"
    assert ks.exists() and ks.stat().st_size > 1000  # #4222
    build = (ANDROID / "build.sh").read_text()
    assert "keystore/studysprint-dev.keystore" in build
    assert "generated per build environment" not in build
    assert "MISSING" in build  # fails loudly instead of diverging


def test_launcher_icon_is_brand_not_stock():
    manifest = (ANDROID / "AndroidManifest.xml").read_text()
    assert 'android:icon="@drawable/ic_launcher"' in manifest
    assert "sym_def_app_icon" not in manifest
    icon = ANDROID / "res" / "drawable" / "ic_launcher.xml"
    assert icon.exists()
    assert "aapt2\" compile --dir res" in (ANDROID / "build.sh").read_text()


def test_apk_evidence_record_in_tree():
    record = (ROOT / "evidence" / "apk" / "README.md").read_text()
    assert "41621272959" in record  # the CI build run (#4221)
    assert "SHA-256" in record
    assert "SMOKE.md" in record  # the device smoke is the record


def test_webview_serves_bundle_state():
    """The device smoke's defect: state.json must be fetchable
    inside the WebView (SMOKE.md, 2026-11-03)."""
    java = (ANDROID / "src" / "org" / "timerloggedout"
            / "studysprint" / "MainActivity.java").read_text()
    assert "shouldInterceptRequest" in java
    assert "Access-Control-Allow-Origin" in java
    assert '"/android_asset/"' in java or "/android_asset/" in java
