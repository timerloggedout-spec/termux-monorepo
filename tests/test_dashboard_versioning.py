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
    assert set(pages) == set(files), "manifest must list every HTML page exactly once"
    assert len(files) == len(set(files)), "manifest must not duplicate page files"
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
    assert manifest["version"] == "1.0.1+0123456789ab"
    assert len(manifest["pages"]) == 2
    assert all(len(p["content_sha256"]) == 64 for p in manifest["pages"])


def test_builder_fails_closed_when_page_cannot_be_versioned(tmp_path):
    (tmp_path / "broken.html").write_text("<html><body>no head close</body></html>")
    result = subprocess.run([
        sys.executable, str(BUILDER), "--root", str(tmp_path), "--channel", "preview",
        "--source-ref", "test", "--source-sha", "abc",
    ], capture_output=True, text=True)
    assert result.returncode != 0

def test_preview_workflow_isolated_and_preserves_existing_site():
    workflow = (ROOT / ".github" / "workflows" / "help-wanted-dashboard-preview.yml").read_text()
    assert "workflow_dispatch:" in workflow
    assert "source_ref:" in workflow and "preview_key:" in workflow
    assert "publish_dir: _preview" in workflow
    assert "destination_dir: previews/${{ inputs.preview_key }}/help-wanted" in workflow
    assert "keep_files: false" in workflow
    assert "force_orphan: true" not in workflow


def test_production_deployment_stamps_the_artifact():
    workflow = (ROOT / ".github" / "workflows" / "help-wanted-dashboard-deploy.yml").read_text()
    assert "scripts/build_dashboard_manifest.py" in workflow
    assert "--channel production" in workflow
    assert "--source-sha" in workflow


def test_builder_rejects_colliding_page_ids(tmp_path):
    (tmp_path / "alpha_beta.html").write_text("<html><head></head><body>a</body></html>")
    (tmp_path / "alpha-beta.html").write_text("<html><head></head><body>b</body></html>")
    result = subprocess.run([
        sys.executable, str(BUILDER), "--root", str(tmp_path), "--channel", "preview",
        "--source-ref", "test", "--source-sha", "abc",
    ], capture_output=True, text=True)
    assert result.returncode != 0
    assert "duplicate page unique IDs" in result.stderr


def test_builder_rejects_empty_registry(tmp_path):
    result = subprocess.run([
        sys.executable, str(BUILDER), "--root", str(tmp_path), "--channel", "preview",
        "--source-ref", "test", "--source-sha", "abc",
    ], capture_output=True, text=True)
    assert result.returncode != 0
    assert "no HTML pages found" in result.stderr


def test_versioning_preview_and_production_share_release_prefix():
    preview = (ROOT / ".github" / "workflows" / "help-wanted-dashboard-preview.yml").read_text()
    production = (ROOT / ".github" / "workflows" / "help-wanted-dashboard-deploy.yml").read_text()
    assert '--version-prefix "1.0.1"' in preview
    assert '--version-prefix "1.0.1"' in production
    assert "scripts/build_dashboard_manifest.py" in production
    assert ".github/workflows/help-wanted-dashboard-preview.yml" in production


def test_fallback_navigation_covers_every_registered_page():
    js = (APP / "versioning.js").read_text()
    manifest = json.loads((APP / "version-manifest.json").read_text())
    for page in manifest["pages"]:
        assert f'"file":"{page["file"]}"' in js, f"fallback navigation missing {page['file']}"


def test_version_comparison_uses_union_of_page_ids_and_pinned_source_shas():
    js = (APP / "versioning.js").read_text()
    assert "currentPages.concat(productionPages)" in js
    assert "REMOVED FROM PREVIEW" in js
    assert "encodeURIComponent(prod.source_sha)" in js
    assert "encodeURIComponent(current.source_sha)" in js
    assert 'current.source_ref || "master"' not in js


def test_builder_preserves_canonical_home_and_comparison_titles(tmp_path):
    (tmp_path / "index.html").write_text("<html><head></head><body>home</body></html>")
    (tmp_path / "versioning.html").write_text("<html><head></head><body>compare</body></html>")
    (tmp_path / "versioning.js").write_text("/* test */")
    subprocess.run([
        sys.executable, str(BUILDER), "--root", str(tmp_path), "--channel", "preview",
        "--source-ref", "test", "--source-sha", "0123456789abcdef",
    ], check=True, capture_output=True, text=True)
    manifest = json.loads((tmp_path / "version-manifest.json").read_text())
    titles = {page["file"]: page["title"] for page in manifest["pages"]}
    assert titles["index.html"] == "Help-Wanted Home"
    assert titles["versioning.html"] == "Version Comparison"
