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


if __name__ == "__main__":
    unittest.main()
