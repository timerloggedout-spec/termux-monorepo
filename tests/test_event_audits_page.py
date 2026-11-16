"""Event-audits page contract (owner directive 2026-11-01 23:32 PT):
the audits get a served page - findings + coverage state from the
audits feed only, coverage staleness against the register, cross-link
from the quota-graphs events tab. PR-1: no Primary nav yet (chrome
PR follows family-wide, as with family/quota-swarm)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/tribute-dashboard"
PAGE = APP / "quota-event-audits.html"
FEED = APP / "data/rate-limit-event-audits.json"


def test_audits_feed_shape():
    feed = json.loads(FEED.read_text())
    assert feed["schema"] == "quota.rate-limit-event-audits/v1"
    assert feed["audits"]
    for a in feed["audits"]:
        assert a["at"] and a["auditor"] and isinstance(a["events_covered"], int)
        for f in a["findings"]:
            for key in ("id", "class", "event_refs", "improvement", "owner", "state"):
                assert key in f


def test_page_render_and_coverage():
    html = PAGE.read_text()
    assert "rate-limit-event-audits.json" in html
    assert "rate-limit-events.json" in html  # register cross-check
    for marker in ("chart-coverage", "chart-states", "chart-classes",
                   "findingCard", "CK.bars", "coverage CURRENT", "BEHIND"):
        assert marker in html
    assert 'aria-label="Primary"' not in html  # PR-1; chrome follows


def test_crosslink_and_registry():
    graphs = (APP / "quota-graphs.html").read_text()
    assert "./quota-event-audits.html" in graphs
    manifest = json.loads((APP / "version-manifest.json").read_text())
    files = [p["file"] for p in manifest["pages"]]
    assert "quota-event-audits.html" in files and files == sorted(files)
    assert '"file":"quota-event-audits.html"' in (APP / "versioning.js").read_text().replace(" ", "")
    assert "https://timerloggedout-spec.github.io/tribute/quota-event-audits.html" in (APP / "sitemap.xml").read_text()
    assert "./quota-event-audits.html" in (APP / "admin.html").read_text()
