import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ops" / "admin_graph_runtime_event.py"
SPEC = importlib.util.spec_from_file_location("admin_graph_runtime_event", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class RuntimeEventTests(unittest.TestCase):
    def test_workflow_run_event_is_normalized(self):
        payload = {
            "repository": {"full_name": MODULE.REPO},
            "sender": {"login": "automation"},
            "workflow_run": {
                "id": 123, "run_attempt": 2, "name": "tribute execute",
                "status": "completed", "conclusion": "success",
                "updated_at": "2026-11-16T12:00:00Z",
                "head_sha": "a" * 40, "html_url": "https://github.com/example/run/123"
            }
        }
        event = MODULE.build_event(payload, "workflow_run")
        self.assertEqual(event["event"], "workflow_success")
        self.assertEqual(event["run_id"], 123)
        self.assertEqual(event["run_attempt"], 2)
        self.assertEqual(event["repo"], MODULE.REPO)
        self.assertTrue(event["id"].startswith("workflow:123:2:success:"))
        self.assertNotIn("logs", event)

    def test_workflow_job_event_is_normalized(self):
        payload = {
            "repository": {"full_name": MODULE.REPO},
            "workflow": {"name": "tribute execute"},
            "sender": {"login": "automation"},
            "workflow_job": {
                "id": 456, "run_id": 123, "run_attempt": 1,
                "name": "execute task", "status": "in_progress",
                "started_at": "2026-11-16T12:01:00Z",
                "head_sha": "b" * 40,
                "html_url": "https://github.com/example/job/456"
            }
        }
        event = MODULE.build_event(payload, "workflow_job")
        self.assertEqual(event["event"], "job_in_progress")
        self.assertEqual(event["kind"], "job")
        self.assertEqual(event["job_id"], 456)
        self.assertEqual(event["workflow"], "tribute execute")

    def test_workflow_snapshot_builds_run_events(self):
        payload = {"workflow_runs": [
            {"id": 123, "run_attempt": 1, "name": "tribute execute", "status": "in_progress", "created_at": "2026-11-16T12:00:00Z"},
            {"id": 124, "run_attempt": 2, "name": "n8n SHE bridge", "status": "completed", "conclusion": "failure", "updated_at": "2026-11-16T12:01:00Z"}
        ]}
        events = MODULE.build_events(payload, "workflow_snapshot")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event"], "workflow_in_progress")
        self.assertEqual(events[1]["event"], "workflow_failure")
        self.assertTrue(all(event["repo"] == MODULE.REPO for event in events))

    def test_unsupported_event_is_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.build_event({}, "push")

    def test_repository_is_preserved_for_worker_validation(self):
        payload = {
            "repository": {"full_name": "attacker/other"},
            "workflow_run": {"id": 1, "status": "in_progress"}
        }
        event = MODULE.build_event(payload, "workflow_run")
        self.assertEqual(event["repo"], "attacker/other")

if __name__ == "__main__":
    unittest.main()
