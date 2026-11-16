"""D2 Proposals chrome wiring (Web Design lane).

d2-proposals.html (D2 exercise record, published at the owner's
order via the D2 seat) carries the shell Primary nav; this file pins
the D2 Proposals anchor's place (immediately after Countdowns), its
aria-current ownership, the Admin inventory row, and that the page
content framing (advisory-only ranking, pick owner-held) is intact.
"""
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "apps/tribute-dashboard"

D2 = ('<a href="https://timerloggedout-spec.github.io/tribute/'
      'd2-proposals.html">D2 Proposals</a>')
D2_CURRENT = ('<a href="https://timerloggedout-spec.github.io/tribute/'
              'd2-proposals.html" aria-current="page">D2 Proposals</a>')
CD = ('<a href="https://timerloggedout-spec.github.io/tribute/'
      'countdowns.html">Countdowns</a>')
CD_CURRENT = ('<a href="https://timerloggedout-spec.github.io/tribute/'
              'countdowns.html" aria-current="page">Countdowns</a>')


def _nav(page: str) -> str:
    raw = (APP / f"{page}.html").read_text(encoding="utf-8")
    m = re.search(r'<nav aria-label="Primary">(.*?)</nav>', raw, re.S)
    assert m, f"{page}: primary nav missing"
    return m.group(1)


def test_d2_anchor_after_countdowns_in_own_nav():
    nav = _nav("d2-proposals")
    assert nav.count("d2-proposals.html") == 1
    assert CD + D2_CURRENT in nav
    assert nav.count('aria-current="page"') == 1


def test_d2_anchor_in_countdowns_nav():
    nav = _nav("countdowns")
    assert CD_CURRENT + D2 in nav


def test_d2_admin_inventory_row():
    raw = (APP / "admin.html").read_text(encoding="utf-8")
    assert raw.count("<td>D2 Proposals</td>") == 1
    assert raw.count('href="./d2-proposals.html"') >= 2


def test_d2_framing_intact():
    raw = (APP / "d2-proposals.html").read_text(encoding="utf-8")
    assert "Proposal Delineation" in raw
    assert "ADVISORY" in raw


def test_d2_sitemap_and_registry():
    sm = (APP / "sitemap.xml").read_text(encoding="utf-8")
    assert sm.count("/tribute/d2-proposals.html") == 1
    assert "/help-wanted/" not in sm
    import json
    vm = json.loads((APP / "version-manifest.json").read_text(encoding="utf-8"))
    assert [p for p in vm["pages"] if p["file"] == "d2-proposals.html"] == [
        {"id": "d2-proposals", "file": "d2-proposals.html",
         "title": "D2 Proposals", "content_sha256": None}]
    vj = (APP / "versioning.js").read_text(encoding="utf-8")
    assert '"id":"d2-proposals","file":"d2-proposals.html"' in vj
    sj = (APP / "site-nav.js").read_text(encoding="utf-8")
    assert '"d2-proposals.html", "d2-proposals"' in sj
