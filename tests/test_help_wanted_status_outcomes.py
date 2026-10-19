"""Operational receipts must not be counted as successful tributes."""
import unittest
from pathlib import Path

from scripts.ci.help_wanted_status import classify_receipt_outcome


class HelpWantedStatusOutcomeTests(unittest.TestCase):
    def test_skip_is_skipped_not_successful_work(self):
        self.assertEqual(
            classify_receipt_outcome({"kind": "followup_skip_cooldown", "ok": True, "action": "skip"}),
            "skipped",
        )

    def test_successful_action_is_actioned_not_accepted(self):
        self.assertEqual(
            classify_receipt_outcome({"kind": "followup_stale_nudge", "ok": True, "action": "stale_nudge"}),
            "actioned",
        )

    def test_failed_action_is_failed(self):
        self.assertEqual(
            classify_receipt_outcome({"kind": "followup_changes", "ok": False, "action": "changes"}),
            "failed",
        )

    def test_failed_skip_receipt_is_not_hidden_as_skipped(self):
        self.assertEqual(
            classify_receipt_outcome({"kind": "followup_skip_cooldown", "ok": False, "action": "skip"}),
            "failed",
        )

    def test_dashboard_exposes_audited_stages_and_operational_outcomes(self):
        html = Path("apps/help-wanted-dashboard/index.html").read_text(encoding="utf-8")
        self.assertIn("Validated (sample)", html)
        self.assertIn("Accepted (sample)", html)
        self.assertIn("Realized effects (sample)", html)
        self.assertIn("out.skipped", html)
        self.assertIn("out.failed", html)


if __name__ == "__main__":
    unittest.main()
