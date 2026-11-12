#!/usr/bin/env python3
"""Wait for the matching QUE admission receipt before project-task intake.

The issue event remains the dispatch entry point. Admission runs in parallel;
this gate waits for its first-fleet receipt rather than racing the evaluator.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def classify_receipt(
    comments: list[dict[str, Any]], template: str, event_at: str
) -> str | None:
    """Return admitted/deferred/unmatched for the newest post-event admission stamp."""
    boundary = _timestamp(event_at)
    receipts = []
    for comment in comments:
        body = comment.get("body") or ""
        if "[MUSEai]@{role:{swarm-admission}} DISPATCH" not in body:
            continue
        try:
            created = _timestamp(comment.get("created_at", ""))
        except (TypeError, ValueError):
            continue
        if created < boundary:
            continue
        receipts.append((created, body))
    if not receipts:
        return None
    _, body = max(receipts, key=lambda item: item[0])
    if f"template `{template}`" not in body:
        return "unmatched"
    if "DISPATCH **ADMITTED**" in body:
        return "admitted"
    if "DISPATCH **DEFERRED**" in body:
        return "deferred"
    return "unmatched"


def fetch_comments(repository: str, issue: int) -> list[dict[str, Any]]:
    result = subprocess.run(
        [
            "gh", "api", "--paginate",
            f"repos/{repository}/issues/{issue}/comments?per_page=100",
            "--jq", ".[] | {body: .body, created_at: .created_at}",
        ],
        check=True, capture_output=True, text=True,
    )
    comments = []
    for line in result.stdout.splitlines():
        if line.strip():
            comments.append(json.loads(line))
    return comments


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--template", default="project-task.yml")
    parser.add_argument("--event-at", required=True)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--poll-interval", type=float, default=5)
    args = parser.parse_args(argv)
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    if not repository or not os.environ.get("GH_TOKEN"):
        parser.error("GITHUB_REPOSITORY and GH_TOKEN are required")
    deadline = time.monotonic() + args.timeout
    while True:
        try:
            decision = classify_receipt(
                fetch_comments(repository, args.issue), args.template, args.event_at
            )
        except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
            print(f"Admission receipt fetch failed; retrying: {exc}", file=sys.stderr)
            decision = None
        if decision:
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
                output.write(f"decision={decision}\n")
            print(f"QUE admission receipt: {decision}")
            return 0 if decision == "admitted" else 0
        if time.monotonic() >= deadline:
            print(
                f"Timed out waiting for the QUE admission receipt for issue #{args.issue}",
                file=sys.stderr,
            )
            return 1
        time.sleep(args.poll_interval)


if __name__ == "__main__":
    raise SystemExit(main())
