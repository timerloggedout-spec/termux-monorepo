#!/usr/bin/env python3
"""Cancel stale queued Actions runs that never received jobs.

GitHub occasionally leaves issue_comment / pull_request runs in status=queued
with zero jobs for days. Those stalls consume the concurrent queue and surface
as permanent failures. This reaper only cancels runs that are still queued,
older than a threshold, and have no jobs. In-progress work is untouched.
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


class GitHubSkip(Exception):
    def __init__(self, code: int, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail[:200]}")


def gh(method: str, path: str, token: str, body: dict | None = None, skip_codes: tuple[int, ...] = ()) -> dict | list:
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
        if exc.code in skip_codes:
            raise GitHubSkip(exc.code, detail) from exc
        raise SystemExit(f"GitHub {method} {path} -> {exc.code}: {detail[:400]}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--older-than-hours", type=float, default=6)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GH_TOKEN required", file=sys.stderr)
        return 2
    cutoff = datetime.now(timezone.utc) - timedelta(hours=args.older_than_hours)
    page = 1
    cancelled = 0
    skipped = 0
    scanned = 0
    while page <= 5:
        query = urllib.parse.urlencode({"status": "queued", "per_page": 50, "page": page})
        payload = gh("GET", f"/repos/{args.repo}/actions/runs?{query}", token)
        runs = payload.get("workflow_runs") or []
        if not runs:
            break
        for run in runs:
            scanned += 1
            created = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
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
                    gh(
                        "POST",
                        f"/repos/{args.repo}/actions/runs/{run['id']}/cancel",
                        token,
                        skip_codes=(409,),
                    )
                    record["action"] = "cancelled"
                    cancelled += 1
                except GitHubSkip as skip:
                    # Queued re-runs can return 409 before they are cancelable.
                    # Fall back to force-cancel; if that also 409s, skip and continue.
                    try:
                        gh(
                            "POST",
                            f"/repos/{args.repo}/actions/runs/{run['id']}/force-cancel",
                            token,
                            skip_codes=(409,),
                        )
                        record["action"] = "force_cancelled"
                        record["detail"] = skip.detail[:180]
                        cancelled += 1
                    except GitHubSkip as forced:
                        record["action"] = "skip_uncancelable"
                        record["status"] = forced.code
                        record["detail"] = forced.detail[:180]
                        skipped += 1
            else:
                record["action"] = "would_cancel"
                cancelled += 1
            print(json.dumps(record, sort_keys=True))
        page += 1
    print(json.dumps({"scanned": scanned, "candidates": cancelled, "skipped_uncancelable": skipped, "apply": args.apply}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
