"""SHE P0.14 — evidence publication planner (observer-only).

Binds a P0.13 ReplayVerdict to an inspectable publication contract.
This module plans the publication action. It does not write a store,
call the network, sign, or mutate git.

Live publication remains a later slice behind SHE_PUBLISH_LIVE=1.
stdlib-only.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from she.incident import Incident, IncidentState
from she.ledger import EvidenceLedger, plan_ledger
from she.replay import ReplayVerdict, plan_replay
from she.verify import DUAL_GATES

ACTIONS = frozenset({"hold", "publish-plan", "observe-only", "quarantine-plan"})

_TERMINAL_BLOCK = {
    IncidentState.QUARANTINED,
    IncidentState.ABANDONED,
}


class PublishError(ValueError):
    """Invalid publication construction or policy violation."""


def live_publish_enabled() -> bool:
    """Live publication remains gated and unused in P0.14."""
    return os.environ.get("SHE_PUBLISH_LIVE", "").strip() == "1"


def _is_security(incident: Incident) -> bool:
    classification = (incident.classification or "").lower()
    fp = incident.fingerprint or ""
    return classification.startswith("dependabot-") or fp.startswith("dependabot:")


@dataclass(frozen=True)
class PublicationPlan:
    """Observer-only publication contract bound to a replay verdict."""

    incident_id: str
    sha: str
    required_gates: tuple[str, ...]
    replay_verdict: str
    digest: str
    action: str
    promotion_decision: str = "hold"
    live: bool = False
    persisted: bool = False
    signed: bool = False
    published: bool = False
    mutates_source: bool = False
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.incident_id:
            raise PublishError("incident_id required")
        if not self.sha:
            raise PublishError("sha required")
        needed = set(self.required_gates)
        if not DUAL_GATES.issubset(needed):
            raise PublishError("dual gates repo-gate + termux-smoke must be required")
        if self.action not in ACTIONS:
            raise PublishError(f"unsupported action: {self.action!r}")
        if len(self.digest) != 64:
            raise PublishError("digest must be sha256 hex")
        if self.live:
            raise PublishError("P0.14 planner cannot be live")
        if self.signed:
            raise PublishError("P0.14 planner cannot sign")
        if self.persisted:
            raise PublishError("P0.14 planner cannot persist")
        if self.published:
            raise PublishError("P0.14 planner cannot publish")
        if self.mutates_source:
            raise PublishError("P0.14 planner cannot mutate source")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "sha": self.sha,
            "required_gates": list(self.required_gates),
            "replay_verdict": self.replay_verdict,
            "digest": self.digest,
            "action": self.action,
            "promotion_decision": self.promotion_decision,
            "live": self.live,
            "persisted": self.persisted,
            "signed": self.signed,
            "published": self.published,
            "mutates_source": self.mutates_source,
            "constraints": list(self.constraints),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> PublicationPlan:
        gates = tuple(str(x) for x in (data.get("required_gates") or ()))
        return cls(
            incident_id=str(data["incident_id"]),
            sha=str(data.get("sha") or ""),
            required_gates=gates,
            replay_verdict=str(data.get("replay_verdict") or "hold"),
            digest=str(data.get("digest") or ""),
            action="hold",
            promotion_decision="hold",
            live=False,
            persisted=False,
            signed=False,
            published=False,
            mutates_source=False,
            constraints=tuple(str(x) for x in (data.get("constraints") or ("from_mapping_fail_closed",))),
            metadata=dict(data.get("metadata") or {}),
        )


def plan_publication(
    incident: Incident,
    *,
    replay: ReplayVerdict | None = None,
    ledger: EvidenceLedger | None = None,
    check_results: Mapping[str, Mapping[str, Any]] | None = None,
) -> PublicationPlan:
    """Plan an observer-only publication contract. Does not publish or persist.

    Dual gates always required (subset). Security/Dependabot stay observe-only.
    from_mapping is fail-closed (action=hold, published=False, live=False).
    """
    if incident.state in _TERMINAL_BLOCK:
        raise PublishError(
            f"publication not applicable for terminal state {incident.state.value}"
        )

    ledger = ledger or plan_ledger(incident, check_results=check_results)
    if ledger.incident_id != incident.incident_id:
        raise PublishError("ledger incident_id must match incident")
    if ledger.sha != incident.sha:
        raise PublishError("ledger sha must match incident sha")

    replay = replay or plan_replay(
        incident, ledger=ledger, check_results=check_results
    )
    if replay.incident_id != incident.incident_id:
        raise PublishError("replay incident_id must match incident")
    if replay.sha != incident.sha:
        raise PublishError("replay sha must match incident sha")

    required = set(ledger.required_gates) | set(replay.required_gates) | set(DUAL_GATES)
    security = _is_security(incident)
    if security:
        required |= {"security-checks"}
    if not DUAL_GATES.issubset(required):
        raise PublishError("dual gates repo-gate + termux-smoke must be required")

    if security:
        action = "observe-only"
        decision = "observe-only"
    elif replay.verdict == "mismatch":
        action = "quarantine-plan"
        decision = "hold"
    elif replay.verdict == "match" and replay.promotion_decision == "promote":
        action = "publish-plan"
        decision = "promote"
    else:
        action = "hold"
        decision = replay.promotion_decision if replay.promotion_decision != "promote" else "hold"

    return PublicationPlan(
        incident_id=incident.incident_id,
        sha=incident.sha,
        required_gates=tuple(sorted(required)),
        replay_verdict=replay.verdict,
        digest=replay.observed_digest,
        action=action,
        promotion_decision=decision,
        live=False,
        persisted=False,
        signed=False,
        published=False,
        mutates_source=False,
        constraints=(
            "dual_gates_required",
            "canonical_sha256",
            "no_sign",
            "no_persist",
            "no_live_store",
            "no_publish",
            "no_git_mutation",
            "security_observe_only",
            "subset_required_gates",
            "child_ledger_must_match",
            "child_replay_must_match",
        ),
        metadata={
            "classification": incident.classification,
            "fingerprint": incident.fingerprint,
            "source": incident.source,
            "state": incident.state.value,
            "security": security,
            "replay_decision": replay.promotion_decision,
            "live_flag_honored": live_publish_enabled(),
        },
    )
