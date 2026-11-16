#!/usr/bin/env python3
"""Normalize GitHub Actions lifecycle payloads for the live admin graph.

Only bounded execution metadata is emitted. Logs, comments, prompts,
completions, credentials, tool arguments and arbitrary payloads are excluded.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = "timerloggedout-spec/termux-monorepo"

def build_event(payload: dict[str, Any], event_name: str) -> dict[str, Any]:
    if event_name == "workflow_run":
        run = payload.get("workflow_run") or {}
        run_id = int(run["id"])
        attempt = int(run.get("run_attempt") or 1)
        status = str(run.get("conclusion") if run.get("status") == "completed" else run.get("status") or "unknown")
        occurred = run.get("updated_at") or run.get("run_started_at") or run.get("created_at")
        base = {"kind":"workflow","event":"workflow_"+status,"status":status,
                "workflow":run.get("name") or "GitHub Actions","run_id":run_id,
                "run_attempt":attempt,"head_sha":run.get("head_sha"),
                "url":run.get("html_url"),"occurred_at":occurred}
    elif event_name == "workflow_job":
        job = payload.get("workflow_job") or {}
        run_id = int(job["run_id"])
        attempt = int(job.get("run_attempt") or 1)
        status = str(job.get("conclusion") if job.get("status") == "completed" else job.get("status") or "unknown")
        occurred = job.get("completed_at") or job.get("started_at") or job.get("created_at")
        base = {"kind":"job","event":"job_"+status,"status":status,
                "workflow":(payload.get("workflow") or {}).get("name") or "GitHub Actions",
                "job":job.get("name") or "unnamed job","job_id":int(job["id"]),
                "run_id":run_id,"run_attempt":attempt,"head_sha":job.get("head_sha"),
                "url":job.get("html_url") or job.get("run_url"),"occurred_at":occurred}
    else:
        raise ValueError("unsupported event: "+event_name)
    if not occurred:
        occurred = datetime.now(timezone.utc).isoformat()
        base["occurred_at"] = occurred
    base["repo"] = (payload.get("repository") or {}).get("full_name") or REPO
    base["actor"] = (payload.get("sender") or {}).get("login")
    identity = "|".join(str(base.get(k) or "") for k in
                        ("kind","run_id","run_attempt","job_id","event","occurred_at"))
    base["id"] = hashlib.sha256(identity.encode()).hexdigest()
    return base

def build_events(payload: dict[str, Any], event_name: str) -> list[dict[str, Any]]:
    if event_name == "workflow_snapshot":
        runs = payload.get("workflow_runs") or []
        if not isinstance(runs, list) or len(runs) > 100:
            raise ValueError("workflow snapshot must contain at most 100 runs")
        return [build_event({"repository":{"full_name":REPO},"workflow_run":run},"workflow_run")
                for run in runs]
    return [build_event(payload, event_name)]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-file", required=True)
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = json.loads(Path(args.event_file).read_text(encoding="utf-8"))
    events = build_events(payload, args.event_name)
    if any(event["repo"] != REPO for event in events):
        raise SystemExit("event repository mismatch")
    Path(args.output).write_text(json.dumps({"events":events},separators=(",",":"))+"\n",encoding="utf-8")
    print("normalized "+str(len(events))+" runtime lifecycle event(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
