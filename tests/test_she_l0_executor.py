"""Tests for she.recovery.executor — pure L0 intent shapes."""
from __future__ import annotations

import pytest

from she.recovery.executor import (
    L0_TARGETS,
    L0ExecutionPlan,
    L0Intent,
    intents_for_workflow_failure,
    plan_l0_execution,
)
from she.recovery.l0 import L0Plan


def test_l0_targets_vocabulary() -> None:
    assert "actions_rerun_failed_jobs" in L0_TARGETS
    assert "observe" in L0_TARGETS
    assert "noop" in L0_TARGETS


def test_plan_l0_execution_workflow_failure() -> None:
    plan = L0Plan(
        incident_id="inc-wf-1",
        actions=("retry", "refresh", "restart"),
        max_attempts=3,
        reason="test",
        metadata={
            "classification": "workflow-failure",
            "fingerprint": "gha:32774439027",
        },
    )
    exe = plan_l0_execution(plan, run_id=32774439027, workflow_id="agentic-repository-operations-report.lock.yml")
    assert exe.incident_id == "inc-wf-1"
    assert exe.mutates_source is False
    assert len(exe.intents) == 3
    assert exe.intents[0].target == "actions_rerun_failed_jobs"
    assert exe.intents[0].run_id == 32774439027
    assert exe.intents[1].target == "cache_refresh"
    assert exe.intents[2].target == "actions_rerun_workflow"


def test_plan_l0_execution_dependabot_observe() -> None:
    plan = L0Plan(
        incident_id="inc-db-1",
        actions=("observe_only",),
        metadata={"classification": "dependabot-critical", "fingerprint": "dependabot:1"},
    )
    exe = plan_l0_execution(plan)
    assert len(exe.intents) == 1
    assert exe.intents[0].target == "observe"
    assert exe.intents[0].run_id is None


def test_intents_for_workflow_failure_canary() -> None:
    exe = intents_for_workflow_failure(
        "canary-agentic-report",
        run_id=32774439027,
        workflow_id="agentic-repository-operations-report.lock.yml",
    )
    assert exe.incident_id == "canary-agentic-report"
    assert any(i.target == "actions_rerun_failed_jobs" for i in exe.intents)
    assert exe.mutates_source is False


def test_roundtrip_mapping() -> None:
    intent = L0Intent(
        action="retry",
        target="actions_rerun_failed_jobs",
        run_id=42,
        workflow_id="ce.yml",
        reason="roundtrip",
    )
    restored = L0Intent.from_mapping(intent.to_mapping())
    assert restored == intent

    plan = L0ExecutionPlan(
        incident_id="x",
        intents=(intent,),
        max_attempts=2,
    )
    restored_p = L0ExecutionPlan.from_mapping(plan.to_mapping())
    assert restored_p.incident_id == "x"
    assert len(restored_p.intents) == 1


def test_unknown_target_rejected() -> None:
    with pytest.raises(ValueError, match="unknown L0 target"):
        L0Intent.from_mapping({"action": "retry", "target": "mutate_source"})
