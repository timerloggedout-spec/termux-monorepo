import unittest

from scripts.ci.emit_ates_run_receipt import build_event


class EmitAcesRunReceiptTests(unittest.TestCase):
    def test_success_receipt_is_sanitized_and_linked(self):
        event = build_event({
            "workflow_run": {
                "id": 1234,
                "run_attempt": 2,
                "name": "Continuous agent ops",
                "conclusion": "success",
                "head_sha": "a" * 40,
                "created_at": "2026-10-20T10:00:00Z",
                "updated_at": "2026-10-20T10:01:30Z",
                "html_url": "https://example.invalid/private-run",
                "head_commit": {"message": "do not copy this"},
            }
        })
        self.assertEqual(event["event"], "task_completed")
        self.assertEqual(event["status"], "success")
        self.assertEqual(event["gha_run_id"], 1234)
        self.assertEqual(event["gha_run_attempt"], 2)
        self.assertEqual(event["duration_ms"], 90000.0)
        self.assertEqual(event["source_sha"], "a" * 40)
        self.assertNotIn("html_url", event)
        self.assertNotIn("head_commit", event)

    def test_missing_duration_stays_missing(self):
        event = build_event({
            "workflow_run": {
                "id": 1234,
                "run_attempt": 1,
                "name": "agent",
                "conclusion": "cancelled",
                "head_sha": "b" * 40,
                "created_at": "2026-10-20T10:00:00Z",
                "updated_at": None,
            }
        })
        self.assertEqual(event["status"], "skipped")
        self.assertNotIn("duration_ms", event)


if __name__ == "__main__":
    unittest.main()
