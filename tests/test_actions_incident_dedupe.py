"""Tests for idempotent Actions incident notification reconciliation."""
import unittest
from pathlib import Path

from scripts.ci.actions_incident_dedupe import reconcile_incident


class ActionsIncidentDedupeTests(unittest.TestCase):
    def test_watcher_is_dispatch_only_after_spam_reduction(self):
        workflow = Path(".github/workflows/actions-run-watcher.yml").read_text(encoding="utf-8")
        # workflow_run trigger removed to eliminate skip-run listing spam.
        self.assertNotIn("workflow_run:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("group: actions-run-watcher-manual", workflow)
        self.assertIn("if: github.event_name == 'workflow_dispatch'", workflow)

    def test_cadence_emits_lag_failure_incidents(self):
        cadence = Path(".github/workflows/cadence-lead-lag.yml").read_text(encoding="utf-8")
        self.assertIn("Emit incidents for lag_failure", cadence)
        self.assertIn("gh issue create", cadence)
        # Scheduled cadence ownership moved to quota-dispatch-tree.yml under #1573.
        # This workflow remains manually dispatchable and must not reintroduce a duplicate cron.
        self.assertIn("workflow_dispatch:", cadence)
        self.assertIn("Cadence owned by quota-dispatch-tree.yml", cadence)
        self.assertNotIn("cron:", cadence)

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

    def test_body_delivery_marker_does_not_access_comments(self):
        class BodyMarkerIssue(dict):
            def get(self, key, default=None):
                if key == "comments":
                    raise AssertionError("comments should not be accessed")
                return super().get(key, default)

        result = reconcile_incident(
            BodyMarkerIssue(body="<!-- actions-notified:fp -->"),
            fingerprint="fp",
            run_id="103a",
            run_attempt="1",
            run_url="https://github.com/example/repo/actions/runs/103a",
        )
        self.assertFalse(result["notify"])

    def test_comment_marker_stops_before_converting_later_bodies(self):
        class ExplodingBody:
            def __str__(self):
                raise AssertionError("later comment body should not be converted")

        result = reconcile_incident(
            {
                "body": "Incident body",
                "comments": [
                    {"body": "<!-- actions-notified:fp -->"},
                    {"body": ExplodingBody()},
                ],
            },
            fingerprint="fp",
            run_id="103b",
            run_attempt="1",
            run_url="https://github.com/example/repo/actions/runs/103b",
        )
        self.assertFalse(result["notify"])

    def test_malformed_and_non_list_comments_preserve_notify_behavior(self):
        for comments in ("<!-- actions-notified:fp -->", [None, "text", {}]):
            with self.subTest(comments=comments):
                result = reconcile_incident(
                    {"body": "Incident body", "comments": comments},
                    fingerprint="fp",
                    run_id="103c",
                    run_attempt="1",
                    run_url="https://github.com/example/repo/actions/runs/103c",
                )
                self.assertTrue(result["notify"])

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
