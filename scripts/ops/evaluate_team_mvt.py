#!/usr/bin/env python3
"""Summarize Team MVT lane receipts without promoting incomplete evidence."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any


EXPECTED_CELLS = 15


def summarize(rows: list[dict[str, Any]], lane_result: str) -> tuple[dict[str, Any], bool]:
    eligible = [row for row in rows if row.get("eligible") == "true"]
    executed = [row for row in eligible if row.get("execution_status") == "success"]
    failed = [row for row in eligible if row.get("execution_status") == "failure"]
    skipped = [row for row in rows if row.get("eligible") != "true"]
    lanes = sorted({str(row.get("lane", "")) for row in rows if row.get("lane")})

    base = {
        "schema": "team-mvt-evaluation/v2",
        "cells": len(rows),
        "expected": EXPECTED_CELLS,
        "eligible": len(eligible),
        "executed": len(executed),
        "execution_failures": len(failed),
        "skipped": len(skipped),
        "lanes": lanes,
        "promotion_ready": False,
    }

    if len(rows) < EXPECTED_CELLS and not failed and lane_result in {
        "cancelled", "failure", "skipped"
    }:
        reason = (
            "lane job was skipped; no lane evidence was produced"
            if lane_result == "skipped"
            else "incomplete DOE cells after cancelled or failed-closed matrix jobs"
        )
        return {**base, "status": "incomplete", "reason": reason}, False

    if len(rows) < EXPECTED_CELLS:
        return {
            **base,
            "status": "invalid",
            "reason": f"expected {EXPECTED_CELLS} DOE cells, found {len(rows)} (lane result {lane_result})",
        }, True

    return {
        **base,
        "status": "observed",
        "reason": "task correctness/evaluator evidence remains UNKNOWN until independent evaluation",
    }, False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--lane-result", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    paths = glob.glob(str(Path(args.input_dir) / "**" / "lane.json"), recursive=True)
    rows = [json.loads(Path(path).read_text(encoding="utf-8")) for path in paths]
    summary, failed = summarize(rows, args.lane_result)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
