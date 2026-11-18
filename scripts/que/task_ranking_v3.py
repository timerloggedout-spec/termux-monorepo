#!/usr/bin/env python3
"""QUE #5283 candidate scorer: que-task-rank/v3-compounding.

Pure, deterministic, shadow-only scoring. This module does not change v1,
dispatch feeds, admission, auto-claim, or claim-order authority.
"""
from __future__ import annotations

import math
from collections import defaultdict

METHOD = "que-task-rank/v3-compounding"
WEIGHTS = {
    "direct_verified_outcome": 20.0,
    "downstream_unlock": 20.0,
    "recurrence_eliminated": 20.0,
    "reuse_leverage": 15.0,
    "reliability_risk_reduction": 15.0,
    "evidence_confidence": 10.0,
}
COST_FIELDS = ("execution_effort", "elapsed_delay", "coordination_rework")
EPSILON = 1e-9


def _unit(value):
    """Return a finite [0, 1] float; reject bools, nulls and bad telemetry."""
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        return None
    return number


def _issue_number(row):
    value = row.get("issue")
    if isinstance(value, bool):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if number >= 0 else None


def score_compounding(evidence):
    """Score one fully evidenced candidate; otherwise return an explicit gap.

    Evidence schema:
      dimensions: all six WEIGHTS keys, each normalized to [0, 1]
      costs: execution_effort, elapsed_delay, coordination_rework in [0, 1]
      realization: observed confidence-adjusted realization in [0, 1]

    The caller must provide cohort-frozen, source-pinned values and retain
    raw values/units outside this normalized scorer. Missing values are not
    zero-imputed.
    """
    if not isinstance(evidence, dict):
        return {"eligible": False, "missing": ["evidence"]}
    dimensions = evidence.get("dimensions")
    costs = evidence.get("costs")
    missing = []
    values = {}
    for key in WEIGHTS:
        raw = dimensions.get(key) if isinstance(dimensions, dict) else None
        value = _unit(raw)
        if value is None:
            missing.append("dimensions." + key)
        else:
            values[key] = value
    cost_values = {}
    for key in COST_FIELDS:
        raw = costs.get(key) if isinstance(costs, dict) else None
        value = _unit(raw)
        if value is None:
            missing.append("costs." + key)
        else:
            cost_values[key] = value
    realization = _unit(evidence.get("realization"))
    if realization is None:
        missing.append("realization")
    if missing:
        return {"eligible": False, "missing": sorted(missing)}

    components = {key: round(values[key] * weight, 6)
                  for key, weight in WEIGHTS.items()}
    benefit_points = round(sum(components.values()), 6)
    effort = round(sum(cost_values.values()), 6)
    raw_efficiency = (100.0 * benefit_points * realization
                      / max(effort, EPSILON))
    return {
        "eligible": True,
        "components": components,
        "benefit_points": benefit_points,
        "costs": cost_values,
        "normalized_effort": effort,
        "realization": realization,
        "raw_efficiency": round(raw_efficiency, 9),
    }


def _percentiles(scored):
    """Midrank percentile; ties share a value, all-equal cohort maps to 50."""
    ordered = sorted((item["raw_efficiency"], item["issue"]) for item in scored)
    groups = defaultdict(list)
    for score, issue in ordered:
        groups[score].append(issue)
    n = len(ordered)
    result = {}
    before = 0
    for score in sorted(groups):
        count = len(groups[score])
        if n == 1:
            percentile = 100.0
        elif len(groups) == 1:
            percentile = 50.0
        else:
            midrank_zero_based = before + (count - 1) / 2.0
            percentile = 100.0 * midrank_zero_based / (n - 1)
        for issue in groups[score]:
            result[issue] = round(percentile, 6)
        before += count
    return result


def rank_compounding(rows, evidence_by_issue):
    """Return two disjoint shadow lists; never fabricate a mixed claim order.

    Complete rows are percentile-ranked within their eligible sub-cohort.
    Rows missing any v3 input are returned separately in v1 order until
    evidence exists. A partial cohort is explicitly marked; percentile
    values must not be compared across different cohort snapshots.
    """
    evidence_by_issue = evidence_by_issue or {}
    eligible, fallback = [], []
    seen = set()
    for row in rows:
        issue = _issue_number(row)
        if issue is None or issue in seen:
            raise ValueError("rows require unique non-negative integer issue ids")
        seen.add(issue)
        scored = score_compounding(evidence_by_issue.get(issue))
        if not scored["eligible"]:
            fallback.append({
                "issue": issue,
                "v1_score": row.get("v1_score"),
                "v1_rank": row.get("v1_rank"),
                "reason": scored["missing"],
            })
            continue
        eligible.append({"issue": issue, **scored,
                         "wall_in_min": row.get("wall_in_min"),
                         "v1_score": row.get("v1_score")})

    percentiles = _percentiles(eligible)
    for item in eligible:
        item["cohort_percentile"] = percentiles[item["issue"]]
        wall = item["wall_in_min"]
        item["wall_imminent"] = (
            wall is not None and not isinstance(wall, bool)
            and isinstance(wall, (int, float)) and math.isfinite(wall)
            and wall <= 48.0 * 60.0
        )
    eligible.sort(key=lambda item: (
        not item["wall_imminent"],
        -item["cohort_percentile"],
        -(item["v1_score"] if isinstance(item["v1_score"], (int, float))
          and not isinstance(item["v1_score"], bool)
          and math.isfinite(item["v1_score"]) else 0.0),
        item["issue"],
    ))
    for rank, item in enumerate(eligible, start=1):
        item["candidate_rank"] = rank

    # Preserve baseline order for ineligible rows, never compare its scale
    # with v3 percentiles and never emit a single mixed claim_order.
    fallback.sort(key=lambda item: (
        item["v1_rank"] if isinstance(item["v1_rank"], int) else 10**12,
        - (item["v1_score"] if isinstance(item["v1_score"], (int, float))
           and not isinstance(item["v1_score"], bool)
           and math.isfinite(item["v1_score"]) else 0.0),
        item["issue"],
    ))
    return {
        "method": METHOD,
        "advisory": True,
        "claim_order_binding": False,
        "complete_coverage": not fallback,
        "eligible_count": len(eligible),
        "fallback_count": len(fallback),
        "eligible": eligible,
        "v1_fallback": fallback,
        "claim_order": None,
    }
