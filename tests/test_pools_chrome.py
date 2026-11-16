"""Pools chrome wiring (Web Design lane).

pools.html (PR #4714, viz lane) shipped bare; the shell rule is one
consistent primary nav on every shell page. This file pins the Pools
anchor's place in that nav (immediately after Wagering Book), its
aria-current ownership, and the Admin inventory row.
"""
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "apps/tribute-dashboard"

POOLS = ('<a href="https://timerloggedout-spec.github.io/tribute/'
         'pools.html">Pools</a>')
POOLS_CURRENT = ('<a href="https://timerloggedout-spec.github.io/tribute/'
                 'pools.html" aria-current="page">Pools</a>')
WAGERING = ('<a href="https://timerloggedout-spec.github.io/tribute/'
            'wagering-book.html">Wagering Book</a>')
WAGERING_CURRENT = ('<a href="https://timerloggedout-spec.github.io/tribute/'
                    'wagering-book.html" aria-current="page">Wagering Book</a>')


def _nav(page: str) -> str:
    raw = (APP / f"{page}.html").read_text(encoding="utf-8")
    m = re.search(r'<nav aria-label="Primary">(.*?)</nav>', raw, re.S)
    assert m, f"{page}: primary nav missing"
    return m.group(1)


def test_pools_anchor_after_wagering_in_pools_nav():
    nav = _nav("pools")
    assert nav.count("pools.html") == 1
    assert WAGERING + POOLS_CURRENT in nav


def test_pools_aria_current_only_on_pools():
    nav = _nav("pools")
    assert nav.count('aria-current="page"') == 1
    assert POOLS_CURRENT in nav
    wag = _nav("wagering-book")
    assert WAGERING_CURRENT + POOLS in wag


def test_pools_admin_inventory_row():
    raw = (APP / "admin.html").read_text(encoding="utf-8")
    assert raw.count("<td>Pools</td>") == 1
    assert raw.count('href="./pools.html"') >= 2


def test_pools_sitemap_and_registry():
    sm = (APP / "sitemap.xml").read_text(encoding="utf-8")
    assert sm.count("/tribute/pools.html") == 1
    assert "/help-wanted/" not in sm
    import json
    vm = json.loads((APP / "version-manifest.json").read_text(encoding="utf-8"))
    assert [p for p in vm["pages"] if p["file"] == "pools.html"] == [
        {"id": "pools", "file": "pools.html", "title": "Pools",
         "content_sha256": None}]
    vj = (APP / "versioning.js").read_text(encoding="utf-8")
    assert '"id":"pools","file":"pools.html"' in vj
