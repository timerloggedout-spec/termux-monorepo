"""SHE P0.7 — repair-PR planner (inspectable L1 contract, no live mutation).

Produces the metadata contract for a later autonomous repair PR:
incident linkage, sandbox branch, evidence URIs, required tests,
rollback SHA, and dual-gate promotion constraints.

This module plans. It does not create branches, commits, or pull requests.
Live materialization is a later slice behind SHE_REPAIR_PR_LIVE=1.
stdlib-only. No network.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from she.incident import Incident, IncidentState
from she.sandbox import SandboxPlan, plan_repair_sandbox
from she.verify import DUAL_GATES, VerificationPlan, plan_verification

REQUIRED_TESTS: frozenset[str] = frozenset(
    {"repo-gate", "termux-smoke", "domain-tests"}
)

_TERMINAL_BLOCK = {
    IncidentState.LEARNED,
    IncidentState.QUARANTINED,
    IncidentState.ABANDONED,
}


class RepairPRError(ValueError):
    """Invalid repair-PR construction or policy violation."""


def live_repair_pr_enabled() -> bool:
    """Live PR creation remains gated and unused in P0.7."""
    return os.environ.get("SHE_REPAIR_PR_LIVE", "").strip() == "1"


def _is_security(incident: Incident) -> bool:
    classification = (incident.classification or "").lower()
    fp = incident.fingerprint or ""
    return classification.startswith("dependabot-") or fp.startswith("dependabot:")


@dataclass(frozen=True)
class RepairPRPlan:
    """Inspectable L1 repair-PR contract for one incident."""

    incident_id: str
    sha: str
    branch: str
    base_ref: str
    title: str
    body: str
    evidence_uris: tuple[str, ...]
    required_tests: tuple[str, ...]
    rollback_sha: str
    promotion_ready: bool = False
    live: bool = False
    mutates_source: bool = False
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        needed = set(self.required_tests)
        if self.rollback_sha != self.sha:
            raise RepairPRError("rollback_sha must match sha")
        if not DUAL_GATES.issubset(needed):
            raise RepairPRError("dual gates repo-gate + termux-smoke must be required tests")
        if not self.incident_id:
            raise RepairPRError("incident_id required")
        if not self.branch.startswith("she/repair/"):
            raise RepairPRError("repair PR branch must stay in she/repair/ namespace")
        if self.live and self.promotion_ready:
            raise RepairPRError("live plans cannot be promotion_ready")
        if self.mutates_source:
            raise RepairPRError("P0.7 planner cannot mutate source")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "sha": self.sha,
            "branch": self.branch,
            "base_ref": self.base_ref,
            "title": self.title,
            "body": self.body,
            "evidence_uris": list(self.evidence_uris),
            "required_tests": list(self.required_tests),
            "rollback_sha": self.rollback_sha,
            "promotion_ready": self.promotion_ready,
            "live": self.live,
            "mutates_source": self.mutates_source,
            "constraints": list(self.constraints),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> RepairPRPlan:
        tests = tuple(str(x) for x in (data.get("required_tests") or ()))
        sha = str(data.get("sha") or "")
        return cls(
            incident_id=str(data["incident_id"]),
            sha=sha,
            branch=str(data["branch"]),
            base_ref=str(data.get("base_ref") or "refs/heads/master"),
            title=str(data.get("title") or ""),
            body=str(data.get("body") or ""),
            evidence_uris=tuple(str(x) for x in (data.get("evidence_uris") or ())),
            required_tests=tests,
            rollback_sha=str(data.get("rollback_sha") or sha),
            promotion_ready=False,
            live=False,
            mutates_source=False,
            constraints=tuple(str(x) for x in (data.get("constraints") or ())),
            metadata=dict(data.get("metadata") or {}),
        )


def _draft_title(incident: Incident) -> str:
    fp = incident.fingerprint or incident.classification or "incident"
    return f"fix(she): repair {incident.incident_id} ({fp})"


def _draft_body(
    incident: Incident,
    sandbox: SandboxPlan,
    verification: VerificationPlan,
) -> str:
    gates = ",".join(sorted(verification.required_gates()))
    return (
        f"## SHE L1 repair plan\n\n"
        f"Incident: `{incident.incident_id}`\n"
        f"Fingerprint: `{incident.fingerprint}`\n"
        f"Classification: `{incident.classification}`\n"
        f"Source SHA (rollback): `{incident.sha}`\n"
        f"Sandbox branch: `{sandbox.branch}`\n"
        f"Evidence dir: `{sandbox.evidence_dir}`\n"
        f"Required gates: `{gates}`\n\n"
        f"Observer-only planner. Live PR creation is not enabled.\n"
        f"Refs: #294 #175\n"
        f"Agent-Identity: Grok (Administrator)\n"
    )


def _bind_child_plans(
    incident: Incident,
    sandbox: SandboxPlan,
    verification: VerificationPlan,
) -> None:
    if sandbox.incident_id != incident.incident_id:
        raise RepairPRError("sandbox incident_id must match incident")
    if sandbox.base_sha != incident.sha:
        raise RepairPRError("sandbox base_sha must match incident sha")
    if verification.incident_id != incident.incident_id:
        raise RepairPRError("verification incident_id must match incident")
    if verification.sha != incident.sha:
        raise RepairPRError("verification sha must match incident sha")


def plan_repair_pr(
    incident: Incident,
    *,
    sandbox: SandboxPlan | None = None,
    verification: VerificationPlan | None = None,
) -> RepairPRPlan:
    """Plan an inspectable repair PR. Does not open a pull request.

    Dual gates are always required tests (subset). Security/Dependabot
    incidents stay observe-only (no write repair PR). Terminal states
    are rejected. promotion_ready stays false until a later executor
    records passing verification against the current SHA.
    """
    if incident.state in _TERMINAL_BLOCK:
        raise RepairPRError(
            f"repair PR not applicable for terminal state {incident.state.value}"
        )
    if _is_security(incident):
        raise RepairPRError("security/dependabot incidents are observe-only")

    sandbox = sandbox or plan_repair_sandbox(incident)
    verification = verification or plan_verification(incident, sandbox=sandbox)
    _bind_child_plans(incident, sandbox, verification)
    tests = tuple(sorted(REQUIRED_TESTS | verification.required_gates()))
    if not DUAL_GATES.issubset(tests):
        raise RepairPRError("dual gates must remain required tests")

    evidence = (
        f"file://{sandbox.evidence_dir}/incident.json",
        f"file://{sandbox.evidence_dir}/verification.txt",
    )
    return RepairPRPlan(
        incident_id=incident.incident_id,
        sha=incident.sha,
        branch=sandbox.branch,
        base_ref=sandbox.base_ref,
        title=_draft_title(incident),
        body=_draft_body(incident, sandbox, verification),
        evidence_uris=evidence,
        required_tests=tests,
        rollback_sha=incident.sha,
        promotion_ready=False,
        live=False,
        mutates_source=False,
        constraints=(
            "dual_gates_required",
            "no_live_pr",
            "isolated_branch_only",
            "rollback_sha_bound",
            "http_200_is_not_pass",
            "append_only_evidence",
        ),
        metadata={
            "classification": incident.classification,
            "fingerprint": incident.fingerprint,
            "source": incident.source,
            "state": incident.state.value,
            "repository": incident.repository,
            "credential_profile": sandbox.credential_profile,
            "verification_ready": verification.promotion_ready,
            "live_flag_honored": live_repair_pr_enabled(),
        },
    )
