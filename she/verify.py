"""SHE P0.6 — verification planner (healing evidence, no live dispatch).

Selects repository, Termux-scope, domain, security, and regression checks
into an explicit evidence contract for an incident. This module plans checks;
it does not run Actions, mutate git, or call the network.

Live execution remains a later slice. Results may be recorded later via
`apply_check_results` without changing the planned gate set.
stdlib-only.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from she.incident import Incident, IncidentState
from she.sandbox import SandboxPlan

VERIFICATION_GATES: frozenset[str] = frozenset(
    {
        "repo-gate",
        "termux-smoke",
        "domain-tests",
        "security-checks",
        "regression-invariants",
    }
)

BASE_GATES: frozenset[str] = frozenset({"repo-gate"})
TERMUX_SCOPE_GATES: frozenset[str] = frozenset({"termux-smoke"})

CHECK_OUTCOMES: frozenset[str] = frozenset(
    {"pending", "pass", "fail", "inconclusive"}
)

_TERMINAL_BLOCK = {
    IncidentState.LEARNED,
    IncidentState.QUARANTINED,
    IncidentState.ABANDONED,
}


class VerificationError(ValueError):
    """Invalid verification construction or policy violation."""


@dataclass(frozen=True)
class CheckSpec:
    """One planned verification check."""

    gate: str
    required: bool
    outcome: str = "pending"
    evidence_uri: str = ""
    notes: str = ""

    def to_mapping(self) -> dict[str, Any]:
        return {
            "gate": self.gate,
            "required": self.required,
            "outcome": self.outcome,
            "evidence_uri": self.evidence_uri,
            "notes": self.notes,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> CheckSpec:
        gate = str(data["gate"])
        if gate not in VERIFICATION_GATES:
            raise VerificationError(f"unknown gate: {gate!r}")
        outcome = str(data.get("outcome") or "pending")
        if outcome not in CHECK_OUTCOMES:
            raise VerificationError(f"unknown outcome: {outcome!r}")
        return cls(
            gate=gate,
            required=bool(data.get("required", True)),
            outcome=outcome,
            evidence_uri=str(data.get("evidence_uri") or ""),
            notes=str(data.get("notes") or ""),
        )


def _validate_checks(checks: tuple[CheckSpec, ...], metadata: Mapping[str, Any] | None = None) -> None:
    if not checks:
        raise VerificationError("verification plan cannot have empty checks")
    seen: set[str] = set()
    for spec in checks:
        if spec.gate not in VERIFICATION_GATES:
            raise VerificationError(f"unknown gate: {spec.gate!r}")
        if spec.gate in seen:
            raise VerificationError(f"duplicate gate: {spec.gate!r}")
        seen.add(spec.gate)
        if spec.outcome not in CHECK_OUTCOMES:
            raise VerificationError(f"unknown outcome: {spec.outcome!r}")
    required = {c.gate for c in checks if c.required}
    if not BASE_GATES.issubset(required):
        raise VerificationError("repo-gate must be required")
    termux_related = bool((metadata or {}).get("termux_related"))
    if termux_related and not TERMUX_SCOPE_GATES.issubset(required):
        raise VerificationError("termux-smoke must be required for Termux scope")
    if not termux_related and TERMUX_SCOPE_GATES.intersection(required):
        raise VerificationError("termux-smoke is reserved for Termux scope")


@dataclass(frozen=True)
class VerificationPlan:
    """Explicit healing-evidence contract for one incident."""

    incident_id: str
    sha: str
    checks: tuple[CheckSpec, ...]
    promotion_ready: bool = False
    live: bool = False
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_checks(self.checks, self.metadata)
        if self.promotion_ready and self.live:
            raise VerificationError("live plans cannot be promotion_ready")

    def required_gates(self) -> frozenset[str]:
        return frozenset(c.gate for c in self.checks if c.required)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "sha": self.sha,
            "checks": [c.to_mapping() for c in self.checks],
            "promotion_ready": self.promotion_ready,
            "live": self.live,
            "constraints": list(self.constraints),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> VerificationPlan:
        raw_checks = data.get("checks") or []
        if not isinstance(raw_checks, list):
            raise VerificationError("checks must be a list")
        checks = tuple(CheckSpec.from_mapping(c) for c in raw_checks)
        return cls(
            incident_id=str(data["incident_id"]),
            sha=str(data.get("sha") or ""),
            checks=checks,
            promotion_ready=False,
            live=False,
            constraints=tuple(str(x) for x in (data.get("constraints") or ())),
            metadata=dict(data.get("metadata") or {}),
        )


def _is_security(incident: Incident) -> bool:
    classification = (incident.classification or "").lower()
    fp = incident.fingerprint or ""
    return classification.startswith("dependabot-") or fp.startswith("dependabot:")


def _is_termux(incident: Incident) -> bool:
    source = (incident.source or "").lower()
    fp = (incident.fingerprint or "").lower()
    classification = (incident.classification or "").lower()
    provenance = (incident.event_provenance or "").lower()
    return any("termux" in value or "android-device" in value
               for value in (source, fp, classification, provenance))


def plan_verification(
    incident: Incident,
    *,
    sandbox: SandboxPlan | None = None,
) -> VerificationPlan:
    """Plan healing-evidence checks. Does not execute workflows.

    The repository gate is always required. Termux smoke is required only
    for Termux runtime/device incidents. Security incidents also require
    security-checks. Domain and regression checks remain required.
    """
    if incident.state in _TERMINAL_BLOCK:
        raise VerificationError(
            f"verification not applicable for terminal state {incident.state.value}"
        )

    security = _is_security(incident)
    termux_related = _is_termux(incident)
    checks = [
        CheckSpec(gate="repo-gate", required=True),
        *(
            [CheckSpec(gate="termux-smoke", required=True,
                       notes="Termux runtime/device scope")]
            if termux_related
            else []
        ),
        CheckSpec(gate="domain-tests", required=True),
        CheckSpec(
            gate="security-checks",
            required=security,
            notes=(
                "required for dependabot/security fingerprints"
                if security
                else "advisory"
            ),
        ),
        CheckSpec(gate="regression-invariants", required=True),
    ]
    required = {c.gate for c in checks if c.required}
    if not BASE_GATES.issubset(required):
        raise VerificationError("repo-gate must remain required")

    if sandbox is not None:
        evidence_dir = sandbox.evidence_dir
        sandbox_branch = sandbox.branch
    else:
        evidence_dir = f".she/evidence/{incident.incident_id}"
        sandbox_branch = ""
    return VerificationPlan(
        incident_id=incident.incident_id,
        sha=incident.sha,
        checks=tuple(checks),
        promotion_ready=False,
        live=False,
        constraints=(
            "repo_gate_required",
            "termux_smoke_scope_conditional",
            "no_live_dispatch",
            "http_200_is_not_pass",
            "append_only_evidence",
            "subset_required_gates",
        ),
        metadata={
            "classification": incident.classification,
            "fingerprint": incident.fingerprint,
            "source": incident.source,
            "termux_related": termux_related,
            "state": incident.state.value,
            "evidence_dir": evidence_dir,
            "sandbox_branch": sandbox_branch,
            "required_gates": sorted(required),
        },
    )


def apply_check_results(
    plan: VerificationPlan,
    results: Mapping[str, Mapping[str, Any]],
) -> VerificationPlan:
    """Record outcomes onto an existing plan. Cannot drop required gates."""
    _validate_checks(plan.checks, plan.metadata)
    by_gate = {c.gate: c for c in plan.checks}
    updated: list[CheckSpec] = []
    for gate, spec in by_gate.items():
        payload = results.get(gate) or {}
        outcome = str(payload.get("outcome") or spec.outcome)
        if outcome not in CHECK_OUTCOMES:
            raise VerificationError(f"unknown outcome for {gate}: {outcome!r}")
        updated.append(
            CheckSpec(
                gate=spec.gate,
                required=spec.required,
                outcome=outcome,
                evidence_uri=str(payload.get("evidence_uri") or spec.evidence_uri),
                notes=str(payload.get("notes") or spec.notes),
            )
        )
    _validate_checks(tuple(updated), plan.metadata)
    required_pass = all(c.outcome == "pass" for c in updated if c.required)
    any_fail = any(c.outcome == "fail" for c in updated if c.required)
    promotion_ready = required_pass and not any_fail and not plan.live
    return VerificationPlan(
        incident_id=plan.incident_id,
        sha=plan.sha,
        checks=tuple(updated),
        promotion_ready=promotion_ready,
        live=False,
        constraints=plan.constraints,
        metadata=dict(plan.metadata),
    )


def summarize_results(plan: VerificationPlan) -> str:
    """Compact evidence line for incident.verification_results."""
    parts = [f"{c.gate}={c.outcome}" for c in plan.checks]
    ready = "ready" if plan.promotion_ready else "blocked"
    return f"she.verify:{ready}:" + ",".join(parts)
