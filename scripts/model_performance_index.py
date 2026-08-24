#!/usr/bin/env python3
"""Outcome-first 3L0 performance index.

Correctness and integrated working outcome dominate. Latency is a low-weight
operational diagnostic/tiebreaker. Task PASS/FAIL is kept distinct from model
correctness, provider errors, warnings, and orchestration failures.
"""
from __future__ import annotations
import json, math, statistics, sys
from collections import defaultdict

VALID_STATUS = {"attempted", "failed", "succeeded", "skipped"}
VALID_OUTCOME = {"PASS", "FAIL", "UNKNOWN", None}


def percentile(values, p):
    if not values:
        return None
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    rank = (len(values) - 1) * p
    lo, hi = math.floor(rank), math.ceil(rank)
    return values[lo] if lo == hi else values[lo] + (values[hi] - values[lo]) * (rank - lo)


def rate(values):
    known = [v for v in values if isinstance(v, (bool, int, float)) and not isinstance(v, bool) or isinstance(v, bool)]
    return sum(float(v) for v in known) / len(known) if known else None


def numeric_rate(values):
    known = [float(v) for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return sum(known) / len(known) if known else None


def main():
    rows = []
    for line in sys.stdin:
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("route_status") not in VALID_STATUS:
            raise SystemExit("invalid route_status")
        outcome = row.get("task_outcome", "UNKNOWN")
        if outcome not in VALID_OUTCOME:
            raise SystemExit("invalid task_outcome")
        rows.append(row)

    unique = {}
    for row in rows:
        key = row.get("experiment_id") or (
            row.get("repository"), row.get("workflow"), row.get("run_id"),
            row.get("run_attempt"), row.get("head_sha"), row.get("provider"),
            row.get("requested_model") or row.get("model"), row.get("role"),
            row.get("prompt_variant")
        )
        unique[key] = row

    groups = defaultdict(list)
    for row in unique.values():
        groups[(row.get("provider"), row.get("requested_model") or row.get("model"), row.get("role"))].append(row)

    result = {"schema_version": 2, "observations": len(unique), "models": []}
    for (provider, model, role), items in sorted(groups.items()):
        attempted = [x for x in items if x["route_status"] in {"attempted", "failed", "succeeded"}]
        succeeded = [x for x in attempted if x["route_status"] == "succeeded"]
        lat = [x["latency_ms"] for x in attempted if isinstance(x.get("latency_ms"), (int, float))]
        req = [x["requests_used"] for x in attempted if isinstance(x.get("requests_used"), (int, float))]

        correctness = numeric_rate([x.get("correctness") for x in succeeded])
        integration = numeric_rate([x.get("integration_success") for x in succeeded])
        acceptance = numeric_rate([x.get("reviewer_acceptance") for x in succeeded])
        outcome_values = [1.0 if x.get("task_outcome") == "PASS" else 0.0 for x in succeeded if x.get("task_outcome") in {"PASS", "FAIL"}]
        outcome = sum(outcome_values) / len(outcome_values) if outcome_values else None

        quality_values = [x for x in (correctness, integration, acceptance, outcome) if x is not None]
        quality = statistics.mean(quality_values) if quality_values else None

        # Latency is deliberately weak. It is useful for spotting loops/stalls,
        # but cannot rescue a correctness or integration failure.
        latency_score = None
        if lat:
            latency_score = 1 / (1 + percentile(lat, .95) / 5000)

        score = None
        if quality is not None:
            fallback = quality
            score = (
                .50 * (correctness if correctness is not None else fallback)
                + .25 * (integration if integration is not None else fallback)
                + .15 * (acceptance if acceptance is not None else fallback)
                + .05 * (outcome if outcome is not None else fallback)
                + .05 * (latency_score if latency_score is not None else fallback)
            )

        task_pass = sum(x.get("task_outcome") == "PASS" for x in succeeded)
        task_fail = sum(x.get("task_outcome") == "FAIL" for x in succeeded)
        warnings = sum(int(x.get("warning_count", 0) or 0) for x in attempted)
        errors = sum(int(x.get("error_count", 0) or 0) for x in attempted)

        result["models"].append({
            "provider": provider,
            "model": model,
            "role": role,
            "attempts": len(attempted),
            "succeeded": len(succeeded),
            "skipped": sum(x["route_status"] == "skipped" for x in items),
            "provider_failures": sum(x.get("error_class") in {"auth", "rate_limit", "provider", "transport"} for x in attempted),
            "success_rate": len(succeeded) / len(attempted) if attempted else None,
            "correctness_rate": correctness,
            "integration_success_rate": integration,
            "task_success_rate": outcome,
            "task_pass": task_pass,
            "task_fail": task_fail,
            "reviewer_acceptance_rate": acceptance,
            "warning_rate": warnings / len(attempted) if attempted else None,
            "error_rate": errors / len(attempted) if attempted else None,
            "median_latency_ms": statistics.median(lat) if lat else None,
            "p95_latency_ms": percentile(lat, .95) if lat else None,
            "median_requests_used": statistics.median(req) if req else None,
            "execution_score_v2": score,
            "sample_status": "provisional" if len(attempted) < 5 else "rankable",
            "scoring_policy": "50_correctness_25_integration_15_acceptance_5_outcome_5_latency"
        })

    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
