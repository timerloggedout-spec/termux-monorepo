"""Local preflight tests for the repository DO-statement style checker."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "ci" / "check_do_statement_style.py"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def fixture_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "scripts" / "ci").mkdir(parents=True)
    (repo / "docs" / "ops").mkdir(parents=True)
    shutil.copy2(CHECKER, repo / "scripts" / "ci" / CHECKER.name)
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Preflight Test")
    git(repo, "config", "user.email", "preflight@example.invalid")
    (repo / "docs" / "ops" / "baseline.md").write_text("# Baseline\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "docs: add baseline")
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    return repo, base


def run_preflight(repo: Path, base: str, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/ci/check_do_statement_style.py",
         "--preflight", "--base", base, *extra],
        cwd=repo, capture_output=True, text=True,
    )


def test_preflight_flags_untracked_instruction_lines(tmp_path: Path) -> None:
    repo, base = fixture_repo(tmp_path)
    draft = repo / "docs" / "ops" / "new-guidance.md"
    draft.write_text("Never start with a prohibition.\n", encoding="utf-8")

    result = run_preflight(repo, base)

    assert result.returncode == 1
    assert "docs/ops/new-guidance.md" in result.stdout
    assert "lead with the intended DO action" in result.stdout


def test_preflight_accepts_action_first_worktree_and_draft(tmp_path: Path) -> None:
    repo, base = fixture_repo(tmp_path)
    draft = repo / "docs" / "ops" / "new-guidance.md"
    draft.write_text("Require authenticated transport for every fetch.\n", encoding="utf-8")
    comment = tmp_path / "comment.md"
    comment.write_text("Hold promotion until all required checks pass.\n", encoding="utf-8")

    result = run_preflight(repo, base, "--text-file", str(comment))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "DO-statement style: PASS" in result.stdout


def test_local_invocation_requires_explicit_preflight(tmp_path: Path) -> None:
    repo, _ = fixture_repo(tmp_path)
    result = subprocess.run(
        [sys.executable, "scripts/ci/check_do_statement_style.py"],
        cwd=repo, capture_output=True, text=True,
        env={**os.environ, "GITHUB_EVENT_PATH": ""},
    )

    assert result.returncode == 2
    assert "--preflight --base <ref>" in result.stdout
