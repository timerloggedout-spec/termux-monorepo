from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "agentic"))

from github_phase_adapter import (  # noqa: E402
    CommandResult,
    active_claim_records,
    add_issue_to_project,
    phase_issue_matches,
)


class GitHubPhaseAdapterTests(unittest.TestCase):
    def test_project_add_dry_run_never_calls_gh(self) -> None:
        with patch("github_phase_adapter.run_gh") as run_gh:
            result = add_issue_to_project("timerloggedout-spec", 1, "https://example.test/issues/1", apply=False)
        self.assertTrue(result["planned"])
        run_gh.assert_not_called()

    def test_project_add_avoids_formatted_mutation_response(self) -> None:
        with patch("github_phase_adapter.run_gh", return_value=CommandResult("", "")) as run_gh:
            result = add_issue_to_project("timerloggedout-spec", 1, "https://example.test/issues/1", apply=True)
        self.assertFalse(result["planned"])
        arguments = run_gh.call_args.args[0]
        self.assertEqual(["project", "item-add", "1", "--owner", "timerloggedout-spec", "--url", "https://example.test/issues/1"], arguments)
        self.assertNotIn("--format", arguments)

    def test_active_claim_records_parse_only_durable_markers(self) -> None:
        digest = "a" * 64
        claims = active_claim_records([
            {"id": 1, "body": f"<!-- dependency-phase-claim: DPH-100:{digest} --> claimed"},
            {"id": 2, "body": "unrelated comment"},
        ])
        self.assertEqual([{"idempotency_key": f"DPH-100:{digest}", "active": True, "comment_id": 1, "issue_url": None}], claims)

    def test_phase_issue_match_requires_exact_generated_provenance(self) -> None:
        plan = {"plan_id": "fixture-plan"}
        phase = {"phase_id": "DPH-100", "title": "Dependent work"}
        canonical = {"title": "[DPH-100] Dependent work", "body": "**Plan:** `fixture-plan`\n**Phase:** `DPH-100`"}
        unrelated = {"title": "[DPH-100] Dependent work", "body": "Implements: DPH-100"}
        self.assertTrue(phase_issue_matches(plan, phase, canonical))
        self.assertFalse(phase_issue_matches(plan, phase, unrelated))


if __name__ == "__main__":
    unittest.main()
