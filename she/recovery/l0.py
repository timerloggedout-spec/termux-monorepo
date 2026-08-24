"""SHE P0.3 — L0 recovery planner (deterministic, no source mutation).

L0 actions never edit repository source. They operate on transient
runtime/CI state only: retry jobs, restart workers, reconnect services,
refresh caches, regenerate ephemeral artifacts, reacquire locks, or
roll back transient promotions.

This module produces a plan. Execution (Actions re-run, Termux daemon
control, etc.) is a later wire-up; authority still gates every action.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from she.incident import Incident, IncidentState

# Canonical L0 action vocabulary (no source mutation).
L0_ACTIONS: frozenset[str] = frozenset(
    {
        "retry",
        "restart",
        "reconnect",
        "refresh",
        "regenerate_transient",
        "reacquire_lock",
        "safe_rollback_ephemeral",
        "observe_only",
    }
)

# classification / fingerprint prefix → preferred ordered actions
_CLASS_PLANS: dict[str, tuple[str, ...]] = {
    "workflow-failure": ("retry", "refresh", "restart"),
    "gate-failure": ("retry", "refresh", "observe_only"),
    "smoke-failure": ("retry", "restart", "regenerate_transient"),
    "dependabot-critical": ("observe_only",),
    "dependabot-high": ("observe_only",),
    "dependabot-medium": ("observe_only",),
    "dependabot-low": ("observe_only",),
}

_FP_PREFIX_PLANS: dict[str, tuple[str, ...]] = {
    "gha:": ("retry", "refresh", "restart"),
    "repo-gate:": ("retry", "refresh"),
    "termux-smoke:": ("retry", "restart", "regenerate_transient"),
    "dependabot:": ("observe_only",),
}


@dataclass(frozen=True)
class L0Plan:
    """Ordered, authority-scoped L0 recovery plan for one incident."""

    incident_id: str
    actions: tuple[str, ...]
    max_attempts: int = 3
    reason: str = ""
    authority_scope: tuple[str, ...] = ("L0-retry",)
    mutates_source: bool = False  # always False for L0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "actions": list(self.actions),
            "max_attempts": self.max_attempts,
            "reason": self.reason,
            "authority_scope": list(self.authority_scope),
            "mutates_source": self.mutates_source,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> L0Plan:
        actions = tuple(str(a) for a in (data.get("actions") or ()))
        for a in actions:
            if a not in L0_ACTIONS:
                raise ValueError(f"unknown L0 action: {a!r}")
        return cls(
            incident_id=str(data["incident_id"]),
            actions=actions,
            max_attempts=int(data.get("max_attempts") or 3),
            reason=str(data.get("reason") or ""),
            authority_scope=tuple(str(x) for x in (data.get("authority_scope") or ("L0-retry",))),
            mutates_source=False,
            metadata=dict(data.get("metadata") or {}),
        )


def _actions_for_incident(inc: Incident) -> tuple[str, ...]:
    classification = (inc.classification or "").lower()
    if classification in _CLASS_PLANS:
        return _CLASS_PLANS[classification]
    fp = inc.fingerprint or ""
    for prefix, plan in _FP_PREFIX_PLANS.items():
        if fp.startswith(prefix):
            return plan
    # default: safe observe + single retry for non-security signals
    if "dependabot" in classification or fp.startswith("dependabot"):
        return ("observe_only",)
    return ("retry", "observe_only")


def plan_l0_recovery(
    incident: Incident,
    *,
    max_attempts: int = 3,
    extra_actions: Sequence[str] | None = None,
) -> L0Plan:
    """Build an L0 recovery plan for a DETECTED/TRIAGED/FAILED incident.

    Raises ValueError if the incident is terminal in a way that forbids L0,
    or if any requested action is outside the L0 vocabulary.
    """
    if incident.state in {
        IncidentState.LEARNED,
        IncidentState.QUARANTINED,
        IncidentState.ABANDONED,
    }:
        raise ValueError(
            f"L0 recovery not applicable for terminal state {incident.state.value}"
        )

    actions = list(_actions_for_incident(incident))
    if extra_actions:
        for a in extra_actions:
            a = str(a)
            if a not in L0_ACTIONS:
                raise ValueError(f"unknown L0 action: {a!r}")
            if a not in actions:
                actions.append(a)

    # Security signals: never auto-retry beyond observe
    if any(a != "observe_only" for a in actions) and (
        incident.classification.startswith("dependabot-")
        or (incident.fingerprint or "").startswith("dependabot:")
    ):
        actions = ["observe_only"]

    reason = (
        f"L0 plan for {incident.classification or 'unknown'} "
        f"fp={incident.fingerprint or 'none'}"
    )
    return L0Plan(
        incident_id=incident.incident_id,
        actions=tuple(actions),
        max_attempts=max(1, min(int(max_attempts), 10)),
        reason=reason,
        authority_scope=("L0-retry", "L0-observe"),
        mutates_source=False,
        metadata={
            "classification": incident.classification,
            "fingerprint": incident.fingerprint,
            "source": incident.source,
            "state": incident.state.value,
        },
    )
