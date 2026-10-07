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

2026-10-07: cancel and force-cancel on 36803855107 and 36803852632 returned
2xx while status stayed queued. DELETE returned 403 "Could not delete the
workflow run". Run 34718267095 force-cancel returned 409 "has not been queued
yet". A 2xx cancel is not clearance until a follow-up GET leaves queued.
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


def still_queued(run: dict) -> bool:
    return (run.get("status") == "queued") and (run.get("conclusion") in (None, ""))


def residual_detail(detail: str) -> str:
    text = detail.replace("\n", " ")
    if "not been queued yet" in text:
        return "residual ghost: not queued yet"
    if "Could not delete" in text:
        return "residual ghost: delete 403"
    return text[:180]


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
                outcome = clear_ghost(args.repo, run["id"], token)
                record["action"] = outcome["action"]
                if outcome.get("detail"):
                    record["detail"] = outcome["detail"]
                if outcome["action"] == "cancelled":
                    cancelled += 1
                elif outcome["action"] == "deleted":
                    deleted += 1
                elif outcome["action"] == "residual_ghost":
                    skipped += 1
                elif outcome["action"] == "error":
                    print(json.dumps(record, sort_keys=True))
                    return 1
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


def clear_ghost(repo: str, run_id: int, token: str) -> dict:
    """Cancel, verify, force-cancel, then delete. 403 delete is residual, not fatal."""
    try:
        gh("POST", f"/repos/{repo}/actions/runs/{run_id}/cancel", token)
    except GitHubError as exc:
        if exc.code != 409:
            return {"action": "error", "detail": str(exc)[:180]}
        return _delete_or_residual(repo, run_id, token, exc.detail)
    current = gh("GET", f"/repos/{repo}/actions/runs/{run_id}", token)
    if not still_queued(current):
        return {"action": "cancelled"}
    try:
        gh("POST", f"/repos/{repo}/actions/runs/{run_id}/force-cancel", token)
    except GitHubError as exc:
        if exc.code != 409:
            return {"action": "error", "detail": str(exc)[:180]}
        return _delete_or_residual(repo, run_id, token, exc.detail)
    current = gh("GET", f"/repos/{repo}/actions/runs/{run_id}", token)
    if not still_queued(current):
        return {"action": "cancelled", "detail": "force-cancel cleared queued status"}
    return _delete_or_residual(repo, run_id, token, "still queued after force-cancel")


def _delete_or_residual(repo: str, run_id: int, token: str, prior: str) -> dict:
    try:
        gh("DELETE", f"/repos/{repo}/actions/runs/{run_id}", token)
    except GitHubError as exc:
        if exc.code in (403, 409):
            return {"action": "residual_ghost", "detail": residual_detail(exc.detail or prior)}
        return {"action": "error", "detail": str(exc)[:180]}
    return {"action": "deleted", "detail": residual_detail(prior) or "deleted ghost"}


if __name__ == "__main__":
    raise SystemExit(main())
