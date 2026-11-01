"""[MUSEai]@{role:{apk-release}} :: lane-shape guards (∅ SDK needed)."""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]

def test_app_sources_exist_and_agree():
    app = ROOT / "apps" / "fleet-apk"
    manifest = (app / "AndroidManifest.xml").read_text()
    version = (app / "VERSION").read_text().strip()
    assert 'package="com.timerloggedout.fleet"' in manifest
    assert re.fullmatch(r"\d+\.\d+\.\d+", version)
    assert (app / "src/com/timerloggedout/fleet/MainActivity.java").exists()

def test_workflow_triggers_and_signing_names_only():
    wf = (ROOT / ".github/workflows/apk-release.yml").read_text()
    assert "apk-v*" in wf and "workflow_dispatch" in wf
    for name in ("ANDROID_KEYSTORE_BASE64", "ANDROID_KEYSTORE_PASSWORD", "ANDROID_KEY_ALIAS", "ANDROID_KEY_PASSWORD"):
        assert name in wf
    assert "secrets." not in wf.replace("secrets.ANDROID_", "")  # only the 4 named secrets referenced

def test_build_script_pipeline_order():
    s = (ROOT / "scripts/apk/build_apk.sh").read_text()
    order = [s.index(t) for t in ("aapt2", "javac", "d8", "zipalign", "apksigner\" sign", "apksigner\" verify", "sha256sum")]
    assert order == sorted(order)
    assert "gradlew" not in s and "gradle " not in s  # SDK-direct only; word may appear in comments
