"""Tracking board chrome wiring (Web Design lane).

tracking.html (PR #2941, viz lane) shipped with a minimal nav; the
shell rule is one consistent primary nav on every shell page. This
file pins the Tracking anchor's place in that nav (immediately after
Desk), its aria-current ownership, the Admin inventory row and the
sitemap loc. admin-graph.html is excluded by design: a self-contained
page with zero outbound links.
"""
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "apps/tribute-dashboard"

SHELL_PAGES = [
    "index", "quota", "admin", "oracle", "3l0", "moneyball", "mvt", "doe",
    "ates", "free-tier-value", "dispatch-tree", "countdowns", "linguist",
    "delphi-rfp", "delphi-ledger", "pr-lanes", "proposals", "quota-usage",
    "quota-graphs", "telemetry", "desk", "tracking",
]
BASE = "https://timerloggedout-spec.github.io/help-wanted/"
TR = f'<a href="{BASE}tracking.html">Tracking</a>'
TR_CURRENT = f'<a href="{BASE}tracking.html" aria-current="page">Tracking</a>'
DESK = f'<a href="{BASE}desk.html">Desk</a>'
DESK_CURRENT = f'<a href="{BASE}desk.html" aria-current="page">Desk</a>'


def _nav(page: str) -> str:
    raw = (APP / f"{page}.html").read_text(encoding="utf-8")
    m = re.search(r'<nav aria-label="Primary">(.*?)</nav>', raw, re.S)
    assert m, f"{page}: primary nav missing"
    return m.group(1)


def test_tracking_anchor_in_every_shell_nav_after_desk():
    for page in SHELL_PAGES:
        nav = _nav(page)
        assert nav.count("tracking.html") == 1, page
        desk = DESK_CURRENT if page == "desk" else DESK
        tr = TR_CURRENT if page == "tracking" else TR
        assert desk in nav, page
        assert nav.index(desk) < nav.index(tr), page


def test_only_tracking_marks_itself_current():
    for page in SHELL_PAGES:
        nav = _nav(page)
        if page == "tracking":
            assert TR_CURRENT in nav
        else:
            assert TR_CURRENT not in nav, page


def test_admin_inventory_and_sitemap_have_tracking():
    admin = (APP / "admin.html").read_text(encoding="utf-8")
    assert "<td>Tracking</td>" in admin
    assert '<a href="./tracking.html">tracking.html</a>' in admin
    sitemap = (APP / "sitemap.xml").read_text(encoding="utf-8")
    assert "help-wanted/tracking.html" in sitemap
