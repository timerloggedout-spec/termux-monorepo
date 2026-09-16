"""Structured, restart-safe job and result envelopes for the Termux hub."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping
from uuid import UUID

from .policy import ApprovalLevel, PolicyError, authorize, get_capability


class JobValidationError(ValueError):
    """Raised when an untrusted job envelope fails hub validation."""


_SECRET_PATTERNS = (
    re.compile(r"(?i)(?:ghp|github_pat|tskey|sk|AIza)[-_a-z0-9]{12,}"),
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s]+"),
    re.compile(r"(?i)(client_secret\s*[:=]\s*)[^\s,]+"),
)


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def parse_timestamp(value: str, field_name: str) -> datetime:
    """Parse a required ISO-8601 timestamp and normalize it to UTC."""
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise JobValidationError(f"{field_name} must be a valid ISO-8601 timestamp") from exc
    if timestamp.tzinfo is None:
        raise JobValidationError(f"{field_name} must include a timezone")
    return timestamp.astimezone(UTC)


def redact(value: str) -> str:
    """Remove common credential shapes from untrusted process output."""
    redacted = value
    for pattern in _SECRET_PATTERNS:
        if pattern.groups:
            redacted = pattern.sub(r"\1[REDACTED]", redacted)
        else:
            redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


@dataclass(frozen=True)
class Job:
    """A validated request to execute exactly one named local capability."""

    job_id: str
    issued_at: datetime
    expires_at: datetime
    requested_by: str
    capability: str
    arguments: Mapping[str, Any] = field(default_factory=dict)
    approval_level: ApprovalLevel = ApprovalLevel.OBSERVE
    approval_id: str | None = None
    schema_version: int = 1

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any], *, now: datetime | None = None) -> "Job":
        """Validate a JSON-compatible job mapping without executing anything."""
        if not isinstance(payload, Mapping):
            raise JobValidationError("Job payload must be a JSON object")
        required = {"job_id", "issued_at", "expires_at", "requested_by", "capability", "approval_level"}
        missing = sorted(required - set(payload))
        if missing:
            raise JobValidationError(f"Missing required job field(s): {', '.join(missing)}")
        unknown = set(payload) - {
            "job_id", "issued_at", "expires_at", "requested_by", "capability", "arguments",
            "approval_level", "approval_id", "schema_version",
        }
        if unknown:
            raise JobValidationError(f"Unknown job field(s): {', '.join(sorted(unknown))}")
        try:
            UUID(str(payload["job_id"]))
        except (ValueError, TypeError, AttributeError) as exc:
            raise JobValidationError("job_id must be a UUID") from exc
        requested_by = payload["requested_by"]
        capability = payload["capability"]
        arguments = payload.get("arguments", {})
        if not isinstance(requested_by, str) or not requested_by.strip():
            raise JobValidationError("requested_by must be a non-empty string")
        if not isinstance(capability, str) or not capability.strip():
            raise JobValidationError("capability must be a non-empty string")
        if not isinstance(arguments, Mapping):
            raise JobValidationError("arguments must be an object")
        issued_at = parse_timestamp(str(payload["issued_at"]), "issued_at")
        expires_at = parse_timestamp(str(payload["expires_at"]), "expires_at")
        reference_now = now or utc_now()
        if expires_at <= issued_at:
            raise JobValidationError("expires_at must be later than issued_at")
        if reference_now > expires_at:
            raise JobValidationError("Job has expired")
        if issued_at > reference_now:
            raise JobValidationError("Job issued_at cannot be in the future")
        if expires_at - issued_at > __import__("datetime").timedelta(hours=24):
            raise JobValidationError("Job lifetime cannot exceed 24 hours")
        try:
            approval = ApprovalLevel.parse(str(payload["approval_level"]))
            spec = get_capability(capability)
            authorize(spec, approval, payload.get("approval_id"))
        except PolicyError as exc:
            raise JobValidationError(str(exc)) from exc
        schema_version = payload.get("schema_version", 1)
        if schema_version != 1:
            raise JobValidationError("Unsupported schema_version")
        return cls(
            job_id=str(payload["job_id"]),
            issued_at=issued_at,
            expires_at=expires_at,
            requested_by=requested_by.strip(),
            capability=capability,
            arguments=dict(arguments),
            approval_level=approval,
            approval_id=payload.get("approval_id"),
            schema_version=schema_version,
        )

    def canonical_json(self) -> str:
        """Produce a stable representation for auditing and idempotency records."""
        return json.dumps(
            {
                "schema_version": self.schema_version,
                "job_id": self.job_id,
                "issued_at": self.issued_at.isoformat(),
                "expires_at": self.expires_at.isoformat(),
                "requested_by": self.requested_by,
                "capability": self.capability,
                "arguments": self.arguments,
                "approval_level": self.approval_level.name,
                "approval_id": self.approval_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @property
    def digest(self) -> str:
        """Return a content digest that links results to the validated request."""
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ResultEnvelope:
    """A redacted and auditable result for one local capability execution."""

    job_id: str
    job_digest: str
    capability: str
    success: bool
    exit_code: int | None
    stdout: str
    stderr: str
    started_at: datetime
    finished_at: datetime

    @property
    def result_digest(self) -> str:
        payload = {
            "job_id": self.job_id,
            "job_digest": self.job_digest,
            "capability": self.capability,
            "success": self.success,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_mapping(self) -> dict[str, Any]:
        """Return a JSON-safe, secret-redacted result object."""
        return {
            "schema_version": 1,
            "job_id": self.job_id,
            "job_digest": self.job_digest,
            "capability": self.capability,
            "success": self.success,
            "exit_code": self.exit_code,
            "stdout": redact(self.stdout),
            "stderr": redact(self.stderr),
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "result_digest": self.result_digest,
        }
