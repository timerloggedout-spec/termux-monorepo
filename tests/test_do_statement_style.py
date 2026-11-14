"""Regression tests for the DO-statement commit-history contract."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/ci/check_do_statement_style.py"
SPEC = importlib.util.spec_from_file_location("do_statement_style", SCRIPT)
assert SPEC and SPEC.loader
STYLE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STYLE)


def test_action_verbs_used_by_repository_commits_are_accepted():
    for subject in (
        "Normalize QUE auto-claim ranking scores",
        "Schedule public quota readings refresh",
        "Clear stale intake diagnosis",
        "Expose Surfaces Map in shared navigation",
        "Automate public quota observation",
        "Exclude deferred work from provider dispatch",
        "Stabilize QUE drain receipt identity",
        "Tighten workflow expression regression",
        "fix(quota): refresh source inputs",
    ):
        assert STYLE.is_action_subject(subject), subject


def test_non_action_first_commit_subject_is_rejected():
    assert not STYLE.is_action_subject("No changes required")


def test_git_history_scan_excludes_synthetic_and_authored_merge_commits():
    args = STYLE.git_log_args("origin/master", "HEAD", "%s")
    assert args == ["git", "log", "--no-merges", "origin/master..HEAD", "--format=%s"]
