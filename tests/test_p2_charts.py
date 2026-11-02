"""P2 chart wiring (chart standard ①): each wired page loads chartkit
and renders at least one chart from its own feed, with the feed stamp."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/help-wanted-dashboard"


def test_doe_charts():
    html = (APP / "doe.html").read_text()
    assert 'src="./chartkit.js"' in html
    assert "CK.bars(" in html
    assert "stampState" in html


def test_ates_charts():
    html = (APP / "ates.html").read_text()
    assert 'src="./chartkit.js"' in html
    assert "CK.bars(" in html
    assert "stampState" in html


def test_p3l0_charts():
    html = (APP / "3l0.html").read_text()
    assert 'src="./chartkit.js"' in html
    assert "CK.bars(" in html
    assert "stampState" in html


def test_mvt_charts():
    html = (APP / "mvt.html").read_text()
    assert 'src="./chartkit.js"' in html
    assert "CK.bars(" in html
    assert "stampState" in html


def test_moneyball_charts():
    html = (APP / "moneyball.html").read_text()
    assert 'src="./chartkit.js"' in html
    assert "CK.bars(" in html
    assert "stampState" in html


def test_oracle_charts():
    html = (APP / "oracle.html").read_text()
    assert 'src="./chartkit.js"' in html
    assert "CK.bars(" in html
    assert "stampState" in html


def test_delphi_rfp_charts():
    html = (APP / "delphi-rfp.html").read_text()
    assert 'src="./chartkit.js"' in html
    assert "CK.bars(" in html
    assert "stampState" in html


def test_delphi_ledger_charts():
    html = (APP / "delphi-ledger.html").read_text()
    assert 'src="./chartkit.js"' in html
    assert "CK.bars(" in html
    assert "stampState" in html


def test_proposals_charts():
    html = (APP / "proposals.html").read_text()
    assert 'src="./chartkit.js"' in html
    assert "CK.bars(" in html
    assert "stampState" in html


def test_free_tier_value_charts():
    html = (APP / "free-tier-value.html").read_text()
    assert 'src="./chartkit.js"' in html
    assert "CK.bars(" in html
    assert "stampState" in html


def test_admin_charts():
    html = (APP / "admin.html").read_text()
    assert 'src="./chartkit.js"' in html
    assert "CK.bars(" in html
    assert "stampState" in html

