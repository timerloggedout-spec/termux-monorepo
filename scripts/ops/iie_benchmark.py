#!/usr/bin/env python3
"""Compare two context-relationship build receipts without hiding correctness drift.

This is a receipt evaluator, not a workload generator. Run the existing builder
once in full-refresh mode and once incrementally against the same frozen source
SHA, then compare the resulting build-summary.json files.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PARITY_FIELDS = (
    "repository",
    "ref",
    "source_sha",
    "node_count",
    "edge_count",
    "verified_edge_count",
    "candidate_edge_count",
    "coverage",
)
METRIC_FIELDS = (
    "wall_seconds",
    "process_cpu_seconds",
    "peak_rss_bytes",
)


def load_receipt(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read receipt {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"receipt {path} must contain a JSON object")
    performance = value.get("performance")
    if not isinstance(performance, dict):
        raise ValueError(f"receipt {path} has no performance object")
    return value


def ratio(baseline: Any, treatment: Any) -> float | None:
    if not isinstance(baseline, (int, float)) or not isinstance(treatment, (int, float)):
        return None
    if baseline <= 0 or treatment <= 0:
        return None
    return round(float(baseline) / float(treatment), 6)


def compare(baseline: dict[str, Any], treatment: dict[str, Any]) -> dict[str, Any]:
    mismatches = {
        field: {"baseline": baseline.get(field), "treatment": treatment.get(field)}
        for field in PARITY_FIELDS
        if baseline.get(field) != treatment.get(field)
    }
    baseline_performance = baseline["performance"]
    treatment_performance = treatment["performance"]
    metrics = {}
    for field in METRIC_FIELDS:
        before = baseline_performance.get(field)
        after = treatment_performance.get(field)
        metrics[field] = {
            "baseline": before,
            "treatment": after,
            "speedup_or_reduction_ratio": ratio(before, after),
        }
    baseline_requests = baseline.get("github_requests")
    treatment_requests = treatment.get("github_requests")
    metrics["github_requests"] = {
        "baseline": baseline_requests,
        "treatment": treatment_requests,
        "speedup_or_reduction_ratio": ratio(baseline_requests, treatment_requests),
    }
    return {
        "schema": "iie.benchmark-comparison/v1",
        "status": "PARITY_FAILED" if mismatches else "PARITY_PASSED",
        "parity_mismatches": mismatches,
        "metrics": metrics,
        "interpretation": (
            "Treatment is not eligible for performance promotion until deterministic "
            "outputs and coverage match the baseline."
            if mismatches else
            "Deterministic output parity holds. Ratios are descriptive; repeat runs "
            "and report variance before claiming a performance improvement."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path, help="full-refresh build-summary.json")
    parser.add_argument("--treatment", required=True, type=Path, help="incremental build-summary.json")
    parser.add_argument("--output", type=Path, help="optional JSON report path")
    args = parser.parse_args(argv)
    try:
        result = compare(load_receipt(args.baseline), load_receipt(args.treatment))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_name(args.output.name + ".tmp")
        temporary.write_text(rendered + chr(10), encoding="utf-8")
        temporary.replace(args.output)
    print(rendered)
    return 0 if result["status"] == "PARITY_PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
