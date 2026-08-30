"""SHE P0.11 — append-only evidence ledger (observer-only, no persist).

Binds incident identity, dual-gate verification outcomes, promotion
decision, and learning record into one inspectable mapping. This module
plans the ledger. It does not write a store, call the network, or mutate git.

Live persistence remains a later slice behind SHE_LEDGER_LIVE=1.
stdlib-only.
"""
from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from she.incident import Incident, IncidentState
from she.learn import LearningRecord, plan_learning
from she.promote import PromotionDecision, plan_promotion
from she.verify import DUAL_GATES, VerificationPlan, apply_check_results, plan_verification, summarize_results

ENTRY_KINDS: frozenset[str] = frozenset(
    {"incident", "verification", "promotion", "learning"}
)

_TERMINAL_BLOCK = {
    IncidentState.QUARANTINED,
    IncidentState.ABANDONED,
}


class LedgerError(ValueError):
    """Invalid ledger construction or policy violation."""


def live_ledger_enabled() -> bool:
    """Live persistence remains gated and unused in P0.11."""
    return os.environ.get("SHE_LEDGER_LIVE", "").strip() == "1"


def _is_security(incident: Incident) -> bool:
    classification = (incident.classification or "").lower()
    fp = incident.fingerprint or ""
    return classification.startswith("dependabot-") or fp.startswith("dependabot:")


@dataclass(frozen=True)
class LedgerEntry:
    """One append-only evidence row."""

    kind: str
    ref: str
    sha: str
    summary: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind not in ENTRY_KINDS:
            raise LedgerError(f"unknown entry kind: {self.kind!r}")
        if not self.ref:
            raise LedgerError("entry ref required")
        if not self.sha:
            raise LedgerError("entry sha required")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "ref": self.ref,
            "sha": self.sha,
            "summary": self.summary,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> LedgerEntry:
        return cls(
            kind=str(data["kind"]),
            ref=str(data.get("ref") or ""),
            sha=str(data.get("sha") or ""),
            summary=str(data.get("summary") or ""),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass(frozen=True)
class EvidenceLedger:
    """Append-only evidence contract for one incident SHA."""

    incident_id: str
    sha: str
    required_gates: tuple[str, ...]
    entries: tuple[LedgerEntry, ...]
    promotion_decision: str
    persisted: bool = False
    live: bool = False
    mutates_source: bool = False
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.incident_id:
            raise LedgerError("incident_id required")
        if not self.sha:
            raise LedgerError("sha required")
        needed = set(self.required_gates)
        if not DUAL_GATES.issubset(needed):
            raise LedgerError("dual gates repo-gate + termux-smoke must be required")
        kinds = [e.kind for e in self.entries]
        if "incident" not in kinds:
            raise LedgerError("ledger must include an incident entry")
        for entry in self.entries:
            if entry.sha != self.sha:
                raise LedgerError("entry sha must match ledger sha")
        if self.live:
            raise LedgerError("P0.11 planner cannot be live")
        if self.persisted:
            raise LedgerError("P0.11 planner cannot persist")
        if self.mutates_source:
            raise LedgerError("P0.11 planner cannot mutate source")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "sha": self.sha,
            "required_gates": list(self.required_gates),
            "entries": [e.to_mapping() for e in self.entries],
            "promotion_decision": self.promotion_decision,
            "persisted": self.persisted,
            "live": self.live,
            "mutates_source": self.mutates_source,
            "constraints": list(self.constraints),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> EvidenceLedger:
        gates = tuple(str(x) for x in (data.get("required_gates") or ()))
        raw_entries = data.get("entries") or ()
        if not isinstance(raw_entries, Sequence) or isinstance(raw_entries, (str, bytes)):
            raise LedgerError("entries must be a sequence")
        return cls(
            incident_id=str(data["incident_id"]),
            sha=str(data.get("sha") or ""),
            required_gates=gates,
            entries=tuple(LedgerEntry.from_mapping(e) for e in raw_entries),
            promotion_decision="hold",
            persisted=False,
            live=False,
            mutates_source=False,
            constraints=tuple(str(x) for x in (data.get("constraints") or ("from_mapping_fail_closed",))),
            metadata=dict(data.get("metadata") or {}),
        )


def plan_ledger(
    incident: Incident,
    *,
    verification: VerificationPlan | None = None,
    promotion: PromotionDecision | None = None,
    learning: LearningRecord | None = None,
    check_results: Mapping[str, Mapping[str, Any]] | None = None,
) -> EvidenceLedger:
    """Plan an append-only evidence ledger. Does not write to disk.

    Dual gates always required (subset). Security/Dependabot stay observe-only.
    from_mapping is fail-closed (persisted=False, live=False).
    """
    if incident.state in _TERMINAL_BLOCK:
        raise LedgerError(
            f"ledger not applicable for terminal state {incident.state.value}"
        )

    verification = verification or plan_verification(incident)
    if check_results:
        verification = apply_check_results(verification, check_results)
    if verification.incident_id != incident.incident_id:
        raise LedgerError("verification incident_id must match incident")
    if verification.sha != incident.sha:
        raise LedgerError("verification sha must match incident sha")
    required = set(verification.required_gates()) | set(DUAL_GATES)
    if not DUAL_GATES.issubset(required):
        raise LedgerError("dual gates repo-gate + termux-smoke must be required")

    promotion = promotion or plan_promotion(
        incident, verification=verification, check_results=check_results
    )
    if promotion.incident_id != incident.incident_id:
        raise LedgerError("promotion incident_id must match incident")
    if promotion.sha != incident.sha:
        raise LedgerError("promotion sha must match incident sha")
    required |= set(promotion.required_gates)

    learning = learning or plan_learning(incident, verification=verification)
    if learning.incident_id != incident.incident_id:
        raise LedgerError("learning incident_id must match incident")
    if learning.sha != incident.sha:
        raise LedgerError("learning sha must match incident sha")

    security = _is_security(incident)
    if security:
        required |= {"security-checks"}

    entries = (
        LedgerEntry(
            kind="incident",
            ref=incident.incident_id,
            sha=incident.sha,
            summary=f"{incident.state.value}:{incident.classification}",
            metadata={
                "fingerprint": incident.fingerprint,
                "source": incident.source,
            },
        ),
        LedgerEntry(
            kind="verification",
            ref=incident.incident_id,
            sha=incident.sha,
            summary=summarize_results(verification),
            metadata={"promotion_ready": verification.promotion_ready},
        ),
        LedgerEntry(
            kind="promotion",
            ref=incident.incident_id,
            sha=incident.sha,
            summary=promotion.decision,
            metadata={
                "promotion_ready": promotion.promotion_ready,
                "reasons": list(promotion.reasons),
            },
        ),
        LedgerEntry(
            kind="learning",
            ref=incident.incident_id,
            sha=incident.sha,
            summary=learning.outcome,
            metadata={"reusable": learning.reusable},
        ),
    )

    decision = "observe-only" if security else promotion.decision
    return EvidenceLedger(
        incident_id=incident.incident_id,
        sha=incident.sha,
        required_gates=tuple(sorted(required)),
        entries=entries,
        promotion_decision=decision,
        persisted=False,
        live=False,
        mutates_source=False,
        constraints=(
            "dual_gates_required",
            "append_only",
            "no_persist",
            "no_live_store",
            "no_git_mutation",
            "security_observe_only",
            "subset_required_gates",
            "child_plans_must_match",
        ),
        metadata={
            "classification": incident.classification,
            "fingerprint": incident.fingerprint,
            "source": incident.source,
            "state": incident.state.value,
            "security": security,
            "verification_ready": verification.promotion_ready,
            "live_flag_honored": live_ledger_enabled(),
        },
    )
