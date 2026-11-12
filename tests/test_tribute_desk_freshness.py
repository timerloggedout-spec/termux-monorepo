"""Per-feed freshness contract for the Tribute Contribution Desk."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/tribute-dashboard/desk.html"
CHARTKIT = ROOT / "apps/tribute-dashboard/chartkit.js"

class TributeDeskFreshnessTests(unittest.TestCase):
    def test_every_independent_desk_feed_exposes_its_own_freshness(self):
        html = PAGE.read_text(encoding="utf-8")
        self.assertIn('CK.stampState(PACK.generated_at,Date.now())', html)
        self.assertIn('CK.stampState(f.generated_at,Date.now())', html)
        self.assertIn('stamp($("questamp"), d)', html)
        self.assertIn('stamp($("quegovstamp"), d)', html)
        self.assertIn('stamp($("quewinstamp"), d)', html)
        for name in ["desk-feed.json", "dispatch-state-feed.json", "queue-by-tier.json",
                     "que-governor.json", "que-priority-windows.json"]:
            self.assertIn(name, html)

    def test_freshness_is_per_feed_with_a_24_hour_threshold(self):
        chartkit = CHARTKIT.read_text(encoding="utf-8")
        self.assertIn("function stampState(generatedAt, nowMs, thresholdMs = 86400000)", chartkit)
        self.assertIn("return 'STALE'", chartkit)
        self.assertIn("return 'unknown'", chartkit)

    def test_unknown_state_is_rendered_explicitly(self):
        html = PAGE.read_text(encoding="utf-8")
        self.assertIn('+" · "+st+" · schema "+', html)

if __name__ == "__main__":
    unittest.main()
