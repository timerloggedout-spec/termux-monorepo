from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "agentic"))

from github_phase_adapter import (  # noqa: E402
    CommandResult,
    GitHubAdapterError,
    active_claim_records,
    add_issue_to_project,
    phase_issue_matches,
    pull_requests,
    run_gh,
)


class GitHubPhaseAdapterTests(unittest.TestCase):
    def test_run_gh_retries_transient_failure_when_explicitly_requested(self) -> None:
        timeout = subprocess.CompletedProcess([], 1, "", "HTTP 504: Gateway Timeout")
        success = subprocess.CompletedProcess([], 0, "{\"ok\": true}", "")
        with patch("github_phase_adapter.subprocess.run", side_effect=[timeout, success]) as execute, patch(
            "github_phase_adapter.time.sleep"
        ) as sleep:
            result = run_gh(["pr", "list"], attempts=3)
        self.assertEqual("{\"ok\": true}", result.stdout)
        self.assertEqual(2, execute.call_count)
        sleep.assert_called_once_with(1.0)

    def test_run_gh_default_does_not_replay_transient_failure(self) -> None:
        timeout = subprocess.CompletedProcess([], 1, "", "HTTP 504: Gateway Timeout")
        with patch("github_phase_adapter.subprocess.run", return_value=timeout) as execute, self.assertRaises(
            GitHubAdapterError
        ):
            run_gh(["issue", "create"])
        self.assertEqual(1, execute.call_count)

    def test_pull_requests_uses_rest_and_fetches_checks_only_for_phase_evidence(self) -> None:
        pulls = [
            {
                "number": 7,
                "title": "[DPH-000] Foundation",
                "body": "",
                "state": "closed",
                "merged_at": "2026-08-19T00:00:00Z",
                "html_url": "https://example.test/pull/7",
                "head": {"sha": "phase-head"},
            },
            {
                "number": 8,
                "title": "Unrelated maintenance",
                "body": "",
                "state": "open",
                "merged_at": None,
                "html_url": "https://example.test/pull/8",
                "head": {"sha": "other-head"},
            },
        ]
        responses = [
            CommandResult(json.dumps(pulls), ""),
            CommandResult(json.dumps({"check_runs": [{"name": "repo-gate", "conclusion": "success"}]}), ""),
            CommandResult(json.dumps({"statuses": [{"context": "termux-smoke", "state": "success"}]}), ""),
        ]
        with patch("github_phase_adapter.run_gh", side_effect=responses) as execute:
            evidence = pull_requests("owner/repo", "master", phase_ids=["DPH-000"])
        self.assertTrue(evidence[0]["merged"])
        self.assertEqual({"repo-gate": "success", "termux-smoke": "success"}, evidence[0]["checks"])
        self.assertEqual({}, evidence[1]["checks"])
        commands = [call.args[0] for call in execute.call_args_list]
        self.assertEqual("api", commands[0][0])
        self.assertIn("/pulls?state=all&base=master", commands[0][-1])
        self.assertNotIn("statusCheckRollup", " ".join(" ".join(command) for command in commands))

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
