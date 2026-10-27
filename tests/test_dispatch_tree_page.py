"""Dispatch Tree page contract (Web Design lane, 2026-10-27).

The visualization lane owns the feed + rendering logic (contract:
docs/ops/DISPATCH-TREE-FEED.md, schema dispatch-tree-feed/v1); the Web
Design lane owns the page integration. These tests pin that integration:

* the page consumes ./data/dispatch-tree-feed.json and nothing else;
* the spec'd surface elements are present (Node A guard hero, the
  comment-vs-code gap, the 32-lane cadence table, firing history,
  recorded gaps) and every feed value renders from the feed — nothing
  about the guard, the lanes or the history is hardcoded in the page;
* the page is wired into the unified nav of every published dashboard
  page, carries aria-current on its own nav link, and is in the sitemap.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "dispatch-tree.html"
FEED = APP / "data" / "dispatch-tree-feed.json"
FEED_URL = "./data/dispatch-tree-feed.json"
NAV_LINK = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
            'dispatch-tree.html">Dispatch Tree</a>')
NAV_PAGES = ["index.html", "quota.html", "matrix.html", "admin.html",
             "oracle.html", "moneyball.html", "3l0.html", "mvt.html",
             "doe.html", "ates.html", "free-tier-value.html"]


def _html():
    return PAGE.read_text(encoding="utf-8")


def _feed():
    return json.loads(FEED.read_text(encoding="utf-8"))


def test_page_consumes_only_its_feed():
    html = _html()
    fetches = re.findall(r"""fetch\(\s*["']([^"']+)["']""", html)
    assert fetches == [FEED_URL]
    assert "api.github.com" not in html
    assert "raw.githubusercontent" not in html


def test_feed_is_the_contract_shape():
    feed = _feed()
    assert feed["schema"] == "dispatch-tree-feed/v1"
    adm = feed["data"]["admission"]
    assert adm["guard_threshold"] == 6
    assert len(feed["data"]["lanes"]) == 32
    gap_ids = {g["id"] for g in feed["gaps"]}
    assert "busy-history-starts-at-first-collection" in gap_ids


def test_spec_surface_and_no_hardcoded_values():
    html, feed = _html(), _feed()
    for marker in ("Node A", "admission guard", "Lanes — cadence state",
                   "Firing history", "Recorded gaps", "dashboard.css"):
        assert marker in html, marker
    adm = feed["data"]["admission"]
    # guard facts render from the feed, never from page literals
    assert adm["guard_expression"] not in html
    assert adm["code_counts"] not in html
    assert adm["comment_says"] not in html
    for lane in feed["data"]["lanes"]:
        if lane["rule_expression"]:
            assert lane["rule_expression"] not in html, lane["lane"]


def test_phase_only_lanes_have_no_invented_due():
    feed = _feed()
    phase_only = [l for l in feed["data"]["lanes"]
                  if l["due_at_read"] is None]
    assert phase_only, "the record holds phase-only lanes; keep them honest"


def test_nav_and_sitemap_wiring():
    html = _html()
    assert 'dispatch-tree.html" aria-current="page"' in html
    for name in NAV_PAGES:
        other = (APP / name).read_text(encoding="utf-8")
        assert NAV_LINK in other, name
    sitemap = (APP / "sitemap.xml").read_text(encoding="utf-8")
    assert ("<loc>https://timerloggedout-spec.github.io/help-wanted/"
            "dispatch-tree.html</loc>") in sitemap


def test_no_credentials_or_mutation():
    html = _html()
    for marker in ("ghp_", "github_pat_", "API_KEY", "password"):
        assert marker not in html
    assert 'method:"POST"' not in html.replace(" ", "")
