"""Owner-records page contract (D1-D5): metadata-only rendering, D4
discovery rules, build provenance and the validated envelope explorer."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/tribute-dashboard"
PAGE = APP / "owner-records.html"
ADMIN = APP / "admin.html"
TRACKING = APP / "tracking.html"


def test_page_fetches_envelope_and_renders_classes():
    html = PAGE.read_text()
    assert "ops/owner-records/index.json" in html
    assert "./owner-records.json" in html  # staged copy on the gated project
    for marker in ("body_status", "NOT_ESTABLISHED", "pending the owner key step"):
        assert marker in html


def test_d4_no_primary_nav_no_sitemap():
    html = PAGE.read_text()
    # D4: the page is not part of the primary nav - neither as a carrier
    # (the nav-uniformity ratchet set stays 23) nor as a sitemap entry.
    assert 'aria-label="Primary"' not in html
    assert "owner-records.html" not in (APP / "sitemap.xml").read_text()
    # Not linked from any shell page's primary nav either.
    nav_pages = [p for p in APP.glob("*.html") if p != PAGE]
    for p in nav_pages:
        m = re.search(r'<nav aria-label="Primary">([\\s\\S]*?)</nav>', p.read_text())
        if m:
            assert "owner-records" not in m.group(1), p.name


def test_d4_crosslinks_from_admin_and_tracking_only():
    assert "./owner-records.html" in ADMIN.read_text()
    assert "./owner-records.html" in TRACKING.read_text()
    # The admin credential scan forbids the literal 'authorization' in
    # admin.html - the inventory row must describe the page without it.
    assert "authorization" not in ADMIN.read_text().lower()


def test_versioning_registry_entries():
    manifest = json.loads((APP / "version-manifest.json").read_text())
    files = [p["file"] for p in manifest["pages"]]
    assert "owner-records.html" in files
    assert files == sorted(files)
    vjs = (APP / "versioning.js").read_text()
    assert '"file":"owner-records.html"' in vjs.replace(" ", "")


def test_metadata_explorer_controls_are_accessible():
    html = PAGE.read_text()
    for control in ('id="record-search"', 'id="class-filter"', 'id="state-filter"',
                    'id="clear-filters"', 'id="results-count"'):
        assert control in html
    assert 'role="status" aria-live="polite"' in html
    assert "Search covers L1 metadata only." in html
    assert "No body search" in html


def test_build_identity_uses_manifest_without_adding_primary_navigation():
    html = PAGE.read_text()
    assert 'fetch("./version-manifest.json"' in html
    assert "manifest.source_sha" in html
    assert "URL parameters differ (manifest wins)" in html
    # versioning.js injects the shared primary nav / all-pages discovery;
    # D4 intentionally keeps this page discoverable from Admin + Tracking only.
    assert 'src="./versioning.js"' not in html
    assert "site-nav.js" not in html
    assert 'aria-label="Primary"' not in html


def test_envelope_validation_fails_closed_and_keeps_bodies_out_of_page():
    html = PAGE.read_text()
    for marker in ("validateEnvelope", "FORBIDDEN_BODY_FIELDS", "owner-records/v1",
                   "No unvalidated data was rendered.", "Envelope rejected:"):
        assert marker in html
    # This public projection must not request an age identity or call a
    # browser decryption API. Ciphertext transport remains Vercel-only.
    assert 'type="password"' not in html
    assert "decrypt(" not in html
    assert "fetch(\"ops/owner-records/bodies" not in html


def test_refresh_is_non_overlapping_and_visibility_aware():
    html = PAGE.read_text()
    assert "if (loading || document.visibilityState === \"hidden\") return;" in html
    assert 'document.addEventListener("visibilitychange"' in html
    assert "window.setInterval(loadEnvelope, 60000)" in html
