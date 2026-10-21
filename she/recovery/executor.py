"""SHE P0.3 — L0 recovery executor (intent shapes only).

Turns an L0Plan into ordered execution intents. Never mutates repository
source. Network / token use is left to a later Actions job or operator
bridge; this module is pure and side-effect free.

Primary mapping for workflow-failure canaries (e.g. agentic-report):
  retry → actions_rerun_failed_jobs / actions_rerun_workflow
  refresh → noop intent with reason (cache refresh deferred)
  restart → same as retry for GHA class
  observe_only → no execution payload
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from she.recovery.l0 import L0_ACTIONS, L0Plan

# Execution target vocabulary (transient runtime only).
L0_TARGETS: frozenset[str] = frozenset(
    {
        "actions_rerun_failed_jobs",
        "actions_rerun_workflow",
        "actions_cancel_run",
        "termux_restart_worker",
        "termux_reconnect",
        "cache_refresh",
        "observe",
        "noop",
    }
)


@dataclass(frozen=True)
class L0Intent:
    """Single L0 execution intent (no side effects)."""

    action: str
    target: str
    run_id: int | None = None
    workflow_id: str | None = None
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "target": self.target,
            "run_id": self.run_id,
            "workflow_id": self.workflow_id,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> L0Intent:
        action = str(data["action"])
        target = str(data["target"])
        if action not in L0_ACTIONS:
            raise ValueError(f"unknown L0 action: {action!r}")
        if target not in L0_TARGETS:
            raise ValueError(f"unknown L0 target: {target!r}")
        run_id = data.get("run_id")
        return cls(
            action=action,
            target=target,
            run_id=int(run_id) if run_id is not None else None,
            workflow_id=str(data["workflow_id"]) if data.get("workflow_id") else None,
            reason=str(data.get("reason") or ""),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass(frozen=True)
class L0ExecutionPlan:
    """Ordered intents for one L0Plan. Authority still gates every action."""

    incident_id: str
    intents: tuple[L0Intent, ...]
    max_attempts: int = 3
    mutates_source: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "intents": [i.to_mapping() for i in self.intents],
            "max_attempts": self.max_attempts,
            "mutates_source": self.mutates_source,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> L0ExecutionPlan:
        intents = tuple(L0Intent.from_mapping(x) for x in (data.get("intents") or ()))
        return cls(
            incident_id=str(data["incident_id"]),
            intents=intents,
            max_attempts=int(data.get("max_attempts") or 3),
            mutates_source=False,
            metadata=dict(data.get("metadata") or {}),
        )


def _target_for_action(
    action: str,
    *,
    classification: str = "",
    fingerprint: str = "",
) -> str:
    """Map L0 action + incident class/fp to a concrete target."""
    if action == "observe_only":
        return "observe"
    cls = (classification or "").lower()
    fp = fingerprint or ""
    if action == "retry":
        if cls.startswith("workflow-") or fp.startswith("gha:"):
            return "actions_rerun_failed_jobs"
        if cls.startswith("gate-") or fp.startswith("repo-gate:"):
            return "actions_rerun_workflow"
        if cls.startswith("smoke-") or fp.startswith("termux-smoke:"):
            return "termux_restart_worker"
        return "actions_rerun_failed_jobs"
    if action == "restart":
        if fp.startswith("termux-smoke:") or "smoke" in cls:
            return "termux_restart_worker"
        return "actions_rerun_workflow"
    if action == "reconnect":
        return "termux_reconnect"
    if action == "refresh":
        return "cache_refresh"
    if action in {"regenerate_transient", "reacquire_lock", "safe_rollback_ephemeral"}:
        return "noop"
    return "noop"


def plan_l0_execution(
    plan: L0Plan,
    *,
    run_id: int | None = None,
    workflow_id: str | None = None,
    extra_metadata: Mapping[str, Any] | None = None,
) -> L0ExecutionPlan:
    """Expand L0Plan into ordered L0Intent shapes.

    run_id / workflow_id are optional context from the triggering incident
    (e.g. failed agentic-report run). They are attached only to Actions
    targets; never required for observe_only.
    """
    classification = str((plan.metadata or {}).get("classification") or "")
    fingerprint = str((plan.metadata or {}).get("fingerprint") or "")
    intents: list[L0Intent] = []
    for action in plan.actions:
        if action not in L0_ACTIONS:
            raise ValueError(f"unknown L0 action in plan: {action!r}")
        target = _target_for_action(
            action, classification=classification, fingerprint=fingerprint
        )
        intent_run_id = run_id if target.startswith("actions_") else None
        intent_wf = workflow_id if target.startswith("actions_") else None
        intents.append(
            L0Intent(
                action=action,
                target=target,
                run_id=intent_run_id,
                workflow_id=intent_wf,
                reason=plan.reason or f"L0 {action} → {target}",
                metadata={
                    "incident_id": plan.incident_id,
                    "classification": classification,
                    "fingerprint": fingerprint,
                },
            )
        )
    meta = dict(plan.metadata or {})
    if extra_metadata:
        meta.update(dict(extra_metadata))
    meta["source_plan_actions"] = list(plan.actions)
    return L0ExecutionPlan(
        incident_id=plan.incident_id,
        intents=tuple(intents),
        max_attempts=plan.max_attempts,
        mutates_source=False,
        metadata=meta,
    )


def intents_for_workflow_failure(
    incident_id: str,
    *,
    run_id: int,
    workflow_id: str | None = None,
    max_attempts: int = 3,
) -> L0ExecutionPlan:
    """Convenience: canary path for agentic-report / CE workflow-failure."""
    from she.recovery.l0 import L0Plan as _P

    plan = _P(
        incident_id=incident_id,
        actions=("retry", "refresh", "restart"),
        max_attempts=max_attempts,
        reason=f"workflow-failure canary run_id={run_id}",
        authority_scope=("L0-retry",),
        mutates_source=False,
        metadata={
            "classification": "workflow-failure",
            "fingerprint": f"gha:{run_id}",
            "source": "actions",
        },
    )
    return plan_l0_execution(plan, run_id=run_id, workflow_id=workflow_id)
