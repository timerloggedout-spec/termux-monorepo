"""Swarm quota page contract (owner build 2026-11-01 22:45 PT): the
page distinguishes the Swarm (DoE participant population) from the
quota registry, renders the swarm-feed layers legibly, carries the
403 events series and the nested-family task view, stamped + STALE.
PR-1 state: no Primary nav yet - the chrome PR adds its anchor
family-wide in one go (family.html precedent)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/help-wanted-dashboard"
PAGE = APP / "quota-swarm.html"
FEED = APP / "data/swarm-feed.json"


def test_swarm_feed_shape():
    feed = json.loads(FEED.read_text())
    assert feed["schema"] == "quota.swarm-feed/v1"
    assert feed["generated_at"]
    s = feed["summary"]
    assert s["registry_model_records"] >= 90
    assert s["distinct_providers"] >= 90
    g4f = next(p for p in feed["providers"] if p["provider"] == "g4f")
    assert g4f["record_count"] >= 60  # aggregator backends nest here
    assert feed["events"]["schema"] == "quota.rate-limit-events/v1"
    assert len(feed["events"]["events"]) >= 7


def test_page_renders_layers_events_and_tasks():
    html = PAGE.read_text()
    assert "swarm-feed.json" in html and "nested-family-feed.json" in html
    for marker in ("chart-layers", "chart-families", "eventTimeline",
                   "atwork-tree", "CK.bars", "CK.line", "CK.stampState",
                   "participant population"):
        assert marker in html
    assert 'aria-label="Primary"' not in html  # PR-1; chrome PR follows


def test_registry_sitemap_crosslinks():
    manifest = json.loads((APP / "version-manifest.json").read_text())
    files = [p["file"] for p in manifest["pages"]]
    assert "quota-swarm.html" in files and files == sorted(files)
    assert '"file":"quota-swarm.html"' in (APP / "versioning.js").read_text().replace(" ", "")
    assert "https://timerloggedout-spec.github.io/help-wanted/quota-swarm.html" in (APP / "sitemap.xml").read_text()
    assert "./quota-swarm.html" in (APP / "quota.html").read_text()
    assert "./quota-swarm.html" in (APP / "family.html").read_text()
    assert "./quota-swarm.html" in (APP / "admin.html").read_text()
