"""Per-feed freshness contract for the Tribute Contribution Desk."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/tribute-dashboard/desk.html"
CHARTKIT = ROOT / "apps/tribute-dashboard/chartkit.js"

def test_every_independent_desk_feed_exposes_its_own_freshness():
    html = PAGE.read_text(encoding="utf-8")
    assert 'CK.stampState(PACK.generated_at,Date.now())' in html
    assert 'CK.stampState(f.generated_at,Date.now())' in html
    assert 'stamp($("questamp"), d)' in html
    assert 'stamp($("quegovstamp"), d)' in html
    assert 'stamp($("quewinstamp"), d)' in html
    for name in ["desk-feed.json", "dispatch-state-feed.json", "queue-by-tier.json",
                 "que-governor.json", "que-priority-windows.json"]:
        assert name in html

def test_freshness_is_per_feed_with_a_24_hour_threshold():
    chartkit = CHARTKIT.read_text(encoding="utf-8")
    assert "function stampState(generatedAt, nowMs, thresholdMs = 86400000)" in chartkit
    assert "return 'STALE'" in chartkit
    assert "return 'unknown'" in chartkit
