"""Classifiers page renders the steward feed and lateral observatory roles."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/tribute-dashboard"


def test_classifiers_page():
    html = (APP / "classifiers.html").read_text()
    assert "ops/classifiers/classifiers-feed.json" in html
    assert 'src="./chartkit.js"' in html and "CK.bars(" in html and "stampState" in html
    assert 'classifiers.html" aria-current="page">Classifiers' in html
    assert "observatory_quartet" in html and "variance_requirement" in html
    assert "Observatory role set" in html
    assert "Compare candidate implementations laterally" in html
    assert "'home','pipeline','trial'" not in html
    assert "'coded_quirk'" not in html
    assert "Tournament inventory" in html
    assert "classifier_graph_registry.json" in html
    assert "model candidates" in html
    assert "awaiting qualification" in html
    assert "Local Mev/Jev/Kev/Laya lateral screen" in html
    assert "independent role arms" in html
    assert "Tournament protocol" in html
    assert "Matched implementation comparator" in html
    assert "implementation_competition.py" in html
    assert "pct_breakdown" in html and "SHARES" in html
    assert "win_probability" not in html and "metrics_internal" not in html


def test_classifiers_sitemap_canonical():
    sm = (APP / "sitemap.xml").read_text()
    assert "https://timerloggedout-spec.github.io/tribute/classifiers.html" in sm
    assert "/help-wanted/" not in sm
