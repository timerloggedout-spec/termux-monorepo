from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest import TestCase, main


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "ci" / "repository_development_evaluation.py"
SPEC = importlib.util.spec_from_file_location("repository_development_evaluation", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)


def raw_evidence(**overrides):
    base = {
        "subject_type": "pull-request",
        "subject_key": "pr-192",
        "source_revision": "6b9812b93f449ed4c27ed47e2b33aef1e9de4a91",
        "adapter": "repository-pr-lifecycle",
        "collected_at": "2026-08-18T12:10:00Z",
        "lifecycle": {
            "state": "open",
            "opened_at": "2026-08-18T12:00:00Z",
            "updated_at": "2026-08-18T12:05:00Z",
            "closed_at": None,
            "merged_at": None,
        },
        "metrics": {
            "commit_count": 2,
            "changed_file_count": 3,
            "additions": 20,
            "deletions": 5,
            "review_count": 1,
            "unresolved_thread_count": 0,
            "check_success_count": 2,
            "check_failure_count": 0,
            "check_cancelled_count": 0,
            "check_pending_count": 0,
            "automation_marker_count": 1,
            "first_automation_response_at": "2026-08-18T12:03:00Z",
        },
    }
    base.update(overrides)
    return base


class RepositoryDevelopmentEvaluationTests(TestCase):
    def test_valid_raw_evidence_builds_auditable_manifest(self):
        payload = CONTRACT.build(raw_evidence())
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(len(payload["result_digest"]), 64)
        CONTRACT.validate(payload)

    def test_unknown_raw_field_is_rejected(self):
        with self.assertRaisesRegex(CONTRACT.ContractError, "unknown"):
            CONTRACT.build(raw_evidence(review_body="untrusted content"))

    def test_secret_shaped_content_is_rejected(self):
        raw = raw_evidence(subject_key="pr-192-ghp_abcdefghijklm")
        with self.assertRaisesRegex(CONTRACT.ContractError, "credential"):
            CONTRACT.build(raw)

    def test_open_lifecycle_rejects_close_timestamp(self):
        raw = raw_evidence(lifecycle={
            "state": "open",
            "opened_at": "2026-08-18T12:00:00Z",
            "updated_at": "2026-08-18T12:05:00Z",
            "closed_at": "2026-08-18T12:06:00Z",
            "merged_at": None,
        })
        with self.assertRaisesRegex(CONTRACT.ContractError, "open lifecycle"):
            CONTRACT.build(raw)

    def test_empty_check_state_is_rejected(self):
        raw = raw_evidence(metrics={
            **raw_evidence()["metrics"],
            "check_success_count": 0,
        })
        with self.assertRaisesRegex(CONTRACT.ContractError, "at least one check"):
            CONTRACT.build(raw)

    def test_first_response_cannot_precede_opening(self):
        raw = raw_evidence(metrics={
            **raw_evidence()["metrics"],
            "first_automation_response_at": "2026-08-18T11:59:59Z",
        })
        with self.assertRaisesRegex(CONTRACT.ContractError, "precedes"):
            CONTRACT.build(raw)


if __name__ == "__main__":
    main()
