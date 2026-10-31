"""Contribution Desk chrome wiring (Web Design lane).

desk.html (PR #2624, viz lane) shipped with a minimal 4-anchor nav; the
shell rule is one consistent primary nav on every shell page. This file
pins the Desk anchor's place in that nav (immediately after Telemetry),
its aria-current ownership, and the Admin inventory row. admin-graph.html
is excluded by design: a self-contained page with zero outbound links.
"""
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "apps/help-wanted-dashboard"

SHELL_PAGES = [
    "index", "quota", "admin", "oracle", "3l0", "moneyball", "mvt", "doe",
    "ates", "free-tier-value", "dispatch-tree", "countdowns", "linguist",
    "delphi-rfp", "delphi-ledger", "pr-lanes", "proposals", "quota-usage",
    "telemetry", "desk",
]
DESK = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
        'desk.html">Desk</a>')
DESK_CURRENT = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
                'desk.html" aria-current="page">Desk</a>')
TELEMETRY = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
             'telemetry.html">Telemetry</a>')
TELEMETRY_CURRENT = ('<a href="https://timerloggedout-spec.github.io/'
                     'help-wanted/telemetry.html" aria-current="page">'
                     'Telemetry</a>')


def _nav(page: str) -> str:
    raw = (APP / f"{page}.html").read_text(encoding="utf-8")
    m = re.search(r'<nav aria-label="Primary">(.*?)</nav>', raw, re.S)
    assert m, f"{page}: primary nav missing"
    return m.group(1)


def test_desk_anchor_in_every_shell_nav_after_telemetry():
    for page in SHELL_PAGES:
        nav = _nav(page)
        assert nav.count("desk.html") == 1, page
        tel = TELEMETRY_CURRENT if page == "telemetry" else TELEMETRY
        desk = DESK_CURRENT if page == "desk" else DESK
        assert tel in nav, page
        assert nav.index(tel) < nav.index(desk), page


def test_only_desk_marks_desk_current():
    for page in SHELL_PAGES:
        nav = _nav(page)
        if page == "desk":
            assert DESK_CURRENT in nav
        else:
            assert DESK_CURRENT not in nav, page


def test_admin_inventory_has_desk_row():
    admin = (APP / "admin.html").read_text(encoding="utf-8")
    assert "<td>Contribution Desk</td>" in admin
    assert '<a href="./desk.html">desk.html</a>' in admin
    sitemap = (APP / "sitemap.xml").read_text(encoding="utf-8")
    assert "help-wanted/desk.html" in sitemap
