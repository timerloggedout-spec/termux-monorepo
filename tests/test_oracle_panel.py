"""Oracle Panel page contract (Web Design lane, 2026-10-27).

The Delphi lane owns the data contract (docs/ops/ORACLE-PANEL-FEED.md):
oracle.html consumes apps/help-wanted-dashboard/data/oracle-panel-feed.json and nothing
else. These tests pin the rendering side of that contract:

* the page reads the contract feed (raw master, the fleet pattern) and no
  other data source;
* the honesty renderers exist in the page: UNVERIFIED points,
  specified_not_run, absent classes shown as absent (never participation),
  and null rounds/calibration rendered as absent (never zero-filled);
* every proposal in the feed can be rendered — the panel must never show
  a proposal the feed (and therefore the registry) does not hold;
* the page is wired into the unified nav, the sitemap, and the admin
  panel; it embeds no credentials and posts nothing.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
FEED = APP / "data/oracle-panel-feed.json"
FEED_URL = "./data/oracle-panel-feed.json"


def _html():
    return (APP / "oracle.html").read_text()


def _feed():
    return json.loads(FEED.read_text())


def test_page_consumes_the_contract_feed_and_nothing_else():
    html = _html()
    assert FEED_URL in html
    assert "oracle-panel-feed" in html
    # No other data endpoints: the contract feed is the only source.
    assert "api.github.com" not in html
    assert "raw.githubusercontent.com" not in html


def test_feed_is_the_contract_shape():
    feed = _feed()
    assert feed["schema"] == "oracle-panel-feed/v1"
    assert feed["sources"]["oracle_method_proposals"] == len(feed["proposals"])
    for p in feed["proposals"]:
        assert p["author"] == "oracle-method"
        assert isinstance(p["unverified_points"], list)
        assert isinstance(p["specified_not_run"], list)
        if p["rounds"] is not None:
            for rnd in ("round_1", "round_2"):
                r = p["rounds"][rnd]
                assert r["rank_of_this"] == r["ranking"].index(p["id"]) + 1
                for cls in r.get("classes_absent", []):
                    assert r["ballots_by_class"][cls] == 0


def test_honesty_renderers_present():
    html = _html()
    assert "UNVERIFIED" in html
    assert "specified_not_run" in html
    assert "classes_absent" in html  # absent classes rendered as absent
    assert "Absent from the record" in html  # null renders as absent
    assert "excluded" in html  # rehearsals named, not silently dropped
    assert "expectations" in html and "implementation" in html  # v1.1 blocks


def test_page_wiring_and_no_credentials():
    html = _html()
    assert "./dashboard.css" in html
    assert (
        'href="https://timerloggedout-spec.github.io/help-wanted/oracle.html" '
        'aria-current="page"'
    ) in html
    link = 'href="https://timerloggedout-spec.github.io/help-wanted/oracle.html"'
    for page in ("index.html", "quota.html", "matrix.html", "admin.html"):
        assert link in (APP / page).read_text(), page
    assert "https://timerloggedout-spec.github.io/help-wanted/oracle.html" in (
        APP / "sitemap.xml"
    ).read_text()
    lowered = html.lower()
    for forbidden in ("ghp_", "github_pat_", "bearer ", "authorization",
                      "method:'post'", 'method:"post"', "method: 'post'"):
        assert forbidden not in lowered, forbidden
