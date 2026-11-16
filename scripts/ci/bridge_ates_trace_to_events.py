#!/usr/bin/env python3
"""Bridge privacy-safe ATES runtime spans into the canonical throughput event schema."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

_SHA = re.compile(r"^[0-9a-f]{40}$")
_ALLOWED = {"task_started", "task_completed", "tool_call", "tool_retry", "handoff", "active_window"}
_STATUS = {"ok": "success", "success": "success", "error": "error", "failed": "failed", "skipped": "skipped"}


def _identifier(namespace: str, value: str) -> str:
    """Retain stable grouping without exporting arbitrary source metadata text."""
    digest = hashlib.sha256((namespace + "\0" + value).encode("utf-8")).hexdigest()
    return f"ates-{namespace}:{digest}"


def convert_record(record: dict, *, run_id: int | None = None, attempt: int | None = None, source_sha: str | None = None) -> dict | None:
    """Convert one trace span; unknown span kinds are ignored, never guessed."""
    kind = record.get("kind")
    if kind not in _ALLOWED:
        return None
    timestamp_key = "started_at" if kind == "task_started" else "ended_at"
    timestamp = record.get(timestamp_key) or record.get("started_at") or record.get("ended_at")
    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("recognized span is missing a timestamp")
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timezone required")
        timestamp = parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except ValueError:
        raise ValueError("recognized span requires a timezone-aware timestamp") from None
    status = _STATUS.get(record.get("status", "ok"))
    if status is None:
        raise ValueError("unrecognized span status")
    task_id = record.get("benchmark_case_id")
    if not isinstance(task_id, str) or not task_id:
        raise ValueError("recognized span is missing benchmark_case_id")
    event = {"timestamp": timestamp, "event": kind, "task_id": _identifier("task", task_id), "status": status}
    role = record.get("role")
    if isinstance(role, str) and role:
        event["agent_id"] = _identifier("role", role)
    if kind in {"tool_call", "tool_retry"}:
        tool = record.get("tool")
        if not isinstance(tool, str) or not tool:
            raise ValueError(f"{kind} span is missing tool label")
        event["tool"] = _identifier("tool", tool)
    duration = record.get("duration_ms")
    if duration is not None:
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or not math.isfinite(duration) or duration < 0:
            raise ValueError("duration_ms must be a finite non-negative number")
        event["duration_ms"] = duration
    if run_id is not None:
        event["gha_run_id"] = run_id
    if attempt is not None:
        event["gha_run_attempt"] = attempt
    if source_sha is not None:
        if not _SHA.fullmatch(source_sha):
            raise ValueError("source_sha must be a 40-character lowercase Git SHA")
        event["source_sha"] = source_sha
    return event


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="runtime trace JSONL")
    parser.add_argument("--output", default="ates-throughput-events.jsonl")
    parser.add_argument("--run-id", type=int)
    parser.add_argument("--attempt", type=int)
    parser.add_argument("--source-sha")
    args = parser.parse_args()
    if (args.run_id is None) != (args.attempt is None):
        parser.error("--run-id and --attempt must be supplied together")
    if args.run_id is not None and (args.run_id < 1 or args.attempt < 1):
        parser.error("run ID and attempt must be positive integers")
    converted = []
    for line_number, line in enumerate(Path(args.input).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError("record must be a JSON object")
            event = convert_record(record, run_id=args.run_id, attempt=args.attempt, source_sha=args.source_sha)
        except (json.JSONDecodeError, ValueError) as exc:
            raise SystemExit(f"{args.input}:{line_number}: {exc}") from exc
        if event is not None:
            converted.append(event)
    Path(args.output).write_text("".join(json.dumps(e, sort_keys=True, separators=(",", ":")) + "\n" for e in converted), encoding="utf-8")
    print(json.dumps({"converted": len(converted), "ignored": "unsupported span kinds omitted"}))


if __name__ == "__main__":
    main()
