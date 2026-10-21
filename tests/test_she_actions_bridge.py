"""SHE Actions bridge — pure plan + dry-run default."""
from __future__ import annotations

from she.recovery.actions_bridge import (
    bridge_workflow_failure,
    execute_actions_bridge,
    plan_actions_commands,
)
from she.recovery.executor import intents_for_workflow_failure


def test_plan_rerun_failed_jobs_path():
    plan = intents_for_workflow_failure("inc-1", run_id=42, workflow_id="wf.yml")
    cmds = plan_actions_commands(plan, owner="o", repo="r", dry_run=True)
    actions_cmds = [c for c in cmds if c.method == "POST" and c.path]
    assert any("rerun-failed-jobs" in c.path for c in actions_cmds)
    assert any(c.path.endswith("/rerun") for c in actions_cmds)
    assert all(c.dry_run for c in cmds)


def test_execute_default_dry_run(monkeypatch):
    monkeypatch.delenv("SHE_L0_LIVE", raising=False)
    result = bridge_workflow_failure(
        "inc-2", run_id=99, owner="timerloggedout-spec", repo="termux-monorepo"
    )
    assert result.executed is False
    assert result.mutates_source is False
    assert any(o.get("dry_run") for o in result.outcomes)
    body = result.to_mapping()
    assert body["incident_id"] == "inc-2"


def test_missing_run_id_skipped():
    from she.recovery.executor import L0ExecutionPlan, L0Intent

    plan = L0ExecutionPlan(
        incident_id="inc-3",
        intents=(
            L0Intent(
                action="retry",
                target="actions_rerun_failed_jobs",
                run_id=None,
                reason="no run",
            ),
        ),
    )
    cmds = plan_actions_commands(plan, owner="o", repo="r")
    assert cmds[0].path == ""
    assert cmds[0].metadata.get("error") == "missing_run_id"
