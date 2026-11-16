"""The quota-analysis workflow is the GitHub-surface proving step for every
quota change (owner ruling 2026-11-01): it must trigger on the quota
surfaces and run the validator, the battery, the snapshot pair/completeness
check, and the coverage check. Text-level pins, offline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = (ROOT / ".github/workflows/quota-analysis.yml").read_text()


def test_workflow_is_read_only():
    assert "contents: read" in WF
    assert "contents: write" not in WF


def test_workflow_triggers_on_quota_surfaces_for_pr_and_push():
    for needle in ("pull_request:", "push:", "workflow_dispatch:",
                   '"ops/quota/**"', '"scripts/quota_poll.py"',
                   '"scripts/quota_allocations.py"',
                   '"tests/test_quota_*.py"',
                   '"docs/ops/generated/quota-status.json"',
                   '".github/workflows/quota-analysis.yml"'):
        assert needle in WF, needle


def test_workflow_runs_the_full_analysis():
    for needle in ("scripts/quota_allocations.py validate",
                   "tests/test_quota_allocations.py",
                   "tests/test_quota_poll.py",
                   "tests/test_quota_dashboard.py",
                   "tests/test_quota_allocation_planner.py",
                   "tests/test_provider_quota_coverage.py",
                   "cmp docs/ops/generated/quota-status.json apps/tribute-dashboard/data/quota.json",
                   "provider_quota_coverage.py --check",
                   "pip install -q pytest"):
        assert needle in WF, needle
