#!/usr/bin/env python3
"""Emit a sanitized ATES receipt for a completed GitHub Actions workflow run."""
from __future__ import annotations

import argparse
import json
import math
import os
from datetime import datetime
from pathlib import Path


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_event(payload: dict) -> dict:
    run = payload.get("workflow_run", payload)
    conclusion = run.get("conclusion")
    status = {
        "success": "success",
        "failure": "failed",
        "cancelled": "skipped",
        "timed_out": "failed",
        "action_required": "failed",
        "neutral": "skipped",
        "skipped": "skipped",
        "startup_failure": "failed",
    }.get(conclusion, "error")
    created = run.get("created_at")
    updated = run.get("updated_at")
    duration_ms = None
    if created and updated:
        duration_ms = max(0.0, (parse_time(updated) - parse_time(created)).total_seconds() * 1000)
        if not math.isfinite(duration_ms):
            duration_ms = None
    sha = run.get("head_sha")
    run_id = run.get("id")
    attempt = run.get("run_attempt")
    event = {
        "timestamp": updated or created,
        "event": "task_completed",
        "agent_id": run.get("name") or "github-actions-workflow",
        "task_id": f"gha:{run_id}:attempt:{attempt}",
        "status": status,
        "gha_run_id": run_id,
        "gha_run_attempt": attempt,
    }
    if duration_ms is not None:
        event["duration_ms"] = round(duration_ms, 3)
    if isinstance(sha, str) and len(sha) == 40 and all(c in "0123456789abcdef" for c in sha):
        event["source_sha"] = sha
    return event


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", default=os.environ.get("GITHUB_EVENT_PATH"))
    parser.add_argument("--output", default="ates-run-receipt.jsonl")
    args = parser.parse_args()
    if not args.event:
        parser.error("--event or GITHUB_EVENT_PATH is required")
    payload = json.loads(Path(args.event).read_text(encoding="utf-8"))
    event = build_event(payload)
    if not event.get("timestamp") or not event.get("gha_run_id") or not event.get("gha_run_attempt"):
        raise SystemExit("workflow payload is missing timestamp/run id/attempt; refusing synthetic receipt")
    Path(args.output).write_text(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"event": event["event"], "status": event["status"], "run_id": event["gha_run_id"], "attempt": event["gha_run_attempt"]}))


if __name__ == "__main__":
    main()
