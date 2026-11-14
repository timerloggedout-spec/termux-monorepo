import json
import tempfile
import unittest
from pathlib import Path

from scripts.ci.write_agent_task_boundary import build_record


class TaskBoundaryTests(unittest.TestCase):
    def test_record_contains_hashes_not_raw_task_text(self):
        record = build_record({
            "agent_id": "gemini",
            "task_kind": "invoke",
            "target_kind": "pull_request",
            "target_number": "871",
            "repository": "timerloggedout-spec/termux-monorepo",
            "base_sha": "a" * 40,
            "task_text": "do not leak this prompt",
            "runner_os": "Linux",
            "runner_image": "ubuntu",
            "workflow": "invoke",
            "provider": "gemini",
            "model": "gemini-test",
        })
        serialized = json.dumps(record)
        self.assertNotIn("do not leak this prompt", serialized)
        self.assertEqual(len(record["task_fingerprint"]), 64)
        self.assertEqual(len(record["task_contract_hash"]), 64)
        self.assertEqual(len(record["environment_fingerprint"]), 64)

    def test_empty_task_text_remains_missing_not_empty_content(self):
        record = build_record({
            "agent_id": "deepseek",
            "task_kind": "issue",
            "repository": "timerloggedout-spec/termux-monorepo",
            "base_sha": "b" * 40,
        })
        self.assertEqual(len(record["task_fingerprint"]), 64)
        self.assertNotIn("task_text", record)
        self.assertNotIn("task_text_sha256", record)

    def test_cohort_is_optional(self):
        record = build_record({
            "agent_id": "gemini",
            "task_kind": "review",
            "repository": "timerloggedout-spec/termux-monorepo",
            "base_sha": "c" * 40,
            "cohort_id": "repair-v1",
        })
        self.assertEqual(record["cohort_id"], "repair-v1")


    def test_execution_provenance_is_carried_as_a_sanitized_boundary(self):
        record = build_record({
            "agent_id": "muse",
            "task_kind": "academy",
            "repository": "timerloggedout-spec/termux-monorepo",
            "base_sha": "d" * 40,
            "execution": {
                "controller": "muse",
                "surface": "external_computer",
                "route": "seat_browser",
                "session_ref": "opaque-session:muse:123",
                "adapter_version": None,
                "attribution_method": "session_export",
                "confidence": 0.9,
                "evidence_refs": ["session_export:123"],
                "session_text": "must not be persisted",
            },
        })
        serialized = json.dumps(record)
        self.assertNotIn("must not be persisted", serialized)
        self.assertNotIn("session_text", serialized)
        self.assertEqual(record["execution"]["controller"], "muse")
        self.assertEqual(record["execution"]["surface"], "external_computer")

    def test_execution_provenance_is_validated_before_artifact_write(self):
        with self.assertRaisesRegex(ValueError, "unsupported execution fields"):
            build_record({
                "agent_id": "que",
                "task_kind": "academy",
                "repository": "timerloggedout-spec/termux-monorepo",
                "base_sha": "e" * 40,
                "execution": {
                    "controller": "que",
                    "surface": "repo_owned_adapter",
                    "route": "api",
                    "session_ref": "opaque-session:que:123",
                    "adapter_version": "amd-academy/0.1.0",
                    "attribution_method": "invocation_telemetry",
                    "confidence": 1.0,
                    "evidence_refs": ["workflow_run:123"],
                    "session_text": "raw material",
                },
            })


if __name__ == "__main__":
    unittest.main()
