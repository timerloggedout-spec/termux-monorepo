"""SHE P0.3/P0.5 — Actions re-run bridge (command plan + optional live wire).

Maps L0Intent targets to GitHub Actions re-run API shapes.

- Pure by default: emit command plans / HTTP descriptions only.
- P0.5: dispatch_l0_plan ranks actions before commands are planned.
- Live execution requires SHE_L0_LIVE=1 and a token (GITHUB_TOKEN / GH_TOKEN).
- Never mutates repository source; only workflow run re-runs / cancels.

API (documented REST):
  POST /repos/{owner}/{repo}/actions/runs/{run_id}/rerun
  POST /repos/{owner}/{repo}/actions/runs/{run_id}/rerun-failed-jobs
  POST /repos/{owner}/{repo}/actions/runs/{run_id}/cancel
"""
from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from she.recovery.dispatcher import DispatchDecision, dispatch_l0_plan
from she.recovery.executor import L0ExecutionPlan, L0Intent, L0_TARGETS, plan_l0_execution
from she.recovery.l0 import L0Plan


@dataclass(frozen=True)
class ActionsCommand:
    """One planned Actions API call."""

    method: str
    path: str
    description: str
    intent_target: str
    run_id: int | None = None
    dry_run: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "path": self.path,
            "description": self.description,
            "intent_target": self.intent_target,
            "run_id": self.run_id,
            "dry_run": self.dry_run,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ActionsBridgeResult:
    """Result of planning (and optionally executing) an L0ExecutionPlan."""

    incident_id: str
    commands: tuple[ActionsCommand, ...]
    executed: bool
    outcomes: tuple[dict[str, Any], ...]
    mutates_source: bool = False
    dispatch: dict[str, Any] | None = None

    def to_mapping(self) -> dict[str, Any]:
        body = {
            "incident_id": self.incident_id,
            "commands": [c.to_mapping() for c in self.commands],
            "executed": self.executed,
            "outcomes": list(self.outcomes),
            "mutates_source": self.mutates_source,
        }
        if self.dispatch is not None:
            body["dispatch"] = dict(self.dispatch)
        return body


def _path_for_intent(intent: L0Intent, owner: str, repo: str) -> str | None:
    if intent.run_id is None and intent.target.startswith("actions_"):
        return None
    rid = intent.run_id
    base = f"repos/{owner}/{repo}/actions/runs/{rid}"
    if intent.target == "actions_rerun_failed_jobs":
        return f"{base}/rerun-failed-jobs"
    if intent.target == "actions_rerun_workflow":
        return f"{base}/rerun"
    if intent.target == "actions_cancel_run":
        return f"{base}/cancel"
    return None


def plan_actions_commands(
    execution_plan: L0ExecutionPlan,
    *,
    owner: str,
    repo: str,
    dry_run: bool = True,
) -> tuple[ActionsCommand, ...]:
    """Pure: expand execution intents into Actions API command plans."""
    cmds: list[ActionsCommand] = []
    for intent in execution_plan.intents:
        if intent.target not in L0_TARGETS:
            continue
        if not intent.target.startswith("actions_"):
            cmds.append(
                ActionsCommand(
                    method="NONE",
                    path="",
                    description=f"non-Actions target {intent.target} — skipped by Actions bridge",
                    intent_target=intent.target,
                    run_id=intent.run_id,
                    dry_run=True,
                    metadata={"reason": intent.reason},
                )
            )
            continue
        path = _path_for_intent(intent, owner, repo)
        if path is None:
            cmds.append(
                ActionsCommand(
                    method="POST",
                    path="",
                    description="missing run_id — cannot plan Actions call",
                    intent_target=intent.target,
                    run_id=None,
                    dry_run=True,
                    metadata={"error": "missing_run_id", "reason": intent.reason},
                )
            )
            continue
        cmds.append(
            ActionsCommand(
                method="POST",
                path=path,
                description=f"{intent.action} → {intent.target} run_id={intent.run_id}",
                intent_target=intent.target,
                run_id=intent.run_id,
                dry_run=dry_run,
                metadata={
                    "reason": intent.reason,
                    "workflow_id": intent.workflow_id,
                    "incident_id": execution_plan.incident_id,
                },
            )
        )
    return tuple(cmds)


def _gh_api_post(path: str) -> dict[str, Any]:
    env = os.environ.copy()
    r = subprocess.run(
        ["gh", "api", "-X", "POST", path],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    out: dict[str, Any] = {
        "returncode": r.returncode,
        "stdout": (r.stdout or "")[:2000],
        "stderr": (r.stderr or "")[:500],
    }
    if r.returncode == 0 and r.stdout.strip():
        try:
            out["json"] = json.loads(r.stdout)
        except json.JSONDecodeError:
            pass
    return out


def live_enabled() -> bool:
    """Authority gate: explicit env opt-in for network side effects."""
    return os.environ.get("SHE_L0_LIVE", "").strip() in {"1", "true", "TRUE", "yes"}


def execute_actions_bridge(
    execution_plan: L0ExecutionPlan,
    *,
    owner: str,
    repo: str,
    force_live: bool | None = None,
    dispatch: Mapping[str, Any] | None = None,
) -> ActionsBridgeResult:
    """Plan commands; execute only when live gate is open.

    force_live=None → use SHE_L0_LIVE env.
    force_live=False → always dry-run.
    force_live=True → attempt live (still requires token via gh).
    """
    do_live = live_enabled() if force_live is None else bool(force_live)
    commands = plan_actions_commands(
        execution_plan, owner=owner, repo=repo, dry_run=not do_live
    )
    outcomes: list[dict[str, Any]] = []
    executed = False
    if do_live:
        for cmd in commands:
            if cmd.method != "POST" or not cmd.path:
                outcomes.append(
                    {"skipped": True, "command": cmd.to_mapping()}
                )
                continue
            result = _gh_api_post(cmd.path)
            outcomes.append({"command": cmd.to_mapping(), "result": result})
            executed = True
    else:
        for cmd in commands:
            outcomes.append(
                {
                    "dry_run": True,
                    "would_call": f"{cmd.method} {cmd.path}" if cmd.path else None,
                    "command": cmd.to_mapping(),
                }
            )
    return ActionsBridgeResult(
        incident_id=execution_plan.incident_id,
        commands=commands,
        executed=executed,
        outcomes=tuple(outcomes),
        mutates_source=False,
        dispatch=dict(dispatch) if dispatch is not None else None,
    )


def filter_execution_plan_by_dispatch(
    execution_plan: L0ExecutionPlan,
    decision: DispatchDecision,
) -> L0ExecutionPlan:
    """Keep only intents whose action was selected by the dispatcher."""
    allowed = set(decision.selected)
    kept = tuple(i for i in execution_plan.intents if i.action in allowed)
    meta = dict(execution_plan.metadata)
    meta["dispatch"] = decision.to_mapping()
    meta["filtered_out"] = [
        i.action for i in execution_plan.intents if i.action not in allowed
    ]
    return L0ExecutionPlan(
        incident_id=execution_plan.incident_id,
        intents=kept,
        max_attempts=execution_plan.max_attempts,
        mutates_source=False,
        metadata=meta,
    )


def dispatch_then_bridge(
    plan: L0Plan,
    *,
    owner: str,
    repo: str,
    run_id: int | None = None,
    workflow_id: str | None = None,
    authority: Sequence[str] | None = None,
    moneyball_score: float | None = None,
    force_live: bool | None = None,
) -> ActionsBridgeResult:
    """P0.5 dry-run wire: rank with dispatch_l0_plan, then plan Actions commands.

    The dispatcher `live` flag is recorded only. Network side effects still
    require SHE_L0_LIVE=1 (or force_live=True) inside execute_actions_bridge.
    MoneyBall may defer aggressive actions; it cannot grant authority.
    """
    do_live = live_enabled() if force_live is None else bool(force_live)
    decision = dispatch_l0_plan(
        plan,
        authority=authority,
        moneyball_score=moneyball_score,
        live=do_live,
    )
    ranked = L0Plan(
        incident_id=plan.incident_id,
        actions=decision.selected,
        max_attempts=plan.max_attempts,
        reason=plan.reason,
        authority_scope=tuple(authority)
        if authority is not None
        else plan.authority_scope,
        mutates_source=False,
        metadata=dict(plan.metadata or {}),
    )
    execution_plan = plan_l0_execution(
        ranked,
        run_id=run_id,
        workflow_id=workflow_id,
        extra_metadata={"dispatch": decision.to_mapping()},
    )
    return execute_actions_bridge(
        execution_plan,
        owner=owner,
        repo=repo,
        force_live=force_live,
        dispatch=decision.to_mapping(),
    )


def bridge_workflow_failure(
    incident_id: str,
    *,
    run_id: int,
    owner: str,
    repo: str,
    workflow_id: str | None = None,
    force_live: bool | None = None,
) -> ActionsBridgeResult:
    """Canary helper: intents_for_workflow_failure → Actions bridge.

    Unfiltered P0.3 path kept for regression. Prefer dispatch_then_bridge
    for new callers that must honor dispatcher authority.
    """
    from she.recovery.executor import intents_for_workflow_failure

    plan = intents_for_workflow_failure(
        incident_id, run_id=run_id, workflow_id=workflow_id
    )
    return execute_actions_bridge(
        plan, owner=owner, repo=repo, force_live=force_live
    )
