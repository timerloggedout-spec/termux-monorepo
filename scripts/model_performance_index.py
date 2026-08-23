#!/usr/bin/env python3
"""Aggregate actual model invocations into a conservative performance index.

Input: newline-delimited JSON observations. Output: JSON grouped by provider/model/role.
Skipped routes never count as model failures; only attempted invocations affect quality
and latency metrics. This deliberately avoids pretending that declared router candidates
are performance evidence.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from collections import defaultdict


def percentile(values, p):
    if not values:
        return None
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    rank = (len(values) - 1) * p
    lo = math.floor(rank)
    hi = math.ceil(rank)
    if lo == hi:
        return values[lo]
    return values[lo] + (values[hi] - values[lo]) * (rank - lo)


def rate(values):
    known = [v for v in values if isinstance(v, bool)]
    return (sum(known) / len(known)) if known else None


def main():
    rows = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if row.get("route_status") not in {"attempted", "failed", "succeeded", "skipped"}:
            raise SystemExit("invalid route_status")
        rows.append(row)

    unique = {}
    for row in rows:
        key = (
            row.get("repository"), row.get("workflow"), row.get("run_id"),
            row.get("run_attempt"), row.get("head_sha"), row.get("provider"),
            row.get("model"), row.get("role"),
        )
        unique[key] = row

    groups = defaultdict(list)
    for row in unique.values():
        groups[(row.get("provider"), row.get("model"), row.get("role"))].append(row)

    result = {"schema_version": 1, "observations": len(unique), "models": []}
    for (provider, model, role), items in sorted(groups.items()):
        attempted = [x for x in items if x["route_status"] in {"attempted", "failed", "succeeded"}]
        succeeded = [x for x in attempted if x["route_status"] == "succeeded"]
        latencies = [x["latency_ms"] for x in attempted if isinstance(x.get("latency_ms"), (int, float))]
        requests = [x["requests_used"] for x in attempted if isinstance(x.get("requests_used"), (int, float))]
        task = [x.get("task_success") for x in succeeded]
        accepted = [x.get("reviewer_acceptance") for x in succeeded]
        quality = rate(task)
        acceptance = rate(accepted)
        latency_score = None
        if latencies:
            p95 = percentile(latencies, 0.95)
            latency_score = 1.0 / (1.0 + (p95 / 5000.0))
        request_score = None
        if requests:
            request_score = 1.0 / max(1.0, statistics.mean(requests))
        score_parts = [x for x in (quality, acceptance, latency_score, request_score) if x is not None]
        score = (0.55 * quality + 0.20 * acceptance + 0.15 * latency_score + 0.10 * request_score) if all(x is not None for x in (quality, acceptance, latency_score, request_score)) else None
        result["models"].append({
            "provider": provider,
            "model": model,
            "role": role,
            "attempts": len(attempted),
            "succeeded": len(succeeded),
            "skipped": sum(x["route_status"] == "skipped" for x in items),
            "provider_failures": sum(x.get("error_class") in {"auth", "rate_limit", "provider", "transport"} for x in attempted),
            "success_rate": (len(succeeded) / len(attempted)) if attempted else None,
            "task_success_rate": quality,
            "reviewer_acceptance_rate": acceptance,
            "median_latency_ms": statistics.median(latencies) if latencies else None,
            "p95_latency_ms": p95 if latencies else None,
            "median_requests_used": statistics.median(requests) if requests else None,
            "execution_score_v1": score,
            "sample_status": "provisional" if len(attempted) < 5 else "rankable",
            "score_components_present": len(score_parts),
        })

    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
