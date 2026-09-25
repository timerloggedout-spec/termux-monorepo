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


def _iso(value: Any) -> str:
    """Require an explicit timezone-bearing ISO-8601 timestamp."""
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp must be a non-empty string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"timestamp must include a timezone: {value!r}")
    return parsed.isoformat().replace("+00:00", "Z")


def _sha(value: Any) -> str:
    """Require a full lowercase Git SHA."""
    if not isinstance(value, str) or len(value) != SHA_LENGTH:
        raise ValueError("source_sha must be a 40-character lowercase SHA")
    if any(ch not in "0123456789abcdef" for ch in value):
        raise ValueError("source_sha must be hexadecimal")
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
    stable = "|".join(str(event.get(key, "")) for key in (
        "source_sha", "gha_run_id", "gha_run_attempt", "agent_id",
        "task_id", "event", "timestamp",
    ))
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()[:32]


def _base(metadata: Mapping[str, Any], agent_id: str, task_id: str) -> dict[str, Any]:
    """Build the common provenance fields for one sanitized event."""
    run = metadata["workflow_run"]
    return {
        "timestamp": _iso(run["created_at"]),
        "event": "task_started",
        "agent_id": agent_id,
        "task_id": task_id,
        "gha_run_id": int(run["id"]),
        "gha_run_attempt": int(run.get("run_attempt", 1)),
        "source_sha": _sha(run["head_sha"]),
    }


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
        start = _iso(started)
        finish = _iso(completed)
        status = _status(job.get("conclusion"))

        started_event = _base(metadata, agent_id, task_id)
        started_event.update({"timestamp": start, "event": "task_started"})
        started_event["source_sha"] = source_sha
        events.append(started_event)

        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        finish_dt = datetime.fromisoformat(finish.replace("Z", "+00:00"))
        duration = max(0.0, (finish_dt - start_dt).total_seconds())

        active_event = _base(metadata, agent_id, task_id)
        active_event.update({"timestamp": start, "event": "active_window", "active_seconds": duration})
        active_event["source_sha"] = source_sha
        events.append(active_event)

        completed_event = _base(metadata, agent_id, task_id)
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
    if not events:
        raise SystemExit("no complete job timing evidence was available")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
