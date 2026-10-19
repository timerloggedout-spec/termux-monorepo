#!/usr/bin/env python3
"""Idempotent Actions incident notification decisions with durable run linkage.

Input: one GitHub CLI issue JSON object on stdin (body + comments).
Output: JSON with updated body, whether to notify, and whether this run is new.
"""
from __future__ import annotations

import json
import sys
from typing import Any

OBSERVATIONS_MARKER = "<!-- actions-run-observations:v1 -->"
NOTIFIED_MARKER_PREFIX = "<!-- actions-notified:"


def reconcile_incident(
    issue: dict[str, Any],
    *,
    fingerprint: str,
    run_id: str,
    run_attempt: str,
    run_url: str,
) -> dict[str, Any]:
    body = str(issue.get("body") or "")
    comments = issue.get("comments") or []
    searchable = [body]
    if isinstance(comments, list):
        searchable.extend(
            str(c.get("body") or "") for c in comments if isinstance(c, dict)
        )
    notification_marker = f"{NOTIFIED_MARKER_PREFIX}{fingerprint} -->"
    # A fingerprint in the issue body records an incident, not successful delivery.
    # Only a marker in a successfully published notification proves notification.
    already_notified = any(notification_marker in text for text in searchable)
    run_marker = f"actions-run:{run_id}:{run_attempt}"
    run_already_recorded = run_marker in body

    if not run_already_recorded:
        entry = f"- [{run_id} (attempt {run_attempt})]({run_url}) — fingerprint `{fingerprint}`"
        if OBSERVATIONS_MARKER in body:
            body = body.rstrip() + "\n" + entry + "\n"
        else:
            body = body.rstrip() + (
                "\n\n" if body.strip() else ""
            ) + OBSERVATIONS_MARKER + "\n### Related run observations\n" + entry + "\n"
        # Hidden marker makes retries idempotent without hiding the visible run link.
        body = body.rstrip() + f"\n<!-- {run_marker} -->\n"

    return {
        "body": body,
        "notify": not already_notified,
        "run_already_recorded": run_already_recorded,
        "fingerprint": fingerprint,
        "notification_marker": notification_marker,
        "run_id": run_id,
        "run_attempt": run_attempt,
    }


def main() -> int:
    issue = json.load(sys.stdin)
    result = reconcile_incident(
        issue,
        fingerprint=sys.argv[1],
        run_id=sys.argv[2],
        run_attempt=sys.argv[3],
        run_url=sys.argv[4],
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
