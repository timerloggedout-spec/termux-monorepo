"""Local regression tests for the repository DO-statement style preflight."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "ci" / "check_do_statement_style.py"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


class DoStatementPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tmp_path = Path(self.temp.name)

    def fixture_repo(self) -> tuple[Path, str]:
        repo = self.tmp_path / "repo"
        repo.mkdir()
        (repo / "scripts" / "ci").mkdir(parents=True)
        (repo / "docs" / "ops").mkdir(parents=True)
        shutil.copy2(CHECKER, repo / "scripts" / "ci" / CHECKER.name)
        git(repo, "init", "-q")
        git(repo, "config", "user.name", "Preflight Test")
        git(repo, "config", "user.email", "preflight@example.invalid")
        (repo / "docs" / "ops" / "baseline.md").write_text("# Baseline\\n", encoding="utf-8")
        git(repo, "add", ".")
        git(repo, "commit", "-m", "docs: add baseline")
        base = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        return repo, base

    def run_preflight(self, repo: Path, base: str, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/ci/check_do_statement_style.py",
             "--preflight", "--base", base, *extra],
            cwd=repo, capture_output=True, text=True,
        )

    def test_preflight_flags_untracked_instruction_lines(self) -> None:
        repo, base = self.fixture_repo()
        draft = repo / "docs" / "ops" / "new-guidance.md"
        draft.write_text("Never start with a prohibition.\\n", encoding="utf-8")

        result = self.run_preflight(repo, base)

        self.assertEqual(result.returncode, 1)
        self.assertIn("docs/ops/new-guidance.md", result.stdout)
        self.assertIn("lead with the intended DO action", result.stdout)

    def test_preflight_accepts_action_first_worktree_and_draft(self) -> None:
        repo, base = self.fixture_repo()
        draft = repo / "docs" / "ops" / "new-guidance.md"
        draft.write_text("Require authenticated transport for every fetch.\\n", encoding="utf-8")
        comment = self.tmp_path / "comment.md"
        comment.write_text("Hold promotion until all required checks pass.\\n", encoding="utf-8")

        result = self.run_preflight(repo, base, "--text-file", str(comment))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DO-statement style: PASS", result.stdout)

    def test_preflight_checks_untracked_source_comments(self) -> None:
        repo, base = self.fixture_repo()
        source = repo / "sample.py"
        source.write_text("# Never bypass the validation gate.\n", encoding="utf-8")

        result = self.run_preflight(repo, base)

        self.assertEqual(result.returncode, 1)
        self.assertIn("sample.py", result.stdout)
        self.assertIn("source comments", result.stdout)

    def test_pull_request_review_body_uses_do_first_language(self) -> None:
        repo, _ = self.fixture_repo()
        event = self.tmp_path / "event.json"
        event.write_text(
            '{"review":{"body":"Never merge before validation."}}',
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, "scripts/ci/check_do_statement_style.py"],
            cwd=repo, capture_output=True, text=True,
            env={**os.environ, "GITHUB_EVENT_PATH": str(event),
                 "GITHUB_EVENT_NAME": "pull_request_review"},
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("pull_request_review.body", result.stdout)

    def test_local_invocation_requires_explicit_preflight(self) -> None:
        repo, _ = self.fixture_repo()
        result = subprocess.run(
            [sys.executable, "scripts/ci/check_do_statement_style.py"],
            cwd=repo, capture_output=True, text=True,
            env={**os.environ, "GITHUB_EVENT_PATH": ""},
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("--preflight --base <ref>", result.stdout)


if __name__ == "__main__":
    unittest.main()
