#!/usr/bin/env python3
"""Regression tests for evaluation-side-effect containment."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVAL_WORKFLOWS = [
    ROOT / ".github/workflows/continuous-evaluation.yml",
    ROOT / ".github/workflows/team-mvt.yml",
    ROOT / ".github/workflows/ox-alpha-smoke.yml",
]

def test_evaluation_workflows_have_no_repository_write_permissions():
    for path in EVAL_WORKFLOWS:
        text = path.read_text(encoding="utf-8")
        assert "contents: write" not in text, path
        assert "pull-requests: write" not in text, path
        assert "issues: write" not in text, path

def test_evaluation_workflows_do_not_create_prs():
    for path in EVAL_WORKFLOWS:
        text = path.read_text(encoding="utf-8")
        assert "pulls.create" not in text, path
        assert "create-pull-request" not in text, path
        assert "gh pr create" not in text, path

def test_model_canary_does_not_post_results_back_to_issue():
    text = (ROOT / ".github/workflows/ox-alpha-smoke.yml").read_text(encoding="utf-8")
    assert "issues/" not in text
    assert "Confirm canary launch" not in text

if __name__ == "__main__":
    test_evaluation_workflows_have_no_repository_write_permissions()
    test_evaluation_workflows_do_not_create_prs()
    test_model_canary_does_not_post_results_back_to_issue()
    print("evaluation side-effect containment: PASS")
