"""Admin Graph page contract (2026-10-30).

The Admin Interaction Graph is a self-contained canonical-model admin UI:
the model is rendered deterministically, every node/edge carries a
repoSource, and statuses follow docs/DEPLOYMENT-LANES.md (SSOT) with
repo-delta markers where the repo's own docs disagree. These tests pin
the page's wiring into the published dashboard set:

* the page is present and carries its honesty markers (simulated pulses,
  prepared-not-sent dispatch, pull-to-refresh suppression);
* the unified nav of every published dashboard page links to it;
* it is in the sitemap.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
PAGE = APP / "admin-graph.html"
NAV_LINK = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
            'admin-graph.html">Admin Graph</a>')
NAV_PAGES = ["index.html", "quota.html", "matrix.html", "admin.html",
             "oracle.html", "moneyball.html", "3l0.html", "mvt.html",
             "doe.html", "ates.html", "free-tier-value.html",
             "countdowns.html", "delphi-ledger.html", "delphi-rfp.html",
             "dispatch-tree.html", "linguist.html", "pr-lanes.html",
             "proposals.html", "quota-usage.html", "telemetry.html"]


def _html():
    return PAGE.read_text(encoding="utf-8")


def test_page_present_and_self_contained():
    html = _html()
    assert "Admin Interaction Graph" in html
    # no credential-bearing or live API calls from the page
    assert "api.github.com" not in html
    assert "raw.githubusercontent" not in html


def test_honesty_markers_present():
    html = _html()
    for marker in ("SIMULATED PULSES", "PREPARED", "pull-to-refresh",
                   "DEPLOYMENT-LANES"):
        assert marker in html, marker


def test_nav_link_on_every_published_page():
    for name in NAV_PAGES:
        text = (APP / name).read_text(encoding="utf-8")
        assert NAV_LINK in text, name


def test_in_sitemap():
    sitemap = (APP / "sitemap.xml").read_text(encoding="utf-8")
    assert "help-wanted/admin-graph.html" in sitemap
