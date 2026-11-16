"""SHE P0.4 — dynamic dispatcher scaffold (pure ranking, no side effects).

Ranks L0 recovery actions against a static capability table and an explicit
authority set. MoneyBall scores are decision-support only and never grant
execution. This module performs no network I/O and never mutates source.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from she.recovery.l0 import L0_ACTIONS, L0Plan

# Capability table: action → required authority tokens (all must be present).
CAPABILITIES: dict[str, frozenset[str]] = {
    "retry": frozenset({"L0-retry"}),
    "restart": frozenset({"L0-retry"}),
    "reconnect": frozenset({"L0-retry"}),
    "refresh": frozenset({"L0-retry", "L0-observe"}),
    "regenerate_transient": frozenset({"L0-retry"}),
    "reacquire_lock": frozenset({"L0-retry"}),
    "safe_rollback_ephemeral": frozenset({"L0-retry"}),
    "observe_only": frozenset({"L0-observe"}),
}

# Lower rank number = preferred when authorized.
_ACTION_RANK: dict[str, int] = {
    "retry": 10,
    "refresh": 20,
    "restart": 30,
    "reconnect": 40,
    "regenerate_transient": 50,
    "reacquire_lock": 60,
    "safe_rollback_ephemeral": 70,
    "observe_only": 90,
}


@dataclass(frozen=True)
class DispatchDecision:
    """Ranked, authority-filtered view of an L0 plan. Never executes."""

    incident_id: str
    selected: tuple[str, ...]
    deferred: tuple[str, ...]
    denied: tuple[str, ...]
    moneyball_score: float | None = None
    live: bool = False
    mutates_source: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "selected": list(self.selected),
            "deferred": list(self.deferred),
            "denied": list(self.denied),
            "moneyball_score": self.moneyball_score,
            "live": self.live,
            "mutates_source": self.mutates_source,
            "metadata": dict(self.metadata),
        }


def _authorized(action: str, authority: Sequence[str]) -> bool:
    needed = CAPABILITIES.get(action, frozenset({"L0-observe"}))
    have = set(authority)
    return needed.issubset(have)


def rank_actions(
    actions: Sequence[str],
    *,
    authority: Sequence[str],
    moneyball_score: float | None = None,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Split actions into selected / deferred / denied. Pure function."""
    selected: list[str] = []
    deferred: list[str] = []
    denied: list[str] = []
    seen: set[str] = set()
    for action in actions:
        if action not in L0_ACTIONS:
            raise ValueError(f"unknown L0 action: {action!r}")
        if action in seen:
            continue
        seen.add(action)
        if not _authorized(action, authority):
            denied.append(action)
            continue
        # MoneyBall may only defer aggressive actions, never authorize new ones.
        if (
            moneyball_score is not None
            and moneyball_score < 0.25
            and action not in {"observe_only", "refresh"}
        ):
            deferred.append(action)
            continue
        selected.append(action)
    selected.sort(key=lambda a: _ACTION_RANK.get(a, 100))
    return tuple(selected), tuple(deferred), tuple(denied)


def dispatch_l0_plan(
    plan: L0Plan,
    *,
    authority: Sequence[str] | None = None,
    moneyball_score: float | None = None,
    live: bool = False,
) -> DispatchDecision:
    """Rank a planner output. `live` is recorded only; this function never executes."""
    auth = tuple(authority) if authority is not None else plan.authority_scope
    selected, deferred, denied = rank_actions(
        plan.actions,
        authority=auth,
        moneyball_score=moneyball_score,
    )
    if not selected and _authorized("observe_only", auth):
        selected = ("observe_only",)
    return DispatchDecision(
        incident_id=plan.incident_id,
        selected=selected,
        deferred=deferred,
        denied=denied,
        moneyball_score=moneyball_score,
        live=bool(live),
        mutates_source=False,
        metadata={
            "plan_reason": plan.reason,
            "authority": list(auth),
            "source_actions": list(plan.actions),
        },
    )


def dispatch_from_mapping(
    data: Mapping[str, Any],
    *,
    authority: Sequence[str] | None = None,
    moneyball_score: float | None = None,
    live: bool = False,
) -> DispatchDecision:
    return dispatch_l0_plan(
        L0Plan.from_mapping(data),
        authority=authority,
        moneyball_score=moneyball_score,
        live=live,
    )
