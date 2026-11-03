#!/usr/bin/env python3
"""Claim a dispatch-queued project-task (the claim/lease step).

The project-task intake is receipt-only by design; execution starts
when a producer CLAIMS the task. A claim is:

1. this comment on the issue (who + seat + provider + session +
   when), and
2. the `dispatch-claimed` label applied in the same motion.

Until both exist, the task is UNCLAIMED no matter what anyone
assumed — the dispatch watchdog (dispatch_watchdog.py) flags
unclaimed tasks at 30 minutes and escalates at 60.

Usage (token from GITHUB_TOKEN / GH_TOKEN):

    python3 claim_task.py 4095 \
        --role optimizations-assurance \
        --producer "Swarm Optimizations & Implementation Assurance seat" \
        --provider command-dispatch --session <session-id>

Interim rule (owner, 2026-11-03, until the mechanism proves
itself): no form filing ships without a simultaneous route-to-seat
dispatch + claim.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

API = "https://api.github.com"
DEFAULT_REPO = "timerloggedout-spec/termux-monorepo"
CLAIM_MARKER = "PRODUCER CLAIM"


def claim_comment(role: str, producer: str, provider: str,
                  session: str, now: datetime) -> str:
    stamp = now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"[MUSEai]@{{role:{{{role}}}}} {CLAIM_MARKER} — dispatch "
        f"pickup.\n\n"
        f"- resolved provider: {provider}\n"
        f"- producer: {producer}\n"
        f"- session: {session}\n"
        f"- claimed at: {stamp}\n\n"
        "State: `dispatch-queued` -> `dispatch-claimed` (label "
        "applied with this claim). Execution underway; the PR is "
        "flagged to the filing seat on appearance."
    )


def _request(method: str, url: str, token: str, payload=None):
    data = json.dumps(payload).encode() if payload is not None \
        else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode() or "{}")


def claim(repo: str, issue: int, role: str, producer: str,
          provider: str, session: str, token: str,
          now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    base = f"{API}/repos/{repo}/issues/{issue}"
    comment = _request("POST", f"{base}/comments", token,
                       {"body": claim_comment(role, producer, provider,
                                              session, now)})
    labels = _request("POST", f"{base}/labels", token,
                      {"labels": ["dispatch-claimed"]})
    return {"comment_id": comment.get("id"),
            "labels": [l["name"] for l in labels]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("issue", type=int)
    ap.add_argument("--role", required=True)
    ap.add_argument("--producer", required=True)
    ap.add_argument("--provider", required=True)
    ap.add_argument("--session", required=True)
    ap.add_argument("--repo",
                    default=os.environ.get("GITHUB_REPOSITORY",
                                           DEFAULT_REPO))
    args = ap.parse_args(argv)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get(
        "GH_TOKEN")
    if not token:
        print("claim_task: GITHUB_TOKEN / GH_TOKEN not set",
              file=sys.stderr)
        return 2
    out = claim(args.repo, args.issue, args.role, args.producer,
                args.provider, args.session, token)
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
