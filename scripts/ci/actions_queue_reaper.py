#!/usr/bin/env python3
"""Cancel stale queued Actions runs that never received jobs.

GitHub occasionally leaves issue_comment / pull_request runs in status=queued
with zero jobs for days. Those stalls consume the concurrent queue and surface
as permanent failures. This reaper only cancels runs that are still queued,
older than a threshold, and have no jobs. In-progress work is untouched.

A queued re-run can return 409 "Cannot cancel a workflow run that is not in
progress." Cancel-only left those ghosts in status=queued (reaper run
37181555004: scanned 44, uncancellable 38). Delete the run after a 409 so the
ghost leaves the concurrent queue. In-progress work is still untouched.
Evidence: DELETE on run 32218223992 returned 204 and a subsequent GET was 404.

"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone


class GitHubError(Exception):
    def __init__(self, method: str, path: str, code: int, detail: str) -> None:
        super().__init__(f"GitHub {method} {path} -> {code}: {detail[:400]}")
        self.method = method
        self.path = path
        self.code = code
        self.detail = detail


def gh(method: str, path: str, token: str, body: dict | None = None) -> dict | list:
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=None if body is None else json.dumps(body).encode(),
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "termux-monorepo-queue-reaper",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise GitHubError(method, path, exc.code, detail) from exc


def cutoff_for(event: str, now: datetime, older_hours: float, schedule_minutes: float) -> datetime:
    """Scheduled runs are hourly. A zero-job queue past the schedule window is a stall.

    Merge Promotion Queue run 37655538554 stayed status=queued with zero jobs from
    2026-10-07T16:57:32Z. The 6h threshold never saw it. Issue-comment ghosts stay
    on the longer threshold.
    """
    if event == "schedule":
        return now - timedelta(minutes=schedule_minutes)
    return now - timedelta(hours=older_hours)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--older-than-hours", type=float, default=6)
    parser.add_argument("--schedule-older-than-minutes", type=float, default=45)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GH_TOKEN required", file=sys.stderr)
        return 2
    page = 1
    cancelled = 0
    deleted = 0
    skipped = 0
    scanned = 0
    while page <= 8:
        query = urllib.parse.urlencode({"status": "queued", "per_page": 50, "page": page})
        payload = gh("GET", f"/repos/{args.repo}/actions/runs?{query}", token)
        runs = payload.get("workflow_runs") or []
        if not runs:
            break
        for run in runs:
            scanned += 1
            created = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
            cutoff = cutoff_for(
                str(run.get("event") or ""),
                datetime.now(timezone.utc),
                args.older_than_hours,
                args.schedule_older_than_minutes,
            )
            if created > cutoff:
                continue
            jobs = gh("GET", f"/repos/{args.repo}/actions/runs/{run['id']}/jobs?per_page=1", token)
            if int(jobs.get("total_count") or 0) > 0:
                continue
            record = {
                "id": run["id"],
                "name": run.get("name"),
                "event": run.get("event"),
                "created_at": run.get("created_at"),
                "head_branch": run.get("head_branch"),
            }
            if args.apply:
                try:
                    gh("POST", f"/repos/{args.repo}/actions/runs/{run['id']}/cancel", token)
                except GitHubError as exc:
                    if exc.code == 409:
                        try:
                            gh(
                                "DELETE",
                                f"/repos/{args.repo}/actions/runs/{run['id']}",
                                token,
                            )
                        except GitHubError as delete_exc:
                            record["action"] = "uncancellable"
                            record["detail"] = delete_exc.detail[:180]
                            skipped += 1
                            print(json.dumps(record, sort_keys=True))
                            continue
                        record["action"] = "deleted"
                        record["detail"] = "cancel 409; deleted ghost"
                        deleted += 1
                        print(json.dumps(record, sort_keys=True))
                        continue
                    print(json.dumps({**record, "action": "error", "detail": str(exc)[:180]}))
                    return 1
                record["action"] = "cancelled"
                cancelled += 1
            else:
                record["action"] = "would_cancel"
                cancelled += 1
            print(json.dumps(record, sort_keys=True))
        page += 1
    print(json.dumps({
        "scanned": scanned,
        "candidates": cancelled,
        "deleted": deleted,
        "uncancellable": skipped,
        "apply": args.apply,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
