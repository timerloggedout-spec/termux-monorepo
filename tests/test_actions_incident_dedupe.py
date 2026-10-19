"""Tests for idempotent Actions incident notification reconciliation."""
import unittest
from pathlib import Path

from scripts.ci.actions_incident_dedupe import reconcile_incident


class ActionsIncidentDedupeTests(unittest.TestCase):
    def test_watcher_serializes_incident_updates_and_checks_out_helper(self):
        workflow = Path(".github/workflows/actions-run-watcher.yml").read_text(encoding="utf-8")
        self.assertIn("queue: max", workflow)
        self.assertIn("group: actions-run-watcher-${{ github.event.workflow_run.name }}-${{ github.event.workflow_run.conclusion }}", workflow)
        self.assertIn("Checkout observer implementation", workflow)
        self.assertIn("--json number,title", workflow)
        self.assertIn('--search "in:title', workflow)
        self.assertIn("--limit 1000", workflow)
        self.assertIn("actions-notified:${fp}", workflow)

    def test_first_fingerprint_requests_notification_and_records_run(self):
        result = reconcile_incident(
            {"body": "Initial incident"},
            fingerprint="gha:observer:failure:abcdef012345",
            run_id="100",
            run_attempt="1",
            run_url="https://github.com/example/repo/actions/runs/100",
        )
        self.assertTrue(result["notify"])
        self.assertIn("actions-run:100:1", result["body"])
        self.assertIn("gha:observer:failure:abcdef012345", result["body"])

    def test_body_fingerprint_without_delivery_marker_retries_notification(self):
        existing = {
            "body": "Fingerprint: gha:observer:failure:abcdef012345",
            "comments": [],
        }
        result = reconcile_incident(
            existing,
            fingerprint="gha:observer:failure:abcdef012345",
            run_id="101",
            run_attempt="1",
            run_url="https://github.com/example/repo/actions/runs/101",
        )
        self.assertTrue(result["notify"])
        self.assertIn("actions-run:101:1", result["body"])
        self.assertIn("/runs/101", result["body"])

    def test_new_fingerprint_notifies_on_existing_incident(self):
        result = reconcile_incident(
            {"body": "Fingerprint: gha:observer:failure:oldsha123456"},
            fingerprint="gha:observer:failure:newsha123456",
            run_id="102",
            run_attempt="1",
            run_url="https://github.com/example/repo/actions/runs/102",
        )
        self.assertTrue(result["notify"])

    def test_existing_comment_fingerprint_also_deduplicates(self):
        result = reconcile_incident(
            {
                "body": "Incident body",
                "comments": [{"body": "Fingerprint gha:observer:failure:abcdef012345 <!-- actions-notified:gha:observer:failure:abcdef012345 -->"}],
            },
            fingerprint="gha:observer:failure:abcdef012345",
            run_id="103",
            run_attempt="2",
            run_url="https://github.com/example/repo/actions/runs/103",
        )
        self.assertFalse(result["notify"])
        self.assertIn("actions-run:103:2", result["body"])

    def test_reprocessing_same_run_does_not_duplicate_run_link(self):
        first = reconcile_incident(
            {},
            fingerprint="gha:observer:failure:abcdef012345",
            run_id="104",
            run_attempt="1",
            run_url="https://github.com/example/repo/actions/runs/104",
        )
        second = reconcile_incident(
            {"body": first["body"]},
            fingerprint="gha:observer:failure:abcdef012345",
            run_id="104",
            run_attempt="1",
            run_url="https://github.com/example/repo/actions/runs/104",
        )
        self.assertTrue(second["run_already_recorded"])
        self.assertEqual(second["body"].count("/runs/104"), 1)


if __name__ == "__main__":
    unittest.main()
