#!/usr/bin/env python3
"""Classify ancestor-push workflow noise.

A push of an already-reachable ancestor can re-execute that commit's workflow
file without moving the branch tip. Historical zero-job YAML failures on those
SHAs are not current-tree regressions and must not open a new incident.
"""

from __future__ import annotations

import argparse
import json


def classify_ancestor_push(compare_status: str, job_count: int) -> str:
    """Return ancestor_push_noise or current.

    compare_status is the GitHub compare status of ``sha...branch``:
    ``ahead`` means the branch tip contains commits the SHA does not, so the
    SHA is an ancestor (or equal-history base) of the tip. Equal tips report
    ``identical`` and stay current. Only a zero-job failure is noise; a real
    job failure on an ancestor still classifies as current.
    """
    if compare_status == "ahead" and job_count == 0:
        return "ancestor_push_noise"
    return "current"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compare-status", required=True)
    parser.add_argument("--job-count", required=True, type=int)
    args = parser.parse_args()
    klass = classify_ancestor_push(args.compare_status, args.job_count)
    print(json.dumps({"class": klass}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
