from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "agentic"))

from dependency_phase_engine import plan_digest  # noqa: E402
from dependency_phases import CommandError, dispatch_claim, live_snapshot  # noqa: E402


def plan_fixture() -> dict:
    return {
        "schema_version": 1,
        "plan_id": "fixture-plan",
        "title": "Fixture dependency plan",
        "base_branch": "master-staging",
        "project": {
            "owner": "example-owner",
            "number": 1,
            "id": "PVT_fixture",
            "url": "https://github.com/users/example-owner/projects/1",
            "status_field_id": "PVTSSF_fixture",
            "status_options": {"Todo": "todo", "In progress": "progress", "Done": "done"},
        },
        "policy": {"dispatch_agents": ["jules"]},
        "phases": [
            {
                "phase_id": "DPH-100",
                "title": "Dependent work",
                "description": "Dependent lifecycle implementation.",
                "depends_on": [],
                "project": {"title_marker": "DPH-100"},
                "approval_required": False,
                "execution": {"mode": "agent", "preferred_agent": "jules"},
                "completion": {"required_checks": ["repo-gate"], "merged_pr": True},
            }
        ],
    }


def canonical_issue() -> dict:
    return {
        "number": 12,
        "title": "[DPH-100] Dependent work",
        "body": "**Plan:** `fixture-plan`\n**Phase:** `DPH-100`",
        "url": "https://github.com/example/repo/issues/12",
    }


class DependencyPhaseCliTests(unittest.TestCase):
    def test_live_snapshot_normalizes_claim_comments_from_canonical_issue(self) -> None:
        plan = plan_fixture()
        digest = plan_digest(plan)
        with (
            patch("dependency_phases.issues", return_value=[canonical_issue()]),
            patch("dependency_phases.issue_comments", return_value=[
                {"id": 7, "body": f"<!-- dependency-phase-claim: DPH-100:{digest} -->"}
            ]),
            patch("dependency_phases.project_items", return_value=[]),
            patch("dependency_phases.pull_requests", return_value=[]),
        ):
            snapshot = live_snapshot(plan, "example/repo", ROOT / "missing-approvals.json")
        self.assertEqual([{"idempotency_key": f"DPH-100:{digest}", "active": True, "comment_id": 7, "issue_url": None}], snapshot["claims"])

    def test_dispatch_rejects_noncanonical_issue_number(self) -> None:
        plan = plan_fixture()
        digest = plan_digest(plan)
        report = {
            "plan_sha256": digest,
            "evaluations": [{"phase_id": "DPH-100", "state": "ready", "reason": "ready", "idempotency_key": f"DPH-100:{digest}"}],
        }
        with patch("dependency_phases.issues", return_value=[canonical_issue()]):
            with self.assertRaisesRegex(CommandError, "not the canonical issue"):
                dispatch_claim(plan, report, "example/repo", "DPH-100", 99, apply=False)

    def test_dispatch_dry_run_uses_only_the_canonical_issue(self) -> None:
        plan = plan_fixture()
        digest = plan_digest(plan)
        report = {
            "plan_sha256": digest,
            "evaluations": [{"phase_id": "DPH-100", "state": "ready", "reason": "ready", "idempotency_key": f"DPH-100:{digest}"}],
        }
        with (
            patch("dependency_phases.issues", return_value=[canonical_issue()]),
            patch("dependency_phases.issue_comments", return_value=[]),
            patch("dependency_phases.post_issue_comment", return_value={"planned": True, "operation": "post_issue_comment", "issue": 12}) as post_comment,
        ):
            result = dispatch_claim(plan, report, "example/repo", "DPH-100", 12, apply=False)
        self.assertFalse(result["claimed"])
        self.assertTrue(result["planned"])
        post_comment.assert_called_once_with("example/repo", 12, unittest.mock.ANY, apply=False)


if __name__ == "__main__":
    unittest.main()
