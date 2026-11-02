"""Classifiers page (owner order, 2026-11-02): renders ONLY the steward's
classifiers feed (classifiers-feed/v1) - census charts, the full unit
table, the observatory quartet, and the %-breakdown record with shares
labelled as shares. Win-probability machinery stays off public pages."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/help-wanted-dashboard"


def test_classifiers_page():
    html = (APP / "classifiers.html").read_text()
    assert "ops/classifiers/classifiers-feed.json" in html
    assert 'src="./chartkit.js"' in html and "CK.bars(" in html and "stampState" in html
    assert 'classifiers.html" aria-current="page">Classifiers' in html
    assert "observatory_quartet" in html and "variance_requirement" in html
    assert "pct_breakdown" in html and "SHARES" in html
    assert "win_probability" not in html and "metrics_internal" not in html


def test_classifiers_sitemap_canonical():
    sm = (APP / "sitemap.xml").read_text()
    assert "https://timerloggedout-spec.github.io/tribute/classifiers.html" in sm
    assert "/help-wanted/" not in sm
