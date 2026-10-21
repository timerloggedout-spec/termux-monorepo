"""SHE P0.8 — learning planner (provenance record, no persist).

Records successful and failed remediation patterns with incident linkage,
verification history, and dual-gate evidence. This module plans the
learning record. It does not write a store, call the network, or mutate git.

Live persistence is a later slice behind SHE_LEARN_LIVE=1.
stdlib-only.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from she.incident import Incident, IncidentState
from she.verify import DUAL_GATES, VerificationPlan, plan_verification, summarize_results

OUTCOMES: frozenset[str] = frozenset({"success", "failure", "observe"})

_NO_LEARN = {
    IncidentState.QUARANTINED,
    IncidentState.ABANDONED,
}


class LearnError(ValueError):
    """Invalid learning construction or policy violation."""


def live_learn_enabled() -> bool:
    """Live persistence remains gated and unused in P0.8."""
    return os.environ.get("SHE_LEARN_LIVE", "").strip() == "1"


def _is_security(incident: Incident) -> bool:
    classification = (incident.classification or "").lower()
    fp = incident.fingerprint or ""
    return classification.startswith("dependabot-") or fp.startswith("dependabot:")


@dataclass(frozen=True)
class LearningRecord:
    """Append-only provenance record for one incident outcome."""

    incident_id: str
    sha: str
    fingerprint: str
    outcome: str
    verification_summary: str
    reusable: bool = False
    live: bool = False
    persisted: bool = False
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.incident_id:
            raise LearnError("incident_id required")
        if not self.sha:
            raise LearnError("sha required")
        if self.outcome not in OUTCOMES:
            raise LearnError(f"unknown outcome: {self.outcome!r}")
        if self.reusable and self.outcome != "success":
            raise LearnError("only success outcomes may be reusable")
        if self.live:
            raise LearnError("P0.8 planner cannot be live")
        if self.persisted:
            raise LearnError("P0.8 planner cannot persist")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "sha": self.sha,
            "fingerprint": self.fingerprint,
            "outcome": self.outcome,
            "verification_summary": self.verification_summary,
            "reusable": self.reusable,
            "live": self.live,
            "persisted": self.persisted,
            "constraints": list(self.constraints),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> LearningRecord:
        return cls(
            incident_id=str(data["incident_id"]),
            sha=str(data.get("sha") or ""),
            fingerprint=str(data.get("fingerprint") or ""),
            outcome=str(data.get("outcome") or "observe"),
            verification_summary=str(data.get("verification_summary") or ""),
            reusable=False,
            live=False,
            persisted=False,
            constraints=tuple(str(x) for x in (data.get("constraints") or ())),
            metadata=dict(data.get("metadata") or {}),
        )


def plan_learning(
    incident: Incident,
    *,
    verification: VerificationPlan | None = None,
    outcome: str | None = None,
) -> LearningRecord:
    """Plan a learning record. Does not write evidence to disk.

    Dual gates must be present in the bound verification plan (subset).
    Security/Dependabot incidents stay observe-only and never reusable.
    Success reuse requires a promotion-ready verification on the same SHA.
    """
    if incident.state in _NO_LEARN:
        raise LearnError(
            f"learning not applicable for terminal state {incident.state.value}"
        )

    verification = verification or plan_verification(incident)
    if verification.incident_id != incident.incident_id:
        raise LearnError("verification incident_id must match incident")
    if verification.sha != incident.sha:
        raise LearnError("verification sha must match incident sha")
    required = verification.required_gates()
    if not DUAL_GATES.issubset(required):
        raise LearnError("dual gates repo-gate + termux-smoke must be in verification")

    security = _is_security(incident)
    if outcome is None:
        if security:
            resolved = "observe"
        elif verification.promotion_ready:
            resolved = "success"
        else:
            resolved = "failure"
    else:
        resolved = outcome
    if resolved not in OUTCOMES:
        raise LearnError(f"unknown outcome: {resolved!r}")
    if security and resolved != "observe":
        raise LearnError("security/dependabot incidents are observe-only")

    reusable = (
        resolved == "success"
        and verification.promotion_ready
        and not security
        and not verification.live
    )
    summary = summarize_results(verification)
    return LearningRecord(
        incident_id=incident.incident_id,
        sha=incident.sha,
        fingerprint=incident.fingerprint or incident.classification,
        outcome=resolved,
        verification_summary=summary,
        reusable=reusable,
        live=False,
        persisted=False,
        constraints=(
            "dual_gates_required",
            "no_persist",
            "no_live_store",
            "security_observe_only",
            "reuse_requires_verified_success",
            "append_only_evidence",
        ),
        metadata={
            "classification": incident.classification,
            "source": incident.source,
            "state": incident.state.value,
            "repository": incident.repository,
            "verification_ready": verification.promotion_ready,
            "live_flag_honored": live_learn_enabled(),
        },
    )
