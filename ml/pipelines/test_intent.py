import unittest
from ml.pipelines.command_center.intent import summarize_intent

BODY = """## Next OPERATOR actions:
1. Dual-gate this SHA
2. Leave #48 on master-staging
Lane vocab: EXTRACT CANDIDATE NEED_EVIDENCE SUPERSEDE
Do not HOLD or WAIT
"""

class IntentTest(unittest.TestCase):
    def test_parse(self) -> None:
        out = summarize_intent(BODY)
        self.assertIn("EXTRACT", out["lanes_mentioned"])
        self.assertIn("HOLD", out["invalid_parking"])
        self.assertFalse(out["pulse_comments_allowed"])
        self.assertTrue(any("Dual-gate" in x for x in out["next"]))
