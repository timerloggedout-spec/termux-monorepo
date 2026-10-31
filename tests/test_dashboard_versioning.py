"""Regression contracts for stable page identities and comparable dashboard builds."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
BUILDER = ROOT / "scripts" / "build_dashboard_manifest.py"


def test_every_dashboard_html_has_stable_identity_in_build_registry():
    pages = sorted(p.name for p in APP.glob("*.html"))
    manifest = json.loads((APP / "version-manifest.json").read_text())
    ids = [p["id"] for p in manifest["pages"]]
    files = [p["file"] for p in manifest["pages"]]
    assert set(pages).issubset(set(files))
    assert len(ids) == len(set(ids)), "page unique IDs must be unique"
    assert "versioning.html" in files
    assert "lanes-and-scopes.html" in files


def test_versioning_header_is_injected_for_all_pages_by_build_step(tmp_path):
    (tmp_path / "index.html").write_text("<html><head><title>Test</title></head><body>ok</body></html>")
    (tmp_path / "versioning.html").write_text("<html><head></head><body>compare</body></html>")
    (tmp_path / "versioning.js").write_text("/* test */")
    subprocess.run([
        sys.executable, str(BUILDER), "--root", str(tmp_path), "--channel", "preview",
        "--source-ref", "refs/pull/1/head", "--source-sha", "0123456789abcdef",
    ], check=True, capture_output=True, text=True)
    for name in ("index.html", "versioning.html"):
        assert 'src="./versioning.js"' in (tmp_path / name).read_text()
    manifest = json.loads((tmp_path / "version-manifest.json").read_text())
    assert manifest["channel"] == "preview"
    assert manifest["version"] == "1.0.0+0123456789ab"
    assert len(manifest["pages"]) == 2
    assert all(len(p["content_sha256"]) == 64 for p in manifest["pages"])


def test_builder_fails_closed_when_page_cannot_be_versioned(tmp_path):
    (tmp_path / "broken.html").write_text("<html><body>no head close</body></html>")
    result = subprocess.run([
        sys.executable, str(BUILDER), "--root", str(tmp_path), "--channel", "preview",
        "--source-ref", "test", "--source-sha", "abc",
    ], capture_output=True, text=True)
    assert result.returncode != 0
