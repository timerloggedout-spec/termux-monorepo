#!/usr/bin/env python3
"""Queue-state observer (owner's queue-timers ask, 2026-11-03).

Reads the Actions API for THIS repository and shapes the
queue-state feed the tribute dashboard's queue.html renders:

    apps/tribute-dashboard/data/queue-state-feed.json

Contract (schema queue-state-feed/v1):
- Counts and instants only. The page computes every AGE in the
  browser from the created_at instants below — never a
  pre-computed duration — mirroring the countdowns contract.
- pinned: live runs whose workflow name matches a critical-path
  pattern (the freeze path: strands proof, countdowns, cuts,
  snapshots, syncs), each with its own created_at instant.
- recent_completions_mix: conclusions of the last 100 completed
  runs — the drain-quality tell (a healthy queue completes real
  work; a churn queue completes skips).

Runs in-Actions with the job token (actions: read). Repo from
GITHUB_REPOSITORY. No other credential exists or is needed.
"""

import argparse
import collections
import json
import os
import urllib.request
from datetime import datetime, timezone

PIN_PATTERNS = (
    "strands", "countdown", "release-cut", "submission-snapshot",
    "studysprint-sync", "android-emulator-gate",
)


def api(path: str, token: str) -> dict:
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def paged_runs(repo: str, status: str, token: str, cap: int = 12) -> list:
    rows, page, total = [], 1, None
    while page <= cap:
        data = api(
            f"/repos/{repo}/actions/runs?status={status}"
            f"&per_page=100&page={page}",
            token,
        )
        total = data["total_count"]
        rows.extend(data["workflow_runs"])
        if len(rows) >= total or not data["workflow_runs"]:
            break
        page += 1
    return rows


def workflow_names(repo: str, token: str) -> dict:
    names, page = {}, 1
    while page <= 5:
        data = api(
            f"/repos/{repo}/actions/workflows?per_page=100&page={page}",
            token,
        )
        for w in data["workflows"]:
            names[w["id"]] = w["name"]
        if len(names) >= data["total_count"]:
            break
        page += 1
    return names


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    args = ap.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    if not token or not args.repo:
        raise SystemExit("GH_TOKEN/GITHUB_TOKEN and a repo are required")
    names = workflow_names(args.repo, token)
    queued = paged_runs(args.repo, "queued", token)
    in_progress = paged_runs(args.repo, "in_progress", token, cap=4)
    completed = paged_runs(args.repo, "completed", token, cap=1)

    def shape(r: dict) -> dict:
        return {
            "id": r["id"],
            "workflow": names.get(r["workflow_id"], str(r["workflow_id"])),
            "event": r["event"],
            "status": r["status"],
            "created_at": r["created_at"],
            "url": r["html_url"],
        }

    by_wf = collections.Counter(
        names.get(r["workflow_id"], str(r["workflow_id"])) for r in queued
    )
    # Wedged ancients: runs the API has listed as queued for over a
    # week. They hold no runner (never started) and resist cancel —
    # a residue class of its own (2026-11-03: three found, Oct 1–7;
    # two cancel-accepted-then-ignored, one 409 pre-queue). They are
    # reported separately so the operational oldest-wait stays the
    # live signal instead of a permanent month-old headline.
    now = datetime.now(timezone.utc)

    def is_ancient(r: dict) -> bool:
        created = datetime.strptime(
            r["created_at"], "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=timezone.utc)
        return (now - created).days >= 7

    ancients = [r for r in queued if is_ancient(r)]
    operational = [r for r in queued if not is_ancient(r)]
    oldest = min(operational, key=lambda r: r["created_at"], default=None)
    pinned = [
        shape(r)
        for r in queued + in_progress
        if any(
            p in names.get(r["workflow_id"], "").lower() for p in PIN_PATTERNS
        )
    ]
    pinned.sort(key=lambda r: r["created_at"])
    feed = {
        "schema": "queue-state-feed/v1",
        "generated_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "repo": args.repo,
        "queued": len(queued),
        "in_progress": len(in_progress),
        "oldest_queued_at": oldest["created_at"] if oldest else None,
        "oldest_queued_run": shape(oldest) if oldest else None,
        "wedged_ancient": [shape(r) for r in ancients],
        "by_workflow_queued": [
            {"workflow": w, "queued": n} for w, n in by_wf.most_common(12)
        ],
        "pinned": pinned,
        "recent_completions_mix": dict(
            collections.Counter(
                r.get("conclusion") for r in completed[:100]
            )
        ),
    }
    with open(args.out, "w") as fh:
        json.dump(feed, fh, indent=2)
    print(
        f"queue-state: queued {feed['queued']} · in_progress "
        f"{feed['in_progress']} · pinned {len(pinned)} · oldest "
        f"{feed['oldest_queued_at']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
