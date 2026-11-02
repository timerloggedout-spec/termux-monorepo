"""Wagering-book chrome (web-design leg for viz PR #3866): the page joins
the shell - self-anchor in its own nav + the canonical sitemap loc."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/tribute-dashboard"


def test_wagering_chrome():
    html = (APP / "wagering-book.html").read_text()
    assert 'wagering-book.html" aria-current="page">Wagering Book' in html
    sm = (APP / "sitemap.xml").read_text()
    assert "https://timerloggedout-spec.github.io/tribute/wagering-book.html" in sm
    assert "/help-wanted/" not in sm
