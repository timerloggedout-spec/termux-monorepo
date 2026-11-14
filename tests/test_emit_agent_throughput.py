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
                "name": "Gemini Dispatch (test)",
                "event": "workflow_dispatch",
                "html_url": "https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/12345",
            },
            "jobs": [{
                "id": 99,
                "name": "agent",
                "started_at": "2026-09-25T18:01:00Z",
                "completed_at": "2026-09-25T18:03:30Z",
                "conclusion": "success",
            }],
            "pull_request_number": 1244,
            "issue_number": 1241,
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
        self.assertEqual(events[-1]["workflow_name"], "Gemini Dispatch (test)")
        self.assertEqual(events[-1]["workflow_event"], "workflow_dispatch")
        self.assertEqual(events[-1]["workflow_run_url"], "https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/12345")
        self.assertEqual(events[-1]["job_id"], 99)
        self.assertEqual(events[-1]["job_name"], "agent")
        self.assertEqual(events[-1]["pull_request_number"], 1244)
        self.assertEqual(events[-1]["issue_number"], 1241)
        self.assertTrue(events[-1]["event_id"])

    def test_task_boundary_fields_are_propagated_without_raw_task_text(self):
        data = self.metadata()
        data["task_boundary"] = {
            "cohort_id": "repair-v1",
            "task_fingerprint": "b" * 64,
            "task_contract_hash": "c" * 64,
            "environment_fingerprint": "d" * 64,
        }
        events = build_events(data)
        for event in events:
            self.assertEqual(event["cohort_id"], "repair-v1")
            self.assertEqual(event["task_fingerprint"], "b" * 64)
            self.assertEqual(event["task_contract_hash"], "c" * 64)
            self.assertEqual(event["environment_fingerprint"], "d" * 64)
            self.assertNotIn("task_text", event)

    def test_author_provenance_is_explicit_and_model_can_remain_unknown(self):
        data = self.metadata()
        data["author"] = {
            "provider": "google",
            "model": None,
            "adapter": "github-actions",
            "role": "specialist",
            "identity_kind": "agent",
            "settings_fingerprint": "e" * 64,
            "context_fingerprint": "f" * 64,
            "attribution_method": "workflow_name_mapping",
            "confidence": 0.8,
            "evidence_refs": ["workflow_run:12345", "workflow_name:Gemini Dispatch"],
        }
        data["github_actor"] = "timerloggedout-spec"
        data["triggering_actor"] = "timerloggedout-spec"
        events = build_events(data)
        for event in events:
            self.assertEqual(event["author"]["provider"], "google")
            self.assertIsNone(event["author"]["model"])
            self.assertEqual(event["author"]["settings_fingerprint"], "e" * 64)
            self.assertEqual(event["author"]["context_fingerprint"], "f" * 64)
            self.assertEqual(event["github_actor"], "timerloggedout-spec")
            self.assertNotIn("prompt", event)
            validate_event(event)

    def test_author_rejects_raw_settings_and_invalid_fingerprints(self):
        data = self.metadata()
        data["author"] = {
            "settings": "must not be stored",
            "identity_kind": "agent",
            "attribution_method": "workflow_name_mapping",
            "confidence": 0.8,
        }
        with self.assertRaises(ValueError):
            build_events(data)
        data["author"] = {
            "settings_fingerprint": "not-a-sha256",
            "identity_kind": "agent",
            "attribution_method": "workflow_name_mapping",
            "confidence": 0.8,
        }
        with self.assertRaises(ValueError):
            build_events(data)

    def test_missing_author_is_explicitly_unresolved(self):
        events = build_events(self.metadata())
        self.assertEqual(events[0]["author"]["identity_kind"], "unknown")
        self.assertEqual(events[0]["author"]["attribution_method"], "unresolved")
        self.assertEqual(events[0]["author"]["confidence"], 0.0)
        self.assertIsNone(events[0]["author"]["model"])

    def test_missing_complexity_stays_missing(self):
        events = build_events(self.metadata(task_complexity=None))
        self.assertNotIn("metrics", events[-1])

    def test_skipped_jobs_do_not_become_fake_completed_tasks(self):
        data = self.metadata()
        data["jobs"][0]["conclusion"] = "skipped"
        self.assertEqual(build_events(data), [])

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


    def test_missing_execution_is_explicitly_unknown(self):
        events = build_events(self.metadata())
        expected = {
            "controller": "unknown",
            "surface": "unknown",
            "route": "unknown",
            "session_ref": None,
            "adapter_version": None,
            "attribution_method": "unresolved",
            "confidence": 0.0,
            "evidence_refs": [],
        }
        for event in events:
            self.assertEqual(event["execution"], expected)

    def test_que_execution_requires_repo_owned_adapter_and_session_evidence(self):
        data = self.metadata()
        data["execution"] = {
            "controller": "que",
            "surface": "repo_owned_adapter",
            "route": "api",
            "session_ref": "session:que:12345",
            "adapter_version": "amd-academy/0.1.0",
            "attribution_method": "invocation_telemetry",
            "confidence": 1.0,
            "evidence_refs": ["workflow_run:12345", "workflow_job:99"],
        }
        events = build_events(data)
        for event in events:
            self.assertEqual(event["execution"]["controller"], "que")
            self.assertEqual(event["execution"]["surface"], "repo_owned_adapter")
            self.assertEqual(event["execution"]["route"], "api")
            validate_event(event)

    def test_que_cannot_claim_external_computer_or_seat_browser_execution(self):
        data = self.metadata()
        data["execution"] = {
            "controller": "que",
            "surface": "seat_browser",
            "route": "seat_browser",
            "session_ref": "session:que:123",
            "adapter_version": "external/1",
            "attribution_method": "session_export",
            "confidence": 1.0,
            "evidence_refs": ["session:123"],
        }
        with self.assertRaisesRegex(ValueError, "QUE execution requires repo_owned_adapter"):
            build_events(data)

    def test_que_execution_without_session_or_evidence_is_rejected(self):
        data = self.metadata()
        data["execution"] = {
            "controller": "que",
            "surface": "repo_owned_adapter",
            "route": "mcp",
            "session_ref": None,
            "adapter_version": "amd-academy/0.1.0",
            "attribution_method": "workflow_name_mapping",
            "confidence": 0.0,
            "evidence_refs": [],
        }
        with self.assertRaises(ValueError):
            build_events(data)

    def test_muse_external_computer_execution_stays_attributed_to_muse(self):
        data = self.metadata()
        data["execution"] = {
            "controller": "muse",
            "surface": "external_computer",
            "route": "seat_browser",
            "session_ref": "session:muse:123",
            "adapter_version": None,
            "attribution_method": "session_export",
            "confidence": 0.9,
            "evidence_refs": ["session_export:123"],
        }
        events = build_events(data)
        for event in events:
            self.assertEqual(event["execution"]["controller"], "muse")
            self.assertEqual(event["execution"]["surface"], "external_computer")
            self.assertNotEqual(event["execution"]["controller"], "que")

    def test_execution_provenance_rejects_raw_session_material(self):
        data = self.metadata()
        data["execution"] = {
            "controller": "que",
            "surface": "repo_owned_adapter",
            "route": "cli",
            "session_ref": "session:que:123",
            "adapter_version": "amd-academy/0.1.0",
            "attribution_method": "invocation_telemetry",
            "confidence": 1.0,
            "evidence_refs": ["workflow_run:12345"],
            "session_text": "raw browser/session contents must never be stored",
        }
        with self.assertRaisesRegex(ValueError, "unsupported execution fields"):
            build_events(data)


    def test_execution_provenance_rejects_token_bearing_session_reference(self):
        data = self.metadata()
        data["execution"] = {
            "controller": "que",
            "surface": "repo_owned_adapter",
            "route": "api",
            "session_ref": "session:que:123?token=do-not-store",
            "adapter_version": "amd-academy/0.1.0",
            "attribution_method": "invocation_telemetry",
            "confidence": 1.0,
            "evidence_refs": ["workflow_run:12345"],
        }
        with self.assertRaisesRegex(ValueError, "opaque session"):
            build_events(data)

    def test_execution_provenance_rejects_unstructured_controller_identity(self):
        data = self.metadata()
        data["execution"] = {
            "controller": "que operator",
            "surface": "repo_owned_adapter",
            "route": "api",
            "session_ref": "session:que:123",
            "adapter_version": "amd-academy/0.1.0",
            "attribution_method": "invocation_telemetry",
            "confidence": 1.0,
            "evidence_refs": ["workflow_run:12345"],
        }
        with self.assertRaisesRegex(ValueError, "safe lowercase identity"):
            build_events(data)

    def test_execution_provenance_rejects_boolean_confidence(self):
        data = self.metadata()
        data["execution"] = {
            "controller": "que",
            "surface": "repo_owned_adapter",
            "route": "api",
            "session_ref": "session:que:123",
            "adapter_version": "amd-academy/0.1.0",
            "attribution_method": "invocation_telemetry",
            "confidence": True,
            "evidence_refs": ["workflow_run:12345"],
        }
        with self.assertRaisesRegex(ValueError, "not a boolean"):
            build_events(data)

def test_execution_controller_is_not_inferred_from_author_or_github_actor():
    payload = {
        "agent_id": "gemini",
        "workflow_run": {
            "id": 12345, "run_attempt": 1, "head_sha": "a" * 40,
            "created_at": "2026-09-25T18:00:00Z", "conclusion": "success",
            "name": "Gemini Dispatch", "event": "workflow_dispatch",
        },
        "jobs": [{
            "id": 99, "name": "agent",
            "started_at": "2026-09-25T18:01:00Z",
            "completed_at": "2026-09-25T18:03:30Z", "conclusion": "success",
        }],
        "author": {"provider": "google", "identity_kind": "agent",
                   "attribution_method": "workflow_name_mapping", "confidence": 0.8},
        "github_actor": "que",
    }
    events = build_events(payload)
    assert events
    assert all(event["execution"]["controller"] == "unknown" for event in events)


if __name__ == "__main__":
    unittest.main()
