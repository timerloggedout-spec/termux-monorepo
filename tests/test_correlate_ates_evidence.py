import unittest

from scripts.ci.correlate_ates_evidence import correlate


SHA = "a" * 40
SHA_B = "b" * 40


def receipt(run_id=101, attempt=1, sha=SHA):
    return {
        "timestamp": "2026-10-21T10:01:00Z",
        "event": "task_completed",
        "agent_id": "Continuous agent ops",
        "task_id": f"gha:{run_id}:attempt:{attempt}",
        "status": "success",
        "gha_run_id": run_id,
        "gha_run_attempt": attempt,
        "source_sha": sha,
        "duration_ms": 60000,
    }


def event(kind="tool_call", run_id=101, attempt=1, sha=SHA, status="success"):
    return {
        "timestamp": "2026-10-21T10:00:30Z",
        "event": kind,
        "task_id": "ates-task:" + "c" * 64,
        "status": status,
        "gha_run_id": run_id,
        "gha_run_attempt": attempt,
        "source_sha": sha,
    }


class AtesCorrelationTests(unittest.TestCase):
    def test_joins_on_run_and_attempt_and_summarizes_allowlisted_counts(self):
        result = correlate(
            [receipt()],
            [event(), event("task_completed"), event("tool_retry", status="error")],
        )
        self.assertEqual(result["matched_event_count"], 3)
        self.assertEqual(result["unmatched_event_count"], 0)
        run = result["runs"][0]
        self.assertEqual(run["event_count"], 3)
        self.assertEqual(run["tool_call_count"], 1)
        self.assertEqual(run["task_completed_count"], 1)
        self.assertEqual(run["tool_retry_count"], 1)
        self.assertEqual(run["sha_verification"], "verified")

    def test_does_not_cross_join_attempts_or_runs(self):
        result = correlate([receipt()], [event(attempt=2), event(run_id=102)])
        self.assertEqual(result["matched_event_count"], 0)
        self.assertEqual(result["unmatched_event_count"], 2)
        self.assertEqual(result["runs"][0]["event_count"], 0)

    def test_quarantines_sha_mismatch_instead_of_joining(self):
        result = correlate([receipt()], [event(sha=SHA_B)])
        self.assertEqual(result["sha_mismatch_event_count"], 1)
        self.assertEqual(result["matched_event_count"], 0)
        self.assertEqual(result["runs"][0]["event_count"], 0)

    def test_missing_event_sha_is_joined_but_verification_is_not_overstated(self):
        result = correlate([receipt()], [event(sha=None)])
        self.assertEqual(result["matched_event_count"], 1)
        self.assertEqual(result["runs"][0]["sha_verification"], "unverified")
        self.assertEqual(result["runs"][0]["sha_unverified_event_count"], 1)


    def test_invalid_event_sha_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "event source_sha"):
            correlate([receipt()], [event(sha="bad")])

    def test_duplicate_receipt_identity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate receipt"):
            correlate([receipt(), receipt()], [])

    def test_missing_run_linkage_stays_unmatched(self):
        row = event()
        row.pop("gha_run_id")
        result = correlate([receipt()], [row])
        self.assertEqual(result["unmatched_event_count"], 1)
        self.assertEqual(result["matched_event_count"], 0)


if __name__ == "__main__":
    unittest.main()
