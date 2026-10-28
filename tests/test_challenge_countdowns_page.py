"""Contract tests for countdowns.html (issue #1880, dashboard surface).

The page consumes only its own feed, computes state and remaining
time client-side from the stored instants on a 1s tick, and never
renders a baked remaining-seconds value.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "countdowns.html"
FEED = APP / "data" / "challenge-countdowns-feed.json"
PAGES = ["index.html", "quota.html", "matrix.html", "admin.html",
         "oracle.html", "moneyball.html", "3l0.html", "mvt.html",
         "doe.html", "ates.html", "free-tier-value.html",
         "dispatch-tree.html", "countdowns.html"]
LINK = "https://timerloggedout-spec.github.io/help-wanted/countdowns.html"


def _page():
    return PAGE.read_text(encoding="utf-8")


def test_page_fetches_only_its_feed():
    html = _page()
    fetches = re.findall(r"fetch\(([^)]*)\)", html)
    assert fetches == ['"./data/challenge-countdowns-feed.json"'], fetches
    assert "api.github.com" not in html
    assert "raw.githubusercontent" not in html


def test_countdown_computed_client_side_from_instants():
    html = _page()
    assert "setInterval(tick,1000)" in html
    assert "Date.parse(e.opens)" in html and "Date.parse(e.closes)" in html
    assert "seconds_to" not in html, "page must never consume a baked remaining-seconds value"
    assert "Date.now()" in html


def test_honest_states_present():
    html = _page()
    for s in ("not recorded", "nothing is shown rather than anything guessed",
              "Overdue", "Completed"):
        assert s in html, s


def test_no_credential_markers():
    html = _page()
    for marker in ("ghp_", "github_pat_", "Bearer ", "api_key", "access_token"):
        assert marker not in html, marker


def test_nav_and_sitemap_wiring():
    for name in PAGES:
        text = (APP / name).read_text(encoding="utf-8")
        assert f'href="{LINK}"' in text, f"countdowns nav link missing in {name}"
    own = _page()
    assert f'href="{LINK}" aria-current="page"' in own
    sitemap = (APP / "sitemap.xml").read_text(encoding="utf-8")
    assert f"<loc>{LINK}</loc>" in sitemap


def test_feed_entries_renderable_shape():
    feed = json.loads(FEED.read_text(encoding="utf-8"))
    assert feed["schema"] == "challenge-countdowns-feed/v1"
    for e in feed["entries"]:
        assert e["title"] and e["id"].startswith("D")
