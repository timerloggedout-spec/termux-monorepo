"""Admin Graph page contract and live routing-pulse integration."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
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
    assert "api.github.com" not in html
    assert "raw.githubusercontent" not in html


def test_live_route_pulse_contract():
    html = _html()
    for marker in ("LIVE ROUTE PULSES", "LIVE_FEED_URL", "task_routed",
                   "routing-orch", "after_seq", "PREPARED",
                   "pull-to-refresh", "DEPLOYMENT-LANES"):
        assert marker in html, marker


def test_nav_link_on_every_published_page():
    for name in NAV_PAGES:
        assert NAV_LINK in (APP / name).read_text(encoding="utf-8")


def test_in_sitemap():
    assert "help-wanted/admin-graph.html" in (APP / "sitemap.xml").read_text(encoding="utf-8")


def test_admin_systems_inventory_row():
    assert "<td>Admin Interaction Graph</td>" in (APP / "admin.html").read_text(encoding="utf-8")
