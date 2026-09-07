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


def percentile_fast(values, p):
    """Fast percentile calculation for pre-sorted numeric lists."""
    if not values:
        return None
    n = len(values)
    if n == 1:
        return values[0]
    rank = (n - 1) * p
    lo = int(rank)
    hi = lo + 1 if lo < n - 1 else lo
    return values[lo] if lo == hi else values[lo] + (values[hi] - values[lo]) * (rank - lo)


def main():
    unique = {}
    for line in sys.stdin:
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("route_status") not in VALID_STATUS:
            raise SystemExit("invalid route_status")
        outcome = row.get("task_outcome", "UNKNOWN")
        if outcome not in VALID_OUTCOME:
            raise SystemExit("invalid task_outcome")

        # Deduplicate on the fly to avoid secondary list iteration
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

    # Optimize group processing with single-pass metric accumulation
    for (provider, model, role), items in sorted(groups.items()):
        attempted_count = 0
        succeeded_count = 0
        skipped_count = 0
        provider_failures = 0
        warnings = 0
        errors = 0

        lat = []
        req = []
        correctness_vals = []
        integration_vals = []
        acceptance_vals = []
        outcome_vals = []

        task_pass = 0
        task_fail = 0

        for x in items:
            st = x.get("route_status")
            if st == "skipped":
                skipped_count += 1
                continue
            if st not in {"attempted", "failed", "succeeded"}:
                continue

            attempted_count += 1
            if x.get("error_class") in {"auth", "rate_limit", "provider", "transport"}:
                provider_failures += 1

            w = x.get("warning_count")
            if w:
                warnings += int(w)
            e = x.get("error_count")
            if e:
                errors += int(e)

            l = x.get("latency_ms")
            if isinstance(l, (int, float)):
                lat.append(l)

            r = x.get("requests_used")
            if isinstance(r, (int, float)):
                req.append(r)

            if st == "succeeded":
                succeeded_count += 1
                c = x.get("correctness")
                if isinstance(c, (int, float)) and not isinstance(c, bool):
                    correctness_vals.append(float(c))

                i_s = x.get("integration_success")
                if isinstance(i_s, (int, float)) and not isinstance(i_s, bool):
                    integration_vals.append(float(i_s))

                r_a = x.get("reviewer_acceptance")
                if isinstance(r_a, (int, float)) and not isinstance(r_a, bool):
                    acceptance_vals.append(float(r_a))

                to = x.get("task_outcome")
                if to == "PASS":
                    task_pass += 1
                    outcome_vals.append(1.0)
                elif to == "FAIL":
                    task_fail += 1
                    outcome_vals.append(0.0)

        correctness = sum(correctness_vals) / len(correctness_vals) if correctness_vals else None
        integration = sum(integration_vals) / len(integration_vals) if integration_vals else None
        acceptance = sum(acceptance_vals) / len(acceptance_vals) if acceptance_vals else None
        outcome = sum(outcome_vals) / len(outcome_vals) if outcome_vals else None

        quality_values = [x for x in (correctness, integration, acceptance, outcome) if x is not None]
        quality = statistics.mean(quality_values) if quality_values else None

        # Sort lat in-place for fast p95 percentile calculation
        if lat:
            lat.sort()
            p95_lat = percentile_fast(lat, 0.95)
            latency_score = 1 / (1 + p95_lat / 5000)
        else:
            p95_lat = None
            latency_score = None

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

        result["models"].append({
            "provider": provider,
            "model": model,
            "role": role,
            "attempts": attempted_count,
            "succeeded": succeeded_count,
            "skipped": skipped_count,
            "provider_failures": provider_failures,
            "success_rate": succeeded_count / attempted_count if attempted_count else None,
            "correctness_rate": correctness,
            "integration_success_rate": integration,
            "task_success_rate": outcome,
            "task_pass": task_pass,
            "task_fail": task_fail,
            "reviewer_acceptance_rate": acceptance,
            "warning_rate": warnings / attempted_count if attempted_count else None,
            "error_rate": errors / attempted_count if attempted_count else None,
            "median_latency_ms": statistics.median(lat) if lat else None,
            "p95_latency_ms": p95_lat,
            "median_requests_used": statistics.median(req) if req else None,
            "execution_score_v2": score,
            "sample_status": "provisional" if attempted_count < 5 else "rankable",
            "scoring_policy": "50_correctness_25_integration_15_acceptance_5_outcome_5_latency"
        })

    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
