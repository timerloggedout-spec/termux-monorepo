"""Owner-records page contract (D1-D5): envelope render, D4 discovery
rules (no primary nav, no sitemap loc - Admin + Tracking cross-links
only), and the versioning registry entries."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/help-wanted-dashboard"
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
        m = re.search(r'<nav aria-label="Primary">([\s\S]*?)</nav>',
                      p.read_text())
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
