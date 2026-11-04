"""D2 delineation page contract tests (viz chrome adaptation).

Content of record is the D2 exercise source; these tests pin the
adaptation invariants only: dashboard shell present, delineation
styles scoped under .d2del (dashboard.css defines .card/.grid -
unscoped copies would collide), the picker + six panels intact,
the advisory framing line present.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/tribute-dashboard/d2-delineation.html"


def _page():
    return PAGE.read_text()


def test_shell_and_scoping():
    html = _page()
    assert 'src="./shell.js"' in html and 'id="topbar"' in html
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
