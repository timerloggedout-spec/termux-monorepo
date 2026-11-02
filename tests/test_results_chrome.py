"""Results-index chrome (web-design leg for viz PR #3881): the page joins
the shell - self-anchor in its own nav + the canonical sitemap loc."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/tribute-dashboard"


def test_results_chrome():
    html = (APP / "results-index.html").read_text()
    assert 'results-index.html" aria-current="page">Results Index' in html
    sm = (APP / "sitemap.xml").read_text()
    assert "https://timerloggedout-spec.github.io/tribute/results-index.html" in sm
    assert "/help-wanted/" not in sm
