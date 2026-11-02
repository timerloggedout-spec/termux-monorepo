"""Nested-family page contract (owner standard 2026-11-01): tree +
charts from the nested-family/v1 feed only, dispatch links to run
records, stamp + STALE, registry/sitemap/cross-link presence.
PR-1 state: the page carries no Primary nav yet - the chrome PR adds
its anchor to every shell nav and updates the nav ratchet in one go."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/help-wanted-dashboard"
PAGE = APP / "family.html"
FEED = APP / "data/nested-family-feed.json"


def test_feed_shape_on_master():
    feed = json.loads(FEED.read_text())
    assert feed["schema"] == "nested-family/v1"
    assert feed["generated_at"]
    for p in feed["providers"]:
        for m in p["models"]:
            assert "tasks" in m and "roles" in m
            for t in m["tasks"]:
                assert "outcome" in t and "source_ref" in t


def test_page_render_and_dispatch_links():
    html = PAGE.read_text()
    assert "nested-family-feed.json" in html
    for marker in ("providerSection", "modelCard", "taskRow",
                   "actions/runs/", "blob/master/", "CK.bars",
                   "CK.stampState", 'id="chart-providers"',
                   'id="chart-outcomes"', "NOT_ESTABLISHED"):
        assert marker in html
    assert 'aria-label="Primary"' in html
    assert 'family.html" aria-current="page">Family' in html


def test_registry_sitemap_crosslinks():
    manifest = json.loads((APP / "version-manifest.json").read_text())
    files = [p["file"] for p in manifest["pages"]]
    assert "family.html" in files and files == sorted(files)
    assert '"file":"family.html"' in (APP / "versioning.js").read_text().replace(" ", "")
    assert "https://timerloggedout-spec.github.io/tribute/family.html" in (APP / "sitemap.xml").read_text()
    assert "./family.html" in (APP / "tracking.html").read_text()
    assert "./family.html" in (APP / "admin.html").read_text()
