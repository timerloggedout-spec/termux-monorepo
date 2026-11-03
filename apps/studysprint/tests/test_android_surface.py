"""Tests for the APK surface (android/, issue #4093).

Manifest/package/version coherence, the shell wiring (the WebView
loads the bundled webApp), the SDK-direct build chain, and the CI
workflow shape. The APK itself is built in Actions.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

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
    assert "file:///android_asset/web/index.html" in java
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
    assert wf.exists()
    text = wf.read_text()
    assert "build.sh" in text
    assert "upload-artifact" in text
    assert "apksigner verify" in text
    assert "android-34" in text and "34.0.0" in text
