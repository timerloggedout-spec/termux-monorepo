#!/usr/bin/env python3
"""Classify zero-job workflow failures that are not the current master tip.

A push of an ancestor SHA can execute that commit's workflow files and fail
before any job starts. Those runs are historical tree evidence, not a defect
in the current master tip. Current-tip zero-job failures stay actionable.
"""

from __future__ import annotations

import argparse
import json
import sys


def classify(head_sha: str, tip_sha: str, job_count: int, conclusion: str) -> str:
    head = (head_sha or "").strip()
    tip = (tip_sha or "").strip()
    if conclusion != "failure":
        return "not-failure"
    if job_count != 0:
        return "has-jobs"
    if not head or not tip:
        return "insufficient-evidence"
    if head == tip:
        return "current-tip-zero-job"
    return "historical-non-tip-zero-job"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--tip-sha", required=True)
    parser.add_argument("--job-count", required=True, type=int)
    parser.add_argument("--conclusion", required=True)
    args = parser.parse_args(argv)
    label = classify(args.head_sha, args.tip_sha, args.job_count, args.conclusion)
    json.dump({"class": label}, sys.stdout)
    sys.stdout.write("\n")
    return 0 if label != "current-tip-zero-job" else 2


if __name__ == "__main__":
    raise SystemExit(main())
