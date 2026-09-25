import json
import tempfile
import unittest
from pathlib import Path

from scripts.ci.emit_agent_throughput import build_events, validate_event, write_events


class AgentThroughputEmitterTests(unittest.TestCase):
    def metadata(self, **overrides):
        payload = {
            "agent_id": "gemini",
            "workflow_run": {
                "id": 12345,
                "run_attempt": 2,
                "head_sha": "a" * 40,
                "created_at": "2026-09-25T18:00:00Z",
                "conclusion": "success",
            },
            "jobs": [{
                "id": 99,
                "name": "agent",
                "started_at": "2026-09-25T18:01:00Z",
                "completed_at": "2026-09-25T18:03:30Z",
                "conclusion": "success",
            }],
            "task_complexity": {
                "additions": 12,
                "deletions": 3,
                "files_changed": 2,
            },
        }
        payload.update(overrides)
        return payload

    def test_emits_start_active_and_completion_with_provenance(self):
        events = build_events(self.metadata())
        self.assertEqual([e["event"] for e in events], [
            "task_started", "active_window", "task_completed",
        ])
        self.assertEqual(events[-1]["status"], "success")
        self.assertEqual(events[-1]["metrics"]["files_changed"], 2)
        self.assertEqual(events[-1]["gha_run_attempt"], 2)
        self.assertEqual(events[-1]["source_sha"], "a" * 40)
        self.assertTrue(events[-1]["event_id"])

    def test_missing_complexity_stays_missing(self):
        events = build_events(self.metadata(task_complexity=None))
        self.assertNotIn("metrics", events[-1])

    def test_missing_job_timing_does_not_fabricate_duration(self):
        data = self.metadata()
        data["jobs"][0]["started_at"] = None
        self.assertEqual(build_events(data), [])

    def test_failed_job_is_observed_as_failed_task(self):
        data = self.metadata()
        data["jobs"][0]["conclusion"] = "failure"
        events = build_events(data)
        self.assertEqual(events[-1]["status"], "failed")

    def test_unknown_fields_are_rejected(self):
        event = build_events(self.metadata())[0]
        event["prompt"] = "must never enter evidence"
        with self.assertRaises(ValueError):
            validate_event(event)

    def test_jsonl_is_deterministic_and_validated(self):
        events = build_events(self.metadata())
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "events.ndjson"
            write_events(events, output)
            rows = [json.loads(line) for line in output.read_text().splitlines()]
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1]["active_seconds"], 150.0)
        self.assertTrue(all("prompt" not in row for row in rows))


if __name__ == "__main__":
    unittest.main()
