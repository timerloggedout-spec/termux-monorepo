"""Contract tests for the public nested workflow discovery page."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"


def test_workflow_discovery_page_is_feed_only_and_discoverable():
    html = (APP / "workflows.html").read_text(encoding="utf-8")
    assert "./dashboard.css" in html
    assert 'fetch("./data/workflow-discovery-feed.json")' in html
    fetches = re.findall(r'fetch\("([^"]+)"\)', html)
    assert fetches == ["./data/workflow-discovery-feed.json"]
    assert "api.github.com" not in html
    assert "raw.githubusercontent" not in html
    assert "nothing is shown rather than anything guessed" in html
    assert 'id="workflow-run-edges"' in html
    assert 'id="reusable-edges"' in html
    assert 'id="schedule-rows"' in html
    assert 'id="activity-rows"' in html
    assert "public standard hosted-runner minutes are free" in html.lower()
    assert "workflows.html" in (APP / "site-nav.js").read_text(encoding="utf-8")
    assert "workflows.html" in (APP / "index.html").read_text(encoding="utf-8")
    assert "workflows.html" in (APP / "sitemap.xml").read_text(encoding="utf-8")
