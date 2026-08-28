"""SHE P0.10 — promotion-decision planner (observer-only, no live merge).

Decides whether a bound verification + repair-PR contract may be marked
ready for a later human/executor merge onto master. This module plans.
It does not merge, push, or mutate git.

Live promotion remains a later slice behind SHE_PROMOTE_LIVE=1.
stdlib-only. No network.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from she.incident import Incident, IncidentState
from she.repair_pr import RepairPRPlan, plan_repair_pr
from she.verify import DUAL_GATES, VerificationPlan, apply_check_results, plan_verification

DECISIONS: frozenset[str] = frozenset({"hold", "promote", "observe-only"})

_TERMINAL_BLOCK = {
    IncidentState.LEARNED,
    IncidentState.QUARANTINED,
    IncidentState.ABANDONED,
}


class PromotionError(ValueError):
    """Invalid promotion construction or policy violation."""


def live_promote_enabled() -> bool:
    """Live merge remains gated and unused in P0.10."""
    return os.environ.get("SHE_PROMOTE_LIVE", "").strip() == "1"


def _is_security(incident: Incident) -> bool:
    classification = (incident.classification or "").lower()
    fp = incident.fingerprint or ""
    return classification.startswith("dependabot-") or fp.startswith("dependabot:")


@dataclass(frozen=True)
class PromotionDecision:
    """Inspectable promotion contract for one incident."""

    incident_id: str
    sha: str
    decision: str
    required_gates: tuple[str, ...]
    rollback_sha: str
    promotion_ready: bool = False
    live: bool = False
    mutates_source: bool = False
    reasons: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.decision not in DECISIONS:
            raise PromotionError(f"unknown decision: {self.decision!r}")
        needed = set(self.required_gates)
        if not DUAL_GATES.issubset(needed):
            raise PromotionError("dual gates repo-gate + termux-smoke must be required")
        if self.rollback_sha != self.sha:
            raise PromotionError("rollback_sha must match sha")
        if not self.incident_id:
            raise PromotionError("incident_id required")
        if self.live and self.promotion_ready:
            raise PromotionError("live plans cannot be promotion_ready")
        if self.mutates_source:
            raise PromotionError("P0.10 planner cannot mutate source")
        if self.decision == "promote" and not self.promotion_ready:
            raise PromotionError("promote requires promotion_ready")
        if self.decision != "promote" and self.promotion_ready:
            raise PromotionError("non-promote decisions cannot be promotion_ready")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "sha": self.sha,
            "decision": self.decision,
            "required_gates": list(self.required_gates),
            "rollback_sha": self.rollback_sha,
            "promotion_ready": self.promotion_ready,
            "live": self.live,
            "mutates_source": self.mutates_source,
            "reasons": list(self.reasons),
            "constraints": list(self.constraints),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> PromotionDecision:
        gates = tuple(str(x) for x in (data.get("required_gates") or ()))
        sha = str(data.get("sha") or "")
        return cls(
            incident_id=str(data["incident_id"]),
            sha=sha,
            decision="hold",
            required_gates=gates,
            rollback_sha=str(data.get("rollback_sha") or sha),
            promotion_ready=False,
            live=False,
            mutates_source=False,
            reasons=tuple(str(x) for x in (data.get("reasons") or ("from_mapping_fail_closed",))),
            constraints=tuple(str(x) for x in (data.get("constraints") or ())),
            metadata=dict(data.get("metadata") or {}),
        )


def _bind(incident: Incident, verification: VerificationPlan, repair: RepairPRPlan) -> None:
    if verification.incident_id != incident.incident_id:
        raise PromotionError("verification incident_id must match incident")
    if verification.sha != incident.sha:
        raise PromotionError("verification sha must match incident sha")
    if repair.incident_id != incident.incident_id:
        raise PromotionError("repair incident_id must match incident")
    if repair.sha != incident.sha:
        raise PromotionError("repair sha must match incident sha")
    if repair.rollback_sha != incident.sha:
        raise PromotionError("repair rollback_sha must match incident sha")


def plan_promotion(
    incident: Incident,
    *,
    verification: VerificationPlan | None = None,
    repair: RepairPRPlan | None = None,
    check_results: Mapping[str, Mapping[str, Any]] | None = None,
) -> PromotionDecision:
    """Plan a promotion decision. Does not merge.

    Dual gates always required (subset). Security/Dependabot stay observe-only.
    HTTP 200 / inconclusive / pending cannot promote. from_mapping is fail-closed.
    """
    if incident.state in _TERMINAL_BLOCK:
        raise PromotionError(
            f"promotion not applicable for terminal state {incident.state.value}"
        )
    if _is_security(incident):
        gates = tuple(sorted(DUAL_GATES | {"security-checks"}))
        return PromotionDecision(
            incident_id=incident.incident_id,
            sha=incident.sha,
            decision="observe-only",
            required_gates=gates,
            rollback_sha=incident.sha,
            promotion_ready=False,
            live=False,
            mutates_source=False,
            reasons=("security_dependabot_observe_only",),
            constraints=(
                "dual_gates_required",
                "no_live_merge",
                "http_200_is_not_pass",
                "subset_required_gates",
            ),
            metadata={
                "classification": incident.classification,
                "fingerprint": incident.fingerprint,
                "live_flag_honored": live_promote_enabled(),
            },
        )

    verification = verification or plan_verification(incident)
    if check_results:
        verification = apply_check_results(verification, check_results)
    repair = repair or plan_repair_pr(incident, verification=verification)
    _bind(incident, verification, repair)

    needed = tuple(sorted(set(verification.required_gates()) | set(repair.required_tests) | DUAL_GATES))
    if not DUAL_GATES.issubset(needed):
        raise PromotionError("dual gates must remain required")

    reasons: list[str] = []
    if repair.live or verification.live:
        reasons.append("child_plan_live")
    if not verification.promotion_ready:
        reasons.append("verification_not_ready")
    pending_or_soft = [
        c.gate
        for c in verification.checks
        if c.required and c.outcome in {"pending", "inconclusive"}
    ]
    if pending_or_soft:
        reasons.append("required_gate_not_pass")
    failed = [c.gate for c in verification.checks if c.required and c.outcome == "fail"]
    if failed:
        reasons.append("required_gate_failed")

    ready = (
        verification.promotion_ready
        and not reasons
        and not live_promote_enabled()
    )
    decision = "promote" if ready else "hold"
    return PromotionDecision(
        incident_id=incident.incident_id,
        sha=incident.sha,
        decision=decision,
        required_gates=needed,
        rollback_sha=incident.sha,
        promotion_ready=ready,
        live=False,
        mutates_source=False,
        reasons=tuple(reasons) or (("all_required_gates_pass",) if ready else ("held",)),
        constraints=(
            "dual_gates_required",
            "no_live_merge",
            "http_200_is_not_pass",
            "rollback_sha_bound",
            "subset_required_gates",
            "child_plans_must_match",
        ),
        metadata={
            "classification": incident.classification,
            "fingerprint": incident.fingerprint,
            "source": incident.source,
            "state": incident.state.value,
            "repair_branch": repair.branch,
            "verification_ready": verification.promotion_ready,
            "live_flag_honored": live_promote_enabled(),
        },
    )
