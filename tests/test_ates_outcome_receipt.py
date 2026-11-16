"""Tests for provenance-only ATES outcome receipt classification."""
import unittest

from scripts.ci.ates_outcome_receipt import build_outcome_receipt


class OutcomeReceiptTests(unittest.TestCase):
    def base(self, **overrides):
        values = {
            "source_run_id": 123,
            "source_run_attempt": 2,
            "source_head_sha": "a" * 40,
            "source_workflow_name": "agent lane",
            "source_conclusion": "failure",
            "skip_reason": "metadata_unavailable",
            "collection_outcome": "success",
            "checkout_outcome": "success",
            "task_boundary_outcome": "success",
            "observed_at": "2026-11-07T00:00:00+00:00",
        }
        values.update(overrides)
        return build_outcome_receipt(**values)

    def test_failed_source_gets_provenance_only_receipt(self):
        receipt = self.base()
        self.assertEqual(receipt["status"], "source_non_success")
        self.assertEqual(receipt["skip_reason"], "source_conclusion_failure")
        self.assertEqual(receipt["source_run_id"], 123)
        self.assertEqual(receipt["source_run_attempt"], 2)
        self.assertEqual(receipt["source_head_sha"], "a" * 40)
        self.assertFalse(receipt["metrics_emitted"])
        self.assertNotIn("ates", receipt)

    def test_cancelled_source_is_not_misreported_as_collector_failure(self):
        receipt = self.base(source_conclusion="cancelled")
        self.assertEqual(receipt["status"], "source_non_success")
        self.assertEqual(receipt["skip_reason"], "source_conclusion_cancelled")

    def test_unknown_conclusion_is_preserved_as_unknown(self):
        receipt = self.base(source_conclusion=None)
        self.assertEqual(receipt["source_conclusion"], "unknown")
        self.assertEqual(receipt["status"], "source_non_success")

    def test_successful_source_rate_limit_is_deferred(self):
        receipt = self.base(source_conclusion="success", skip_reason="rate_limited")
        self.assertEqual(receipt["status"], "deferred")
        self.assertEqual(receipt["skip_reason"], "rate_limited")

    def test_collector_failure_is_failed(self):
        receipt = self.base(source_conclusion="success", collection_outcome="failure")
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(receipt["skip_reason"], "collection_failed")

    def test_unmapped_success_is_skipped_without_guessing(self):
        receipt = self.base(source_conclusion="success", skip_reason="unmapped_workflow")
        self.assertEqual(receipt["status"], "skipped")
        self.assertEqual(receipt["skip_reason"], "unmapped_workflow")

    def test_non_success_source_takes_precedence_over_observer_failure(self):
        receipt = self.base(source_conclusion="cancelled", collection_outcome="failure")
        self.assertEqual(receipt["status"], "source_non_success")

    def test_invalid_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            self.base(source_run_id=True)
        with self.assertRaises(ValueError):
            self.base(source_run_attempt=0)


if __name__ == "__main__":
    unittest.main()
