"""SHE P0.12 — evidence attestation digest (observer-only).

Binds a planned EvidenceLedger to a deterministic SHA-256 digest over a
canonical JSON mapping. This module plans the attestation. It does not
write a store, call the network, or mutate git.

Live signing remains a later slice behind SHE_ATTEST_LIVE=1.
stdlib-only.
"""
from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from she.incident import Incident, IncidentState
from she.ledger import EvidenceLedger, plan_ledger
from she.verify import DUAL_GATES

DIGEST_ALGO = "sha256"
_TERMINAL_BLOCK = {IncidentState.QUARANTINED, IncidentState.ABANDONED}

class AttestError(ValueError):
    """Invalid attestation construction or policy violation."""

def live_attest_enabled() -> bool:
    return os.environ.get("SHE_ATTEST_LIVE", "").strip() == "1"

def _is_security(incident: Incident) -> bool:
    classification = (incident.classification or "").lower()
    fp = incident.fingerprint or ""
    return classification.startswith("dependabot-") or fp.startswith("dependabot:")

def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")

def digest_mapping(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()

@dataclass(frozen=True)
class Attestation:
    incident_id: str
    sha: str
    required_gates: tuple[str, ...]
    digest: str
    algorithm: str = DIGEST_ALGO
    promotion_decision: str = "hold"
    signed: bool = False
    live: bool = False
    persisted: bool = False
    mutates_source: bool = False
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.incident_id: raise AttestError("incident_id required")
        if not self.sha: raise AttestError("sha required")
        if not DUAL_GATES.issubset(set(self.required_gates)): raise AttestError("dual gates repo-gate + termux-smoke must be required")
        if self.algorithm != DIGEST_ALGO: raise AttestError(f"unsupported algorithm: {self.algorithm!r}")
        if len(self.digest) != 64: raise AttestError("digest must be sha256 hex")
        if self.live: raise AttestError("P0.12 planner cannot be live")
        if self.signed: raise AttestError("P0.12 planner cannot sign")
        if self.persisted: raise AttestError("P0.12 planner cannot persist")
        if self.mutates_source: raise AttestError("P0.12 planner cannot mutate source")

    def to_mapping(self) -> dict[str, Any]:
        return {"incident_id": self.incident_id, "sha": self.sha, "required_gates": list(self.required_gates), "digest": self.digest, "algorithm": self.algorithm, "promotion_decision": self.promotion_decision, "signed": self.signed, "live": self.live, "persisted": self.persisted, "mutates_source": self.mutates_source, "constraints": list(self.constraints), "metadata": dict(self.metadata)}

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "Attestation":
        return cls(incident_id=str(data["incident_id"]), sha=str(data.get("sha") or ""), required_gates=tuple(str(x) for x in (data.get("required_gates") or ())), digest=str(data.get("digest") or ""), promotion_decision="hold", signed=False, live=False, persisted=False, mutates_source=False, constraints=tuple(str(x) for x in (data.get("constraints") or ("from_mapping_fail_closed",))), metadata=dict(data.get("metadata") or {}))

def plan_attestation(incident: Incident, *, ledger: EvidenceLedger | None = None, check_results: Mapping[str, Mapping[str, Any]] | None = None) -> Attestation:
    if incident.state in _TERMINAL_BLOCK: raise AttestError(f"attestation not applicable for terminal state {incident.state.value}")
    ledger = ledger or plan_ledger(incident, check_results=check_results)
    if ledger.incident_id != incident.incident_id or ledger.sha != incident.sha: raise AttestError("ledger identity/SHA must match incident")
    required = set(ledger.required_gates) | DUAL_GATES
    security = _is_security(incident)
    if security: required.add("security-checks")
    payload = {"incident_id": incident.incident_id, "sha": incident.sha, "required_gates": sorted(required), "ledger": ledger.to_mapping()}
    return Attestation(incident_id=incident.incident_id, sha=incident.sha, required_gates=tuple(sorted(required)), digest=digest_mapping(payload), promotion_decision="observe-only" if security else ledger.promotion_decision, constraints=("dual_gates_required","canonical_sha256","no_sign","no_persist","no_live_store","no_git_mutation","security_observe_only","subset_required_gates","child_ledger_must_match"), metadata={"classification": incident.classification, "fingerprint": incident.fingerprint, "source": incident.source, "state": incident.state.value, "security": security, "ledger_decision": ledger.promotion_decision, "live_flag_honored": live_attest_enabled()})
