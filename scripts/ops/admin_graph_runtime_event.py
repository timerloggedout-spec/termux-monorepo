#!/usr/bin/env python3
"""Normalize bounded task-routing and GitHub Actions lifecycle metadata."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = "timerloggedout-spec/termux-monorepo"

def _workflow_event(payload: dict[str, Any], event_name: str) -> dict[str, Any]:
    if event_name == "workflow_run":
        run = payload.get("workflow_run") or {}
        run_id = int(run["id"])
        attempt = int(run.get("run_attempt") or 1)
        status = str(run.get("conclusion") if run.get("status") == "completed" else run.get("status") or "unknown")
        occurred = run.get("updated_at") or run.get("run_started_at") or run.get("created_at")
        base = {"kind": "workflow", "event": "workflow_" + status, "status": status,
                "workflow": run.get("name") or "GitHub Actions", "run_id": run_id,
                "run_attempt": attempt, "head_sha": run.get("head_sha"),
                "url": run.get("html_url"), "occurred_at": occurred}
    elif event_name == "workflow_job":
        job = payload.get("workflow_job") or {}
        run_id = int(job["run_id"])
        attempt = int(job.get("run_attempt") or 1)
        status = str(job.get("conclusion") if job.get("status") == "completed" else job.get("status") or "unknown")
        occurred = job.get("completed_at") or job.get("started_at") or job.get("created_at")
        base = {"kind": "job", "event": "job_" + status, "status": status,
                "workflow": (payload.get("workflow") or {}).get("name") or "GitHub Actions",
                "job": job.get("name") or "unnamed job", "job_id": int(job["id"]),
                "run_id": run_id, "run_attempt": attempt, "head_sha": job.get("head_sha"),
                "url": job.get("html_url") or job.get("run_url"), "occurred_at": occurred}
    else:
        raise ValueError("unsupported workflow event: " + event_name)
    if not base["occurred_at"]:
        base["occurred_at"] = datetime.now(timezone.utc).isoformat()
    base["repo"] = (payload.get("repository") or {}).get("full_name") or REPO
    base["actor"] = (payload.get("sender") or {}).get("login")
    if base["kind"] == "workflow":
        base["id"] = "workflow:" + str(run_id) + ":" + str(attempt) + ":" + status + ":" + str(base["occurred_at"])
    else:
        identity = "|".join(str(base.get(k) or "") for k in
                            ("kind", "run_id", "run_attempt", "job_id", "event", "occurred_at"))
        base["id"] = hashlib.sha256(identity.encode()).hexdigest()
    return base

def _route_event(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any] | None:
    comment = payload.get("comment") or {}
    body = str(comment.get("body") or "")
    producer_claim = "PRODUCER CLAIM" in body
    executor_marker = "DISPATCH EXECUTOR CLAIM" in body
    role_match = re.search(r"\[MUSEai\]@\{role:\{([^}]+)\}\}", body)
    route_role = role_match.group(1).strip() if role_match else ""
    arm_match = re.search(r"^\s*-\s*arm:\s*([^\s(]+)(?:\s*\(([^)]+)\))?", body, re.M | re.I)
    executor_claim = executor_marker or route_role == "dispatch-executor" or arm_match is not None
    if not producer_claim and not executor_claim:
        return None
    issue = payload.get("issue") or {}
    issue_url = issue.get("html_url")
    if issue.get("number") is not None:
        issue_number = int(issue["number"])
    else:
        issue_match = re.search(r"/issues/(\d+)$", str(comment.get("issue_url") or ""))
        if not issue_match:
            return None
        issue_number = int(issue_match.group(1))
        issue_url = "https://github.com/" + REPO + "/issues/" + str(issue_number)
    comment_id = int(comment["id"])
    run_id = int(context["run_id"])
    run_attempt = int(context.get("run_attempt") or 1)
    if not route_role:
        return None

    provider = arm_id = model = dispatch_id = None
    source = "producer_claim"
    if executor_claim:
        source = "dispatch_executor_claim"
        if arm_match:
            arm_id = arm_match.group(1).strip()[:120]
            model = (arm_match.group(2) or "").strip()[:160] or None
        dispatch_match = re.search(r"^\s*-\s*dispatch_id:\s*([^\r\n]+)", body, re.M | re.I)
        dispatch_id = dispatch_match.group(1).strip()[:160] if dispatch_match else None
    else:
        match = re.search(r"^\s*-\s*resolved provider:\s*([^\r\n]+)", body, re.M | re.I)
        provider = match.group(1).strip()[:120] if match else None
    occurred = comment.get("created_at") or datetime.now(timezone.utc).isoformat()
    route_payload = {"task_ref": "#" + str(issue_number), "issue_number": issue_number,
                     "source_comment_id": comment_id, "source": source,
                     "route_role": route_role[:120], "provider": provider,
                     "arm_id": arm_id, "model": model, "dispatch_id": dispatch_id}
    return {"id": "route:" + str(issue_number) + ":" + str(comment_id),
            "kind": "route", "event": "task_routed", "status": "routed",
            "workflow": "QUE task routing", "job": route_role[:120],
            "step": (provider or arm_id or "route selected")[:160],
            "repo": (payload.get("repository") or {}).get("full_name") or REPO,
            "run_id": run_id, "run_attempt": run_attempt,
            "head_sha": context.get("head_sha"), "url": issue_url,
            "occurred_at": occurred, "actor": (payload.get("sender") or {}).get("login"),
            "payload": route_payload}

def build_event(payload: dict[str, Any], event_name: str,
                context: dict[str, Any] | None = None) -> dict[str, Any]:
    if event_name == "issue_comment":
        event = _route_event(payload, context or {})
        if event is None:
            raise ValueError("issue comment does not contain a recognized task claim")
        return event
    return _workflow_event(payload, event_name)

def build_events(payload: dict[str, Any], event_name: str,
                 context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    if event_name == "workflow_snapshot":
        runs = payload.get("workflow_runs") or []
        if not isinstance(runs, list) or len(runs) > 100:
            raise ValueError("workflow snapshot must contain at most 100 runs")
        return [_workflow_event({"repository": {"full_name": REPO}, "workflow_run": run}, "workflow_run")
                for run in runs]
    if event_name == "runtime_snapshot":
        runs = payload.get("workflow_runs") or []
        comments = payload.get("issue_comments") or []
        if not isinstance(runs, list) or len(runs) > 100:
            raise ValueError("runtime snapshot must contain at most 100 workflow runs")
        if not isinstance(comments, list) or len(comments) > 2000:
            raise ValueError("runtime snapshot must contain at most 2000 issue comments")
        events = [_workflow_event({"repository": {"full_name": REPO}, "workflow_run": run}, "workflow_run")
                  for run in runs]
        for comment in comments:
            user = comment.get("user") or {}
            wrapper = {
                "repository": {"full_name": REPO},
                "sender": {"login": user.get("login")},
                "comment": comment,
            }
            route_event = _route_event(wrapper, context or {})
            if route_event:
                events.append(route_event)
        return events
    if event_name == "issue_comment":
        try:
            return [build_event(payload, event_name, context)]
        except ValueError as exc:
            if str(exc) == "issue comment does not contain a recognized task claim":
                return []
            raise
    return [build_event(payload, event_name, context)]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-file", required=True)
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--run-attempt", default="1")
    parser.add_argument("--head-sha")
    parser.add_argument("--github-output")
    args = parser.parse_args()
    payload = json.loads(Path(args.event_file).read_text(encoding="utf-8"))
    context = {"run_id": args.run_id, "run_attempt": args.run_attempt, "head_sha": args.head_sha}
    if args.event_name in {"issue_comment", "runtime_snapshot"} and not args.run_id:
        raise SystemExit("route normalization requires the observer workflow run id")
    events = build_events(payload, args.event_name, context)
    if any(event["repo"] != REPO for event in events):
        raise SystemExit("event repository mismatch")
    Path(args.output).write_text(json.dumps({"events": events}, separators=(",", ":")) + "\n", encoding="utf-8")
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as handle:
            handle.write("event_count=" + str(len(events)) + "\n")
    print("normalized " + str(len(events)) + " runtime event(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
