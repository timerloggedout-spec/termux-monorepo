#!/usr/bin/env python3
"""Emit sanitized ATES events from trusted GitHub Actions run metadata.

The producer is deliberately offline: GitHub API access belongs to the
workflow observer, while this module converts already-fetched metadata into
the repository's closed throughput-event contract. It never copies prompts,
completions, credentials, comments, or arbitrary payloads.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


EVENTS = {
    "task_started",
    "task_completed",
    "active_window",
    "tool_call",
    "tool_retry",
    "handoff",
}
STATUSES = {"success", "failed", "error", "skipped"}
SHA_LENGTH = 40
# Bolt optimization: Pre-allocate hex character set for O(1) C-level superset validation
HEX_CHARS = frozenset("0123456789abcdef")


def _iso_dt(value: Any) -> tuple[str, datetime]:
    """Require an explicit timezone-bearing ISO-8601 timestamp and return both ISO string and datetime."""
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp must be a non-empty string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"timestamp must include a timezone: {value!r}")
    return parsed.isoformat().replace("+00:00", "Z"), parsed


def _iso(value: Any) -> str:
    """Require an explicit timezone-bearing ISO-8601 timestamp."""
    return _iso_dt(value)[0]


def _sha(value: Any) -> str:
    """Require a full lowercase Git SHA."""
    if not isinstance(value, str) or len(value) != SHA_LENGTH:
        raise ValueError("source_sha must be a 40-character lowercase SHA")
    if not HEX_CHARS.issuperset(value):
        raise ValueError("source_sha must be hexadecimal")
    return value


def _sha256(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character SHA-256 digest")
    if not HEX_CHARS.issuperset(value):
        raise ValueError(f"{field} must be lowercase hexadecimal")
    return value


def _non_negative(value: Any) -> float:
    """Normalize a finite non-negative number."""
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"expected non-negative number, got {value!r}") from exc
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"expected finite non-negative number, got {value!r}")
    return number


def _status(conclusion: Any) -> str:
    """Map an Actions conclusion into the closed telemetry status enum."""
    value = str(conclusion or "").lower()
    if value in {"success", "neutral"}:
        return "success"
    if value in {"skipped"}:
        return "skipped"
    if value in {"failure", "timed_out", "startup_failure"}:
        return "failed"
    if value in {"cancelled", "action_required", "stale"}:
        return "error"
    return "error"


def _event_id(event: Mapping[str, Any]) -> str:
    """Create a deterministic idempotency key without retaining arbitrary text."""
    # Bolt optimization: Fast f-string interpolation instead of generator join
    stable = f"{event.get('source_sha', '')}|{event.get('gha_run_id', '')}|{event.get('gha_run_attempt', '')}|{event.get('agent_id', '')}|{event.get('task_id', '')}|{event.get('event', '')}|{event.get('timestamp', '')}"
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()[:32]


AUTHOR_KINDS = {"agent", "manager", "scout", "orchestrator", "infrastructure", "human", "unknown"}
AUTHOR_METHODS = {"workflow_name_mapping", "invocation_telemetry", "task_boundary_declared", "session_export", "human_attested", "inferred", "unresolved"}


def _author(metadata: Mapping[str, Any]) -> dict[str, Any]:
    """Return a closed, privacy-safe author attribution record.

    Provider/model identity is never inferred from the GitHub account name.
    Missing model/settings/context evidence remains null; fingerprints only.
    """
    raw = metadata.get("author")
    if raw is None:
        raw = {}
    if not isinstance(raw, Mapping):
        raise ValueError("author must be an object")
    allowed = {
        "provider", "model", "adapter", "role", "identity_kind",
        "settings_fingerprint", "context_fingerprint", "attribution_method",
        "confidence", "evidence_refs",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unsupported author fields: {sorted(unknown)}")
    result: dict[str, Any] = {
        "provider": None, "model": None, "adapter": "github-actions",
        "role": None, "identity_kind": "unknown",
        "settings_fingerprint": None, "context_fingerprint": None,
        "attribution_method": "unresolved", "confidence": 0.0, "evidence_refs": [],
    }
    for field in ("provider", "model", "adapter", "role"):
        value = raw.get(field)
        if value is not None:
            if not isinstance(value, str) or not value.strip() or len(value) > 128:
                raise ValueError(f"author.{field} must be a non-empty string up to 128 characters")
            result[field] = value.strip()
    kind = raw.get("identity_kind", result["identity_kind"])
    if kind not in AUTHOR_KINDS:
        raise ValueError("invalid author.identity_kind")
    result["identity_kind"] = kind
    method = raw.get("attribution_method", result["attribution_method"])
    if method not in AUTHOR_METHODS:
        raise ValueError("invalid author.attribution_method")
    result["attribution_method"] = method
    for field in ("settings_fingerprint", "context_fingerprint"):
        value = raw.get(field)
        if value is not None:
            result[field] = _sha256(value, f"author.{field}")
    try:
        confidence = float(raw.get("confidence", 0.0))
    except (TypeError, ValueError) as exc:
        raise ValueError("author.confidence must be between 0 and 1") from exc
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        raise ValueError("author.confidence must be between 0 and 1")
    result["confidence"] = confidence
    refs = raw.get("evidence_refs", [])
    if not isinstance(refs, list) or len(refs) > 20:
        raise ValueError("author.evidence_refs must be a list of at most 20 references")
    if any(not isinstance(ref, str) or not ref.strip() or len(ref) > 256 for ref in refs):
        raise ValueError("author evidence references must be non-empty strings up to 256 characters")
    result["evidence_refs"] = sorted(set(ref.strip() for ref in refs))
    return result


def _base(metadata: Mapping[str, Any], agent_id: str, task_id: str,
          job: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build the common provenance fields for one sanitized event."""
    run = metadata["workflow_run"]
    event = {
        "timestamp": _iso(run["created_at"]),
        "event": "task_started",
        "agent_id": agent_id,
        "task_id": task_id,
        "gha_run_id": int(run["id"]),
        "gha_run_attempt": int(run.get("run_attempt", 1)),
        "source_sha": _sha(run["head_sha"]),
        "author": _author(metadata),
    }
    workflow_name = run.get("name")
    if isinstance(workflow_name, str) and workflow_name.strip():
        event["workflow_name"] = workflow_name.strip()[:256]
    workflow_url = run.get("html_url")
    if isinstance(workflow_url, str) and workflow_url.startswith("https://"):
        event["workflow_run_url"] = workflow_url[:2048]
    workflow_event = run.get("event")
    if isinstance(workflow_event, str) and workflow_event.strip():
        event["workflow_event"] = workflow_event.strip()[:64]
    if job is not None:
        job_id = int(job["id"])
        if job_id > 0:
            event["job_id"] = job_id
        job_name = job.get("name")
        if isinstance(job_name, str) and job_name.strip():
            event["job_name"] = job_name.strip()[:256]
    for source_field in ("pull_request_number", "issue_number"):
        value = metadata.get(source_field)
        if isinstance(value, int) and not isinstance(value, bool) and value > 0:
            event[source_field] = value
    for source_field in ("github_actor", "triggering_actor"):
        value = metadata.get(source_field)
        if value is not None:
            if not isinstance(value, str) or not value.strip() or len(value) > 128:
                raise ValueError(f"{source_field} must be a non-empty string up to 128 characters")
            event[source_field] = value.strip()
    boundary = metadata.get("task_boundary")
    if isinstance(boundary, Mapping):
        for field in ("cohort_id", "task_fingerprint", "task_contract_hash", "environment_fingerprint"):
            value = boundary.get(field)
            if value is not None:
                if field == "cohort_id":
                    if not isinstance(value, str) or not value:
                        raise ValueError("cohort_id must be a non-empty string")
                else:
                    _sha256(value, field)
                event[field] = value
    return event


def build_events(metadata: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Convert trusted run/job metadata into bounded throughput events.

    One Actions job is represented as one bounded task. Complexity is attached
    only when the observer found exactly one associated PR and therefore has a
    concrete structural evidence source. Missing complexity remains missing.
    """
    run = metadata.get("workflow_run")
    if not isinstance(run, Mapping):
        raise ValueError("workflow_run metadata is required")
    agent_id = metadata.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        raise ValueError("agent_id is required")
    source_sha = _sha(run.get("head_sha"))
    jobs = metadata.get("jobs", [])
    if not isinstance(jobs, list):
        raise ValueError("jobs must be a list")

    complexity = metadata.get("task_complexity")
    if complexity is not None:
        if not isinstance(complexity, Mapping):
            raise ValueError("task_complexity must be an object")
        complexity = {
            "additions": _non_negative(complexity.get("additions")),
            "deletions": _non_negative(complexity.get("deletions")),
            "files_changed": _non_negative(complexity.get("files_changed")),
        }

    events: list[dict[str, Any]] = []
    for job in jobs:
        if not isinstance(job, Mapping):
            raise ValueError("job entries must be objects")
        job_id = int(job["id"])
        started = job.get("started_at")
        completed = job.get("completed_at")
        if not started or not completed:
            continue
        task_id = f"gha:{run['id']}:{run.get('run_attempt', 1)}:job:{job_id}"
        start, start_dt = _iso_dt(started)
        finish, finish_dt = _iso_dt(completed)
        conclusion = str(job.get("conclusion") or "").lower()
        # A skipped job did not execute the agent task. Do not turn scheduler
        # control-flow into a fake completed task or throughput observation.
        if conclusion in {"skipped", "action_required"}:
            continue
        status = _status(conclusion)

        started_event = _base(metadata, agent_id, task_id, job)
        started_event.update({"timestamp": start, "event": "task_started"})
        started_event["source_sha"] = source_sha
        events.append(started_event)

        # Bolt optimization: Reuse parsed datetime objects from _iso_dt to avoid duplicate ISO parsing
        duration = max(0.0, (finish_dt - start_dt).total_seconds())

        active_event = _base(metadata, agent_id, task_id, job)
        active_event.update({"timestamp": start, "event": "active_window", "active_seconds": duration})
        active_event["source_sha"] = source_sha
        events.append(active_event)

        completed_event = _base(metadata, agent_id, task_id, job)
        completed_event.update({"timestamp": finish, "event": "task_completed", "status": status})
        completed_event["source_sha"] = source_sha
        if complexity is not None:
            completed_event["metrics"] = dict(complexity)
        events.append(completed_event)

    for event in events:
        event["event_id"] = _event_id(event)
    return events


def validate_event(event: Mapping[str, Any]) -> None:
    """Validate the closed event shape without requiring third-party packages."""
    allowed = {
        "timestamp", "event", "agent_id", "task_id", "tool", "status",
        "duration_ms", "latency_ms", "active_seconds", "inference_seconds",
        "tokens_in", "tokens_out", "complexity_score", "metrics",
        "gha_run_id", "gha_run_attempt", "source_sha", "event_id",
        "cohort_id", "task_fingerprint", "task_contract_hash", "environment_fingerprint",
        "author", "github_actor", "triggering_actor", "workflow_name",
        "workflow_run_url", "workflow_event", "job_id", "job_name",
        "pull_request_number", "issue_number",
    }
    unknown = set(event) - allowed
    if unknown:
        raise ValueError(f"unsupported telemetry fields: {sorted(unknown)}")
    if not isinstance(event.get("timestamp"), str) or not event["timestamp"]:
        raise ValueError("event timestamp is required")
    if event.get("event") not in EVENTS:
        raise ValueError("invalid event type")
    if event.get("status") is not None and event["status"] not in STATUSES:
        raise ValueError("invalid status")
    if event.get("agent_id") is not None and not isinstance(event["agent_id"], str):
        raise ValueError("agent_id must be a string")
    if event.get("task_id") is not None and not isinstance(event["task_id"], str):
        raise ValueError("task_id must be a string")
    if event.get("gha_run_id") is not None and int(event["gha_run_id"]) < 1:
        raise ValueError("gha_run_id must be positive")
    if event.get("gha_run_attempt") is not None and int(event["gha_run_attempt"]) < 1:
        raise ValueError("gha_run_attempt must be positive")
    if event.get("source_sha") is not None:
        _sha(event["source_sha"])
    if event.get("author") is not None:
        if not isinstance(event["author"], Mapping):
            raise ValueError("author must be an object")
        normalized = _author({"author": event["author"]})
        if dict(event["author"]) != normalized:
            raise ValueError("author must be normalized and contain only contract fields")
    for field, limit in (("github_actor", 128), ("triggering_actor", 128),
                         ("workflow_name", 256), ("job_name", 256), ("workflow_event", 64)):
        if event.get(field) is not None and (not isinstance(event[field], str) or not event[field] or len(event[field]) > limit):
            raise ValueError(f"{field} must be a non-empty string up to {limit} characters")
    if event.get("workflow_run_url") is not None and (
        not isinstance(event["workflow_run_url"], str) or not event["workflow_run_url"].startswith("https://")
        or len(event["workflow_run_url"]) > 2048
    ):
        raise ValueError("workflow_run_url must be an HTTPS URL up to 2048 characters")
    if event.get("job_id") is not None and (not isinstance(event["job_id"], int) or event["job_id"] < 1):
        raise ValueError("job_id must be a positive integer")
    for field in ("pull_request_number", "issue_number"):
        if event.get(field) is not None and (not isinstance(event[field], int) or isinstance(event[field], bool) or event[field] < 1):
            raise ValueError(f"{field} must be a positive integer")
    if event.get("metrics") is not None:
        metrics = event["metrics"]
        if not isinstance(metrics, Mapping):
            raise ValueError("metrics must be an object")
        if set(metrics) - {"additions", "deletions", "files_changed", "complexity_score"}:
            raise ValueError("unsupported structural metric")
        for value in metrics.values():
            _non_negative(value)


def write_events(events: list[dict[str, Any]], output: Path) -> None:
    """Validate and write deterministic JSONL evidence."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for event in events:
            validate_event(event)
            handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")


def main() -> int:
    """Run the metadata-to-JSONL producer."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    events = build_events(metadata)
    write_events(events, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
