"""SHE P0.3 — Actions re-run bridge (command plan + optional live wire).

Maps L0Intent targets to GitHub Actions re-run API shapes.

- Pure by default: emit command plans / HTTP descriptions only.
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

from she.recovery.executor import L0ExecutionPlan, L0Intent, L0_TARGETS


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

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "commands": [c.to_mapping() for c in self.commands],
            "executed": self.executed,
            "outcomes": list(self.outcomes),
            "mutates_source": self.mutates_source,
        }


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
    """Canary helper: intents_for_workflow_failure → Actions bridge."""
    from she.recovery.executor import intents_for_workflow_failure

    plan = intents_for_workflow_failure(
        incident_id, run_id=run_id, workflow_id=workflow_id
    )
    return execute_actions_bridge(
        plan, owner=owner, repo=repo, force_live=force_live
    )
