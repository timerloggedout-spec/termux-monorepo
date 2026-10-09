#!/usr/bin/env python3
"""Classify Actions job conclusions before incident notification.

A workflow_run conclusion of failure is not enough. Concurrency cancel
and skipped jobs have produced incident comments against superseded SHAs.
Only a job conclusion of failure or timed_out is actionable.
"""

from __future__ import annotations

import json
import sys
from typing import Any

ACTIONABLE = {"failure", "timed_out"}
NON_ACTIONABLE = {"success", "skipped", "cancelled", "neutral", None, ""}


def classify(jobs: list[dict[str, Any]]) -> dict[str, Any]:
    conclusions = [job.get("conclusion") for job in jobs]
    actionable = [
        {"name": job.get("name"), "conclusion": job.get("conclusion")}
        for job in jobs
        if job.get("conclusion") in ACTIONABLE
    ]
    unknown = sorted(
        {
            str(item)
            for item in conclusions
            if item not in ACTIONABLE and item not in NON_ACTIONABLE
        }
    )
    return {
        "schema": "actions-job-classifier/v1",
        "actionable": bool(actionable),
        "actionable_jobs": actionable,
        "unknown_conclusions": unknown,
        "job_count": len(jobs),
    }


def main() -> int:
    payload = json.load(sys.stdin)
    jobs = payload.get("jobs", payload if isinstance(payload, list) else [])
    if not isinstance(jobs, list):
        print("jobs payload must be a list", file=sys.stderr)
        return 2
    result = classify(jobs)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["actionable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
