from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "agentic"))

from github_phase_adapter import CommandResult, add_issue_to_project  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
