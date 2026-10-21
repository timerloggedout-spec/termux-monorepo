"""SHE P0.13 — attestation replay verifier (observer-only).

Recomputes the P0.12 digest from a planned EvidenceLedger and compares it
to a supplied Attestation. This module plans the replay verdict. It does
not write a store, call the network, sign, or mutate git.

Live replay remains a later slice behind SHE_REPLAY_LIVE=1.
stdlib-only.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from she.attest import Attestation, digest_mapping, plan_attestation
from she.incident import Incident, IncidentState
from she.ledger import EvidenceLedger, plan_ledger
from she.verify import DUAL_GATES

VERDICTS = frozenset({"match", "mismatch", "observe-only", "hold"})

_TERMINAL_BLOCK = {
    IncidentState.QUARANTINED,
    IncidentState.ABANDONED,
}


class ReplayError(ValueError):
    """Invalid replay construction or policy violation."""


def live_replay_enabled() -> bool:
    """Live replay remains gated and unused in P0.13."""
    return os.environ.get("SHE_REPLAY_LIVE", "").strip() == "1"


def _is_security(incident: Incident) -> bool:
    classification = (incident.classification or "").lower()
    fp = incident.fingerprint or ""
    return classification.startswith("dependabot-") or fp.startswith("dependabot:")


@dataclass(frozen=True)
class ReplayVerdict:
    """Observer-only comparison of a planned attestation against a recomputed digest."""

    incident_id: str
    sha: str
    required_gates: tuple[str, ...]
    expected_digest: str
    observed_digest: str
    verdict: str
    promotion_decision: str = "hold"
    live: bool = False
    persisted: bool = False
    signed: bool = False
    mutates_source: bool = False
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.incident_id:
            raise ReplayError("incident_id required")
        if not self.sha:
            raise ReplayError("sha required")
        needed = set(self.required_gates)
        if not DUAL_GATES.issubset(needed):
            raise ReplayError("dual gates repo-gate + termux-smoke must be required")
        if self.verdict not in VERDICTS:
            raise ReplayError(f"unsupported verdict: {self.verdict!r}")
        if len(self.expected_digest) != 64 or len(self.observed_digest) != 64:
            raise ReplayError("digests must be sha256 hex")
        if self.live:
            raise ReplayError("P0.13 planner cannot be live")
        if self.signed:
            raise ReplayError("P0.13 planner cannot sign")
        if self.persisted:
            raise ReplayError("P0.13 planner cannot persist")
        if self.mutates_source:
            raise ReplayError("P0.13 planner cannot mutate source")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "sha": self.sha,
            "required_gates": list(self.required_gates),
            "expected_digest": self.expected_digest,
            "observed_digest": self.observed_digest,
            "verdict": self.verdict,
            "promotion_decision": self.promotion_decision,
            "live": self.live,
            "persisted": self.persisted,
            "signed": self.signed,
            "mutates_source": self.mutates_source,
            "constraints": list(self.constraints),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> ReplayVerdict:
        gates = tuple(str(x) for x in (data.get("required_gates") or ()))
        return cls(
            incident_id=str(data["incident_id"]),
            sha=str(data.get("sha") or ""),
            required_gates=gates,
            expected_digest=str(data.get("expected_digest") or ""),
            observed_digest=str(data.get("observed_digest") or ""),
            verdict="hold",
            promotion_decision="hold",
            live=False,
            persisted=False,
            signed=False,
            mutates_source=False,
            constraints=tuple(str(x) for x in (data.get("constraints") or ("from_mapping_fail_closed",))),
            metadata=dict(data.get("metadata") or {}),
        )


def plan_replay(
    incident: Incident,
    *,
    attestation: Attestation | None = None,
    ledger: EvidenceLedger | None = None,
    check_results: Mapping[str, Mapping[str, Any]] | None = None,
) -> ReplayVerdict:
    """Plan an observer-only attestation replay. Does not persist or sign.

    Dual gates always required (subset). Security/Dependabot stay observe-only.
    from_mapping is fail-closed (verdict=hold, live=False).
    """
    if incident.state in _TERMINAL_BLOCK:
        raise ReplayError(
            f"replay not applicable for terminal state {incident.state.value}"
        )

    ledger = ledger or plan_ledger(incident, check_results=check_results)
    if ledger.incident_id != incident.incident_id:
        raise ReplayError("ledger incident_id must match incident")
    if ledger.sha != incident.sha:
        raise ReplayError("ledger sha must match incident sha")

    attestation = attestation or plan_attestation(
        incident, ledger=ledger, check_results=check_results
    )
    if attestation.incident_id != incident.incident_id:
        raise ReplayError("attestation incident_id must match incident")
    if attestation.sha != incident.sha:
        raise ReplayError("attestation sha must match incident sha")

    required = set(ledger.required_gates) | set(attestation.required_gates) | set(DUAL_GATES)
    security = _is_security(incident)
    if security:
        required |= {"security-checks"}
    if not DUAL_GATES.issubset(required):
        raise ReplayError("dual gates repo-gate + termux-smoke must be required")

    payload = {
        "incident_id": incident.incident_id,
        "sha": incident.sha,
        "required_gates": sorted(required),
        "ledger": ledger.to_mapping(),
    }
    observed = digest_mapping(payload)
    expected = attestation.digest
    matched = observed == expected

    if security:
        verdict = "observe-only"
        decision = "observe-only"
    elif not matched:
        verdict = "mismatch"
        decision = "hold"
    else:
        verdict = "match"
        decision = attestation.promotion_decision

    return ReplayVerdict(
        incident_id=incident.incident_id,
        sha=incident.sha,
        required_gates=tuple(sorted(required)),
        expected_digest=expected,
        observed_digest=observed,
        verdict=verdict,
        promotion_decision=decision,
        live=False,
        persisted=False,
        signed=False,
        mutates_source=False,
        constraints=(
            "dual_gates_required",
            "canonical_sha256",
            "no_sign",
            "no_persist",
            "no_live_store",
            "no_git_mutation",
            "security_observe_only",
            "subset_required_gates",
            "child_ledger_must_match",
            "child_attestation_must_match",
        ),
        metadata={
            "classification": incident.classification,
            "fingerprint": incident.fingerprint,
            "source": incident.source,
            "state": incident.state.value,
            "security": security,
            "matched": matched,
            "attestation_decision": attestation.promotion_decision,
            "live_flag_honored": live_replay_enabled(),
        },
    )
