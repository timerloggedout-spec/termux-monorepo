"""D2 delineation page contract tests (viz chrome adaptation).

The page's single home is d2-proposals.html (D2 seat ruling);
content of record is the D2 exercise source. These tests pin the
adaptation invariants only: Web Design's static chrome intact,
delineation styles scoped under .d2del (dashboard.css defines
.card/.grid - unscoped copies collide and leak element styles),
the picker + six panels intact, the advisory framing present.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/tribute-dashboard/d2-proposals.html"


def _page():
    return PAGE.read_text()


def test_shell_and_scoping():
    html = _page()
    assert 'aria-current="page">D2 Proposals' in html
    assert 'href="./dashboard.css"' in html
    style = html.split("<style>")[1].split("</style>")[0]
    assert ".d2del .card{" in style and ".d2del .grid{" in style
    bare = [ln for ln in style.splitlines()
            if re.match(r"\s*\.(card|grid|panel|picker)\b", ln)
            and ".d2del" not in ln]
    assert bare == []
    assert "minmax(280px,1fr)" in style


def test_content_intact():
    html = _page()
    assert 'id="pick"' in html
    assert len(re.findall(r'id="panel-[a-f]"', html)) == 6
    assert "the pick is the owner" in html
    assert "ADVISORY RANK" in html
