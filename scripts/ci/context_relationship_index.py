#!/usr/bin/env python3
"""Build a deterministic, redacted temporal context/lead-lag index from GitHub event data."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_gh(*args: str) -> object:
    env = os.environ.copy()
    env.setdefault("GH_PAGER", "cat")
    return json.loads(subprocess.check_output(["gh", *args], env=env, text=True))


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def seconds_between(a: str | None, b: str | None) -> float | None:
    left, right = parse_time(a), parse_time(b)
    if not left or not right:
        return None
    return max(0.0, (right - left).total_seconds())


def classify_event(event: dict) -> str:
    kind = event.get("event") or event.get("type") or "unknown"
    action = event.get("action") or ""
    return f"{kind}:{action}" if action else str(kind)


def optional_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except ValueError as exc:
        raise SystemExit(f"invalid integer: {value!r}") from exc
    if parsed < 1:
        raise SystemExit("number must be positive")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="evaluation-results/context-relationship-index.json")
    parser.add_argument("--pr")
    parser.add_argument("--issue")
    parser.add_argument("--head-sha", default=os.getenv("GITHUB_SHA", ""))
    args = parser.parse_args()

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    event = json.loads(Path(event_path).read_text()) if event_path and Path(event_path).exists() else {}
    observed_at = now()

    pr_number = optional_int(args.pr) or event.get("pull_request", {}).get("number")
    issue_number = optional_int(args.issue) or event.get("issue", {}).get("number")
    head_sha = args.head_sha or event.get("pull_request", {}).get("head", {}).get("sha") or event.get("after", "")

    lead_events = [{
        "kind": "github_event",
        "class": classify_event(event),
        "observed_at": observed_at,
        "event_name": os.getenv("GITHUB_EVENT_NAME", "unknown"),
        "run_id": os.getenv("GITHUB_RUN_ID"),
        "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "head_sha": head_sha,
    }]
    lag_events = []

    if repo and pr_number:
        try:
            pr = run_gh("pr", "view", str(pr_number), "--repo", repo,
                        "--json", "number,headRefOid,createdAt,updatedAt,mergedAt,closedAt,state")
            lead_events.append({"kind": "pull_request", "number": pr["number"], "observed_at": observed_at,
                                "source_sha": pr.get("headRefOid"), "created_at": pr.get("createdAt")})
            if pr.get("mergedAt"):
                lag_events.append({"kind": "merge", "observed_at": pr["mergedAt"], "source_sha": pr.get("headRefOid")})
            elif pr.get("closedAt"):
                lag_events.append({"kind": "close", "observed_at": pr["closedAt"], "source_sha": pr.get("headRefOid")})
        except Exception as exc:
            lead_events.append({"kind": "pr_query_warning", "observed_at": observed_at, "message": str(exc)[:300]})

    if repo and (pr_number or issue_number):
        number = pr_number or issue_number
        try:
            comments = run_gh("api", f"repos/{repo}/issues/{number}/comments", "--paginate")
            if isinstance(comments, list):
                for comment in comments[-100:]:
                    lead_events.append({
                        "kind": "comment",
                        "id": comment.get("id"),
                        "created_at": comment.get("created_at"),
                        "updated_at": comment.get("updated_at"),
                        "author": comment.get("user", {}).get("login"),
                    })
        except Exception as exc:
            lead_events.append({"kind": "comment_query_warning", "observed_at": observed_at, "message": str(exc)[:300]})

    if repo and head_sha:
        try:
            checks = run_gh("api", f"repos/{repo}/commits/{head_sha}/check-runs", "--paginate")
            if isinstance(checks, dict):
                checks = checks.get("check_runs", [])
            for check in checks or []:
                lag_events.append({
                    "kind": "check",
                    "name": check.get("name"),
                    "status": check.get("status"),
                    "conclusion": check.get("conclusion"),
                    "started_at": check.get("started_at"),
                    "completed_at": check.get("completed_at"),
                    "run_id": check.get("id"),
                })
        except Exception as exc:
            lag_events.append({"kind": "check_query_warning", "observed_at": observed_at, "message": str(exc)[:300]})

    pairs = []
    for lead in lead_events:
        lead_time = lead.get("observed_at") or lead.get("created_at")
        candidates = []
        for lag in lag_events:
            lag_time = lag.get("observed_at") or lag.get("completed_at") or lag.get("started_at")
            delta = seconds_between(lead_time, lag_time)
            if delta is not None and delta >= 0:
                candidates.append((delta, lag))
        if candidates:
            delta, lag = min(candidates, key=lambda item: item[0])
            pairs.append({
                "lead_kind": lead.get("kind"),
                "lag_kind": lag.get("kind"),
                "lead_at": lead_time,
                "lag_at": lag.get("observed_at") or lag.get("completed_at") or lag.get("started_at"),
                "elapsed_seconds": delta,
                "relationship_status": "temporal-correlation",
                "causal_claim": False,
            })

    result = {
        "schema": "context-relationship-index/v1",
        "observed_at": observed_at,
        "repository": repo,
        "source_sha": head_sha,
        "event_name": os.getenv("GITHUB_EVENT_NAME", "unknown"),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID"),
        "workflow_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "correlation": {"pr_number": pr_number, "issue_number": issue_number,
                        "context_key": os.getenv("CONTEXT_KEY"), "experiment_id": os.getenv("EXPERIMENT_ID")},
        "lead_events": lead_events,
        "lag_events": lag_events,
        "lead_lag_pairs": pairs,
        "limitations": [
            "Temporal correlation is not causal attribution.",
            "GitHub login is not sufficient to identify the underlying agent when a shared PAT is used.",
            "Missing provider/session provenance remains INCONCLUSIVE rather than being guessed.",
        ],
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out} with {len(lead_events)} leads, {len(lag_events)} lags, {len(pairs)} temporal pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
