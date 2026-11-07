"""Deterministic autonomous escalation policy primitives.

This module only classifies and selects a bounded next step. It performs no
network I/O, invokes no agent, mutates no source, and cannot expand authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import math
from typing import Iterable


TERMINAL_STATES = frozenset({
    "TASK_PASS", "TASK_FAIL", "BLOCKED_CAPABILITY", "BLOCKED_PERMISSION",
    "STAGNATED", "BUDGET_EXHAUSTED", "QUARANTINED", "UNKNOWN",
})
CLASSIFICATIONS = frozenset({
    "TRANSIENT_FAILURE", "CAPABILITY_GAP", "STAGNATION", "CONTRADICTION",
    "VERIFIER_REJECTION", "PROVIDER_UNAVAILABLE", "SECURITY_ANOMALY", "HIGH_IMPACT_RESULT",
    "RESOURCE_EXHAUSTED", "POLICY_DENIAL", "NO_PROGRESS", "UNKNOWN",
})


@dataclass(frozen=True)
class ExecutorCandidate:
    """A live, independently resolved executor candidate.

    All admission booleans must be true. Roster presence alone is insufficient.
    score is decision-support only and never affects authorization.
    """

    executor_ref: str
    role: str
    capabilities: frozenset[str]
    family: str
    adapter_available: bool
    credential_available: bool
    permission_eligible: bool
    healthy: bool
    quota_available: bool
    score: float = 0.0

    def __post_init__(self) -> None:
        if isinstance(self.score, bool) or not isinstance(self.score, (int, float)) or not math.isfinite(self.score):
            raise ValueError("score must be a finite number")
        for name in ("adapter_available", "credential_available", "permission_eligible", "healthy", "quota_available"):
            if not isinstance(getattr(self, name), bool):
                raise ValueError(f"{name} must be boolean")

    @property
    def eligible(self) -> bool:
        return all((
            bool(self.executor_ref), self.adapter_available,
            self.credential_available, self.permission_eligible,
            self.healthy, self.quota_available,
        ))


@dataclass(frozen=True)
class EscalationBudget:
    local_repair_remaining: int = 0
    retry_remaining: int = 0
    same_strategy_replay_count: int = 0
    specialist_handoff_remaining: int = 0
    alternate_family_remaining: int = 0
    manager_replan_remaining: int = 0
    verification_remaining: int = 0

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")


@dataclass(frozen=True)
class EscalationDecision:
    decision: str
    classification: str
    terminal_state: str
    reason_code: str
    target_executor_ref: str | None = None
    authorization_preserved: bool = True
    budget_snapshot: EscalationBudget = field(default_factory=EscalationBudget)

    def to_mapping(self) -> dict:
        result = asdict(self)
        result["budget_snapshot"] = asdict(self.budget_snapshot)
        return result


def _pick_candidate(
    candidates: Iterable[ExecutorCandidate],
    *,
    required_capabilities: frozenset[str],
    excluded_executors: frozenset[str],
    excluded_families: frozenset[str] = frozenset(),
) -> ExecutorCandidate | None:
    eligible = [
        candidate for candidate in candidates
        if candidate.eligible
        and required_capabilities.issubset(candidate.capabilities)
        and candidate.executor_ref not in excluded_executors
        and candidate.family not in excluded_families
    ]
    # Stable tie-break ensures identical inputs produce identical routes.
    return sorted(eligible, key=lambda c: (-c.score, c.executor_ref))[0] if eligible else None


def decide_escalation(
    classification: str,
    *,
    budget: EscalationBudget,
    candidates: Iterable[ExecutorCandidate] = (),
    required_capabilities: Iterable[str] = (),
    current_executor_ref: str | None = None,
    current_family: str | None = None,
    attempted_executor_refs: Iterable[str] = (),
    attempted_families: Iterable[str] = (),
    retry_condition_changed: bool = False,
    same_strategy_replay_count: int | None = None,
) -> EscalationDecision:
    """Return a deterministic, bounded next step without executing it.

    Candidate selection requires a concrete adapter, credential, permission,
    health, and quota signal. A policy denial is never routed around.
    """
    normalized = str(classification).upper()
    if normalized not in CLASSIFICATIONS:
        normalized = "UNKNOWN"
    if same_strategy_replay_count is None:
        same_strategy_replay_count = budget.same_strategy_replay_count
    if isinstance(same_strategy_replay_count, bool) or not isinstance(same_strategy_replay_count, int) or same_strategy_replay_count < 0:
        raise ValueError("same_strategy_replay_count must be a non-negative integer")
    attempted = frozenset(attempted_executor_refs)
    if current_executor_ref:
        attempted = attempted | {current_executor_ref}
    attempted_families_set = frozenset(attempted_families)
    required = frozenset(str(x) for x in required_capabilities)
    pool = tuple(candidates)

    def result(decision: str, terminal: str = "NON_TERMINAL",
               reason: str | None = None, target: str | None = None) -> EscalationDecision:
        return EscalationDecision(
            decision=decision,
            classification=normalized,
            terminal_state=terminal,
            reason_code=reason or normalized,
            target_executor_ref=target,
            authorization_preserved=True,
            budget_snapshot=budget,
        )

    if normalized == "POLICY_DENIAL":
        return result("TERMINATE", "BLOCKED_PERMISSION", "POLICY_DENIAL")
    if normalized == "SECURITY_ANOMALY":
        return result("CONTAIN_BRANCH", "QUARANTINED", "SECURITY_ANOMALY")
    if normalized == "RESOURCE_EXHAUSTED":
        return result("CONTINUE_SAFE_WORK", "BUDGET_EXHAUSTED", "RESOURCE_EXHAUSTED")
    if normalized == "UNKNOWN":
        return result("TERMINATE", "UNKNOWN", "INSUFFICIENT_EVIDENCE")

    if normalized == "TRANSIENT_FAILURE" and budget.retry_remaining > 0:
        if retry_condition_changed and same_strategy_replay_count == 0:
            return result("RETRY_WITH_BACKOFF", reason="TRANSIENT_CONDITION_CHANGED")
        # An unchanged replay is not a retry. Continue to a different executor.

    if normalized in {"STAGNATION", "NO_PROGRESS"} and budget.local_repair_remaining > 0:
        return result("REPAIR_LOCAL", reason="LOCAL_REPAIR_BUDGET_AVAILABLE")

    if normalized in {"CONTRADICTION"} and budget.manager_replan_remaining > 0:
        return result("MANAGER_ARBITRATION", reason="CONFLICT_REQUIRES_ARBITRATION")

    if normalized == "HIGH_IMPACT_RESULT" and budget.verification_remaining > 0:
        verifier = _pick_candidate(
            pool, required_capabilities=required | {"independent-verification"},
            excluded_executors=attempted,
        )
        if verifier:
            return result("INDEPENDENT_VERIFY", reason="ELIGIBLE_INDEPENDENT_VERIFIER_FOUND",
                          target=verifier.executor_ref)
        return result("TERMINATE", "UNKNOWN", "NO_INDEPENDENT_VERIFIER_AVAILABLE")

    if normalized in {"CAPABILITY_GAP", "STAGNATION", "NO_PROGRESS",
                      "VERIFIER_REJECTION", "TRANSIENT_FAILURE"}:
        if budget.specialist_handoff_remaining > 0:
            candidate = _pick_candidate(
                pool, required_capabilities=required,
                excluded_executors=attempted,
            )
            if candidate:
                return result("HANDOFF_SPECIALIST", reason="ELIGIBLE_SPECIALIST_FOUND",
                              target=candidate.executor_ref)

    if normalized in {"PROVIDER_UNAVAILABLE", "TRANSIENT_FAILURE",
                      "CAPABILITY_GAP", "VERIFIER_REJECTION"}:
        if budget.alternate_family_remaining > 0:
            excluded_families = attempted_families_set
            if current_family:
                excluded_families = excluded_families | {current_family}
            candidate = _pick_candidate(
                pool, required_capabilities=required,
                excluded_executors=attempted,
                excluded_families=excluded_families,
            )
            if candidate:
                return result("HANDOFF_ALTERNATE_FAMILY",
                              reason="HEALTHY_ALTERNATE_FAMILY_FOUND",
                              target=candidate.executor_ref)

    if normalized in {"STAGNATION", "NO_PROGRESS", "CONTRADICTION"} and budget.manager_replan_remaining > 0:
        return result("MANAGER_ARBITRATION", reason="MANAGER_REPLAN_BUDGET_AVAILABLE")

    if normalized == "PROVIDER_UNAVAILABLE":
        return result("TERMINATE", "BLOCKED_CAPABILITY", "NO_HEALTHY_CALLABLE_ADAPTER")
    if normalized == "CAPABILITY_GAP":
        return result("TERMINATE", "BLOCKED_CAPABILITY", "NO_ELIGIBLE_SPECIALIST")
    if normalized == "TRANSIENT_FAILURE":
        return result("TERMINATE", "STAGNATED", "NO_SAFE_RECOVERY_ROUTE")
    if normalized in {"STAGNATION", "NO_PROGRESS"}:
        terminal = "BUDGET_EXHAUSTED" if not any((
            budget.local_repair_remaining, budget.specialist_handoff_remaining,
            budget.manager_replan_remaining,
        )) else "STAGNATED"
        return result("TERMINATE", terminal, "NO_PROGRESS_WITHIN_BUDGET")
    if normalized == "CONTRADICTION":
        return result("TERMINATE", "BUDGET_EXHAUSTED", "ARBITRATION_BUDGET_EXHAUSTED")
    if normalized == "VERIFIER_REJECTION":
        return result("TERMINATE", "TASK_FAIL", "VERIFIER_REJECTED_WITH_NO_REPAIR_ROUTE")
    return result("TERMINATE", "UNKNOWN", "NO_POLICY_TRANSITION")
