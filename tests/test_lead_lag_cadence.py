"""Regression tests for the bounded Lead/Lag observer."""
import sys
import unittest
from unittest.mock import patch

from scripts.ops.lead_lag_cadence import classify_conclusion, classify_runs, is_dual_gate, main


class LeadLagCadenceTests(unittest.TestCase):
    def test_success_badge_is_not_task_pass(self):
        self.assertEqual(classify_conclusion("success", "completed"), "lag_success_badge")

    def test_skipped_and_cancelled_are_operational_not_model_failures(self):
        for conclusion in ("skipped", "cancelled", "neutral", "startup_failure"):
            with self.subTest(conclusion=conclusion):
                self.assertEqual(classify_conclusion(conclusion, "completed"), "lag_operational")

    def test_in_flight_precedes_empty_conclusion(self):
        self.assertEqual(classify_conclusion(None, "queued"), "lead_in_flight")

    def test_dual_gate_marker_is_diagnostic_only(self):
        self.assertTrue(is_dual_gate("repo gate"))
        self.assertTrue(is_dual_gate("agentic termux smoke"))
        report = classify_runs([{
            "name": "repo gate",
            "conclusion": "success",
            "status": "completed",
            "head_sha": "0123456789abcdef",
        }])
        self.assertEqual(report["verdict"], "PASS_BADGE_PLANE")
        self.assertNotIn("task_pass", report)
        self.assertEqual(report["dual_gate_runs"][0]["head_sha"], "0123456789ab")

    def test_sample_limit_outside_api_bounds_is_rejected_before_network(self):
        with patch.object(sys, "argv", ["lead_lag_cadence.py", "--per-page", "101"]):
            with self.assertRaises(SystemExit) as caught:
                main()
        self.assertEqual(caught.exception.code, 2)

    def test_failure_is_preserved_as_failure(self):
        report = classify_runs([{
            "name": "test suite",
            "conclusion": "failure",
            "status": "completed",
            "head_sha": "deadbeef",
        }])
        self.assertEqual(report["verdict"], "FAIL_NEEDS_REPAIR")
        self.assertEqual(report["counts"]["lag_failure"], 1)
        self.assertEqual(report["failures"][0]["class"], "lag_failure")


if __name__ == "__main__":
    unittest.main()
