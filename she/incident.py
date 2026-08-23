"""SHE P0.1 — durable incident identity and lifecycle state machine.

Matches docs/architecture/SELF-HEALING-ENGINE.md core state machine:

  DETECTED -> TRIAGED -> DIAGNOSING -> … -> RESOLVED / LEARNED
  plus QUARANTINED, ESCALATED, ROLLED_BACK, ABANDONED.

stdlib-only. No network. JSON-serializable for evidence stores.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Mapping
from uuid import uuid4


class IncidentError(ValueError):
    """Invalid incident construction or illegal state transition."""


class IncidentState(str, Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    DIAGNOSING = "DIAGNOSING"
    RESEARCH = "RESEARCH"
    PLANNED = "PLANNED"
    DISPATCHED = "DISPATCHED"
    REMEDIATING = "REMEDIATING"
    VERIFYING = "VERIFYING"
    FAILED = "FAILED"
    PROMOTING = "PROMOTING"
    RESOLVED = "RESOLVED"
    LEARNED = "LEARNED"
    QUARANTINED = "QUARANTINED"
    ESCALATED = "ESCALATED"
    ROLLED_BACK = "ROLLED_BACK"
    ABANDONED = "ABANDONED"


TERMINAL_STATES: frozenset[IncidentState] = frozenset(
    {
        IncidentState.LEARNED,
        IncidentState.QUARANTINED,
        IncidentState.ESCALATED,
        IncidentState.ROLLED_BACK,
        IncidentState.ABANDONED,
    }
)

# Directed edges of the core state machine (+ safe escalations).
ALLOWED_TRANSITIONS: dict[IncidentState, frozenset[IncidentState]] = {
    IncidentState.DETECTED: frozenset(
        {
            IncidentState.TRIAGED,
            IncidentState.QUARANTINED,
            IncidentState.ABANDONED,
        }
    ),
    IncidentState.TRIAGED: frozenset(
        {
            IncidentState.DIAGNOSING,
            IncidentState.PLANNED,  # known-fix short path
            IncidentState.ESCALATED,
            IncidentState.ABANDONED,
        }
    ),
    IncidentState.DIAGNOSING: frozenset(
        {
            IncidentState.RESEARCH,
            IncidentState.PLANNED,
            IncidentState.ESCALATED,
            IncidentState.ABANDONED,
        }
    ),
    IncidentState.RESEARCH: frozenset(
        {
            IncidentState.PLANNED,
            IncidentState.ESCALATED,
            IncidentState.ABANDONED,
        }
    ),
    IncidentState.PLANNED: frozenset(
        {
            IncidentState.DISPATCHED,
            IncidentState.ESCALATED,
            IncidentState.ABANDONED,
        }
    ),
    IncidentState.DISPATCHED: frozenset(
        {
            IncidentState.REMEDIATING,
            IncidentState.FAILED,
            IncidentState.ESCALATED,
        }
    ),
    IncidentState.REMEDIATING: frozenset(
        {
            IncidentState.VERIFYING,
            IncidentState.FAILED,
            IncidentState.ROLLED_BACK,
            IncidentState.ESCALATED,
        }
    ),
    IncidentState.VERIFYING: frozenset(
        {
            IncidentState.PROMOTING,
            IncidentState.FAILED,
            IncidentState.ROLLED_BACK,
        }
    ),
    IncidentState.FAILED: frozenset(
        {
            IncidentState.DIAGNOSING,  # re-diagnose
            IncidentState.PLANNED,  # retry with revised plan
            IncidentState.ESCALATED,
            IncidentState.ABANDONED,
            IncidentState.ROLLED_BACK,
        }
    ),
    IncidentState.PROMOTING: frozenset(
        {
            IncidentState.RESOLVED,
            IncidentState.ROLLED_BACK,
            IncidentState.ESCALATED,
        }
    ),
    IncidentState.RESOLVED: frozenset({IncidentState.LEARNED, IncidentState.ROLLED_BACK}),
    IncidentState.LEARNED: frozenset(),
    IncidentState.QUARANTINED: frozenset(),
    IncidentState.ESCALATED: frozenset({IncidentState.TRIAGED, IncidentState.ABANDONED}),
    IncidentState.ROLLED_BACK: frozenset(
        {IncidentState.DIAGNOSING, IncidentState.ABANDONED, IncidentState.LEARNED}
    ),
    IncidentState.ABANDONED: frozenset(),
}


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
    if isinstance(value, str):
        text = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    raise IncidentError(f"invalid datetime: {value!r}")


@dataclass(frozen=True)
class Transition:
    from_state: IncidentState
    to_state: IncidentState
    at: datetime
    by: str
    reason: str = ""

    def to_mapping(self) -> dict[str, Any]:
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "at": self.at.isoformat().replace("+00:00", "Z"),
            "by": self.by,
            "reason": self.reason,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> Transition:
        return cls(
            from_state=IncidentState(data["from_state"]),
            to_state=IncidentState(data["to_state"]),
            at=_parse_dt(data["at"]),
            by=str(data.get("by") or "unknown"),
            reason=str(data.get("reason") or ""),
        )


@dataclass
class Incident:
    """Durable SHE incident record (control-plane SSOT fragment).

    Required fields mirror SELF-HEALING-ENGINE.md § Incident requirements.
    """

    incident_id: str
    state: IncidentState
    created_at: datetime
    updated_at: datetime
    source: str
    event_provenance: str
    repository: str
    ref: str
    sha: str
    severity: str = "medium"
    classification: str = "unknown"
    evidence_refs: list[str] = field(default_factory=list)
    authority_scope: list[str] = field(default_factory=list)
    allowed_actions: list[str] = field(default_factory=list)
    selected_capabilities: list[str] = field(default_factory=list)
    selected_workers: list[str] = field(default_factory=list)
    remediation_plan: str = ""
    verification_results: list[str] = field(default_factory=list)
    promotion_result: str = ""
    learning_record: str = ""
    fingerprint: str = ""
    history: list[Transition] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_terminal(self) -> bool:
        return self.state in TERMINAL_STATES

    def can_transition(self, to_state: IncidentState) -> bool:
        return to_state in ALLOWED_TRANSITIONS.get(self.state, frozenset())

    def transition(
        self,
        to_state: IncidentState,
        *,
        by: str,
        reason: str = "",
        at: datetime | None = None,
    ) -> Transition:
        if self.is_terminal and to_state not in ALLOWED_TRANSITIONS.get(
            self.state, frozenset()
        ):
            raise IncidentError(
                f"incident {self.incident_id} is terminal in {self.state.value}"
            )
        if not self.can_transition(to_state):
            raise IncidentError(
                f"illegal transition {self.state.value} -> {to_state.value} "
                f"for incident {self.incident_id}"
            )
        when = at or _utc_now()
        edge = Transition(
            from_state=self.state,
            to_state=to_state,
            at=when,
            by=by,
            reason=reason,
        )
        self.state = to_state
        self.updated_at = when
        self.history.append(edge)
        return edge

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "state": self.state.value,
            "created_at": self.created_at.isoformat().replace("+00:00", "Z"),
            "updated_at": self.updated_at.isoformat().replace("+00:00", "Z"),
            "source": self.source,
            "event_provenance": self.event_provenance,
            "repository": self.repository,
            "ref": self.ref,
            "sha": self.sha,
            "severity": self.severity,
            "classification": self.classification,
            "evidence_refs": list(self.evidence_refs),
            "authority_scope": list(self.authority_scope),
            "allowed_actions": list(self.allowed_actions),
            "selected_capabilities": list(self.selected_capabilities),
            "selected_workers": list(self.selected_workers),
            "remediation_plan": self.remediation_plan,
            "verification_results": list(self.verification_results),
            "promotion_result": self.promotion_result,
            "learning_record": self.learning_record,
            "fingerprint": self.fingerprint,
            "history": [t.to_mapping() for t in self.history],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> Incident:
        required = (
            "incident_id",
            "state",
            "created_at",
            "updated_at",
            "source",
            "event_provenance",
            "repository",
            "ref",
            "sha",
        )
        missing = [k for k in required if k not in data]
        if missing:
            raise IncidentError(f"missing required fields: {', '.join(missing)}")
        history_raw = data.get("history") or []
        if not isinstance(history_raw, list):
            raise IncidentError("history must be a list")
        return cls(
            incident_id=str(data["incident_id"]),
            state=IncidentState(data["state"]),
            created_at=_parse_dt(data["created_at"]),
            updated_at=_parse_dt(data["updated_at"]),
            source=str(data["source"]),
            event_provenance=str(data["event_provenance"]),
            repository=str(data["repository"]),
            ref=str(data["ref"]),
            sha=str(data["sha"]),
            severity=str(data.get("severity") or "medium"),
            classification=str(data.get("classification") or "unknown"),
            evidence_refs=[str(x) for x in (data.get("evidence_refs") or [])],
            authority_scope=[str(x) for x in (data.get("authority_scope") or [])],
            allowed_actions=[str(x) for x in (data.get("allowed_actions") or [])],
            selected_capabilities=[
                str(x) for x in (data.get("selected_capabilities") or [])
            ],
            selected_workers=[str(x) for x in (data.get("selected_workers") or [])],
            remediation_plan=str(data.get("remediation_plan") or ""),
            verification_results=[
                str(x) for x in (data.get("verification_results") or [])
            ],
            promotion_result=str(data.get("promotion_result") or ""),
            learning_record=str(data.get("learning_record") or ""),
            fingerprint=str(data.get("fingerprint") or ""),
            history=[Transition.from_mapping(t) for t in history_raw],
            metadata=dict(data.get("metadata") or {}),
        )

    @classmethod
    def create(
        cls,
        *,
        source: str,
        event_provenance: str,
        repository: str,
        ref: str,
        sha: str,
        severity: str = "medium",
        classification: str = "unknown",
        evidence_refs: list[str] | None = None,
        authority_scope: list[str] | None = None,
        allowed_actions: list[str] | None = None,
        fingerprint: str = "",
        metadata: dict[str, Any] | None = None,
        incident_id: str | None = None,
        at: datetime | None = None,
    ) -> Incident:
        when = at or _utc_now()
        return cls(
            incident_id=incident_id or str(uuid4()),
            state=IncidentState.DETECTED,
            created_at=when,
            updated_at=when,
            source=source,
            event_provenance=event_provenance,
            repository=repository,
            ref=ref,
            sha=sha,
            severity=severity,
            classification=classification,
            evidence_refs=list(evidence_refs or []),
            authority_scope=list(authority_scope or []),
            allowed_actions=list(allowed_actions or []),
            fingerprint=fingerprint,
            metadata=dict(metadata or {}),
        )
