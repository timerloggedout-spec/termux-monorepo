"""Quota Graphs chrome wiring (Web Design lane).

quota-graphs.html (PR #2913, viz lane) shipped with a minimal nav; the
shell rule is one consistent primary nav on every shell page. This file
pins the Quota Graphs anchor's place in that nav (immediately after
Quota Usage), its aria-current ownership, the Admin inventory row and
the sitemap loc. admin-graph.html is excluded by design: a
self-contained page with zero outbound links.
"""
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "apps/tribute-dashboard"

SHELL_PAGES = [
    "index", "quota", "admin", "oracle", "3l0", "moneyball", "mvt", "doe",
    "ates", "free-tier-value", "dispatch-tree", "countdowns", "linguist",
    "delphi-rfp", "delphi-ledger", "pr-lanes", "proposals", "quota-usage",
    "telemetry", "desk", "quota-graphs",
]
QG = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
      'quota-graphs.html">Quota Graphs</a>')
QG_CURRENT = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
              'quota-graphs.html" aria-current="page">Quota Graphs</a>')
QU = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
      'quota-usage.html">Quota Usage</a>')
QU_CURRENT = ('<a href="https://timerloggedout-spec.github.io/'
              'help-wanted/quota-usage.html" aria-current="page">'
              'Quota Usage</a>')


def _nav(page: str) -> str:
    raw = (APP / f"{page}.html").read_text(encoding="utf-8")
    m = re.search(r'<nav aria-label="Primary">(.*?)</nav>', raw, re.S)
    assert m, f"{page}: primary nav missing"
    return m.group(1)


def test_quota_graphs_anchor_in_every_shell_nav_after_quota_usage():
    for page in SHELL_PAGES:
        nav = _nav(page)
        assert nav.count("quota-graphs.html") == 1, page
        qu = QU_CURRENT if page == "quota-usage" else QU
        qg = QG_CURRENT if page == "quota-graphs" else QG
        assert qu in nav, page
        assert nav.index(qu) < nav.index(qg), page


def test_only_quota_graphs_marks_itself_current():
    for page in SHELL_PAGES:
        nav = _nav(page)
        if page == "quota-graphs":
            assert QG_CURRENT in nav
        else:
            assert QG_CURRENT not in nav, page


def test_admin_inventory_and_sitemap_have_quota_graphs():
    admin = (APP / "admin.html").read_text(encoding="utf-8")
    assert "<td>Quota Graphs</td>" in admin
    assert '<a href="./quota-graphs.html">quota-graphs.html</a>' in admin
    sitemap = (APP / "sitemap.xml").read_text(encoding="utf-8")
    assert "help-wanted/quota-graphs.html" in sitemap
