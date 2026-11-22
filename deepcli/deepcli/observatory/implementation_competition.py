"""Matched-cohort comparison for versioned tournament implementations.

This module compares immutable run receipts. It preserves missing observations,
reports paired uncertainty, and returns a human-review recommendation. It
never promotes or changes the active implementation.
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any

METRIC_DIRECTIONS = {
    "task_quality": "max",
    "acceptance_rate": "max",
    "grounding": "max",
    "calibration": "max",
    "reproducibility": "max",
    "latency_ms": "min",
    "compute_cost": "min",
    "inference_cost": "min",
    "human_effort": "min",
    "context_tokens": "min",
    "retry_count": "min",
    "integration_conflicts": "min",
}

REQUIRED_RECEIPT_FIELDS = (
    "implementation_id",
    "implementation_version",
    "cohort_id",
    "task_id",
    "task_contract_hash",
    "environment_fingerprint",
    "evaluator_version",
    "run_id",
    "outcome",
    "hard_gates",
    "metrics",
)

REQUIRED_HARD_GATES = (
    "task_contract_valid",
    "schema_valid",
    "security_and_policy",
    "provenance_complete",
    "deterministic_checks",
)


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _validate_receipts(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(receipts, list) or not receipts:
        raise ValueError("receipts must be a non-empty list")
    grouped: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    fingerprints = set()
    contracts = set()
    evaluators = set()
    cohorts = set()
    for index, receipt in enumerate(receipts):
        if not isinstance(receipt, dict):
            raise ValueError(f"receipt[{index}] must be an object")
        missing = [field for field in REQUIRED_RECEIPT_FIELDS if field not in receipt]
        if missing:
            raise ValueError(f"receipt[{index}] missing fields: {', '.join(missing)}")
        implementation = (receipt["implementation_id"], receipt["implementation_version"])
        task_id = receipt["task_id"]
        if not all(isinstance(value, str) and value for value in (*implementation, task_id)):
            raise ValueError(f"receipt[{index}] has an empty implementation or task identity")
        if task_id in grouped[implementation]:
            raise ValueError(f"duplicate receipt for {implementation[0]} task {task_id}")
        if not isinstance(receipt["metrics"], dict) or not isinstance(receipt["hard_gates"], dict):
            raise ValueError(f"receipt[{index}] metrics and hard_gates must be objects")
        grouped[implementation][task_id] = receipt
        fingerprints.add(receipt["environment_fingerprint"])
        contracts.add(receipt["task_contract_hash"])
        evaluators.add(receipt["evaluator_version"])
        cohorts.add(receipt["cohort_id"])
    if len(grouped) != 2:
        raise ValueError("exactly two implementation versions are required")
    if len(cohorts) != 1 or len(contracts) != 1 or len(fingerprints) != 1 or len(evaluators) != 1:
        raise ValueError("implementations require the same cohort, task contract, environment and evaluator")
    implementations = list(grouped.items())
    left_tasks, right_tasks = set(implementations[0][1]), set(implementations[1][1])
    if left_tasks != right_tasks:
        raise ValueError("implementations must cover the same matched task IDs")
    return {
        "grouped": grouped,
        "implementations": [key for key, _ in implementations],
        "task_ids": sorted(left_tasks),
        "cohort_id": next(iter(cohorts)),
        "task_contract_hash": next(iter(contracts)),
        "environment_fingerprint": next(iter(fingerprints)),
        "evaluator_version": next(iter(evaluators)),
    }


def _gate_failures(receipts: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    failures = []
    for task_id, receipt in sorted(receipts.items()):
        failed = [gate for gate in REQUIRED_HARD_GATES if receipt["hard_gates"].get(gate) is not True]
        if receipt["outcome"] != "SUCCEEDED":
            failed.append(f"outcome:{receipt['outcome']}")
        if failed:
            failures.append({"task_id": task_id, "failed_gates": failed})
    return failures


def _metric_summary(incumbent: dict[str, dict[str, Any]],
                    challenger: dict[str, dict[str, Any]],
                    metric: str,
                    direction: str) -> dict[str, Any]:
    pairs = []
    for task_id in sorted(set(incumbent) & set(challenger)):
        left = incumbent[task_id]["metrics"].get(metric)
        right = challenger[task_id]["metrics"].get(metric)
        if _number(left) and _number(right):
            raw_delta = float(right) - float(left)
            pairs.append({"task_id": task_id, "incumbent": float(left),
                          "challenger": float(right), "delta": raw_delta,
                          "improvement": raw_delta if direction == "max" else -raw_delta})
    if not pairs:
        return {"direction": direction, "sample_count": 0, "incumbent_mean": None,
                "challenger_mean": None, "paired_delta_mean": None,
                "improvement_mean": None, "ci95": None, "pairs": []}
    incumbent_values = [item["incumbent"] for item in pairs]
    challenger_values = [item["challenger"] for item in pairs]
    improvements = [item["improvement"] for item in pairs]
    mean = statistics.fmean(improvements)
    ci95 = None
    if len(improvements) >= 2:
        margin = 1.96 * statistics.stdev(improvements) / math.sqrt(len(improvements))
        ci95 = [mean - margin, mean + margin]
    return {
        "direction": direction,
        "sample_count": len(pairs),
        "incumbent_mean": statistics.fmean(incumbent_values),
        "challenger_mean": statistics.fmean(challenger_values),
        "paired_delta_mean": statistics.fmean(item["delta"] for item in pairs),
        "improvement_mean": mean,
        "ci95": ci95,
        "pairs": pairs,
    }


def compare_implementations(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare exactly two implementation versions on one matched cohort."""
    validated = _validate_receipts(receipts)
    incumbent_key, challenger_key = validated["implementations"]
    grouped = validated["grouped"]
    incumbent = grouped[incumbent_key]
    challenger = grouped[challenger_key]
    incumbent_failures = _gate_failures(incumbent)
    challenger_failures = _gate_failures(challenger)
    metric_names = sorted({
        metric for receipt in receipts for metric in receipt["metrics"]
        if metric in METRIC_DIRECTIONS
    })
    metrics = {
        metric: _metric_summary(incumbent, challenger, metric, METRIC_DIRECTIONS[metric])
        for metric in metric_names
    }
    comparable = {
        metric: summary for metric, summary in metrics.items()
        if summary["sample_count"] > 0
    }
    candidate_dominates = bool(comparable) and all(
        summary["improvement_mean"] >= 0 for summary in comparable.values()
    ) and any(summary["improvement_mean"] > 0 for summary in comparable.values())
    incumbent_dominates = bool(comparable) and all(
        summary["improvement_mean"] <= 0 for summary in comparable.values()
    ) and any(summary["improvement_mean"] < 0 for summary in comparable.values())
    if incumbent_failures or challenger_failures:
        recommendation = "blocked_by_hard_gate"
    elif candidate_dominates:
        recommendation = "challenger_for_human_review"
    elif incumbent_dominates:
        recommendation = "retain_incumbent"
    else:
        recommendation = "pareto_tradeoff_or_insufficient_evidence"
    return {
        "schema": "tournament.implementation-comparison.v1",
        "cohort_id": validated["cohort_id"],
        "task_contract_hash": validated["task_contract_hash"],
        "environment_fingerprint": validated["environment_fingerprint"],
        "evaluator_version": validated["evaluator_version"],
        "matched_task_count": len(validated["task_ids"]),
        "task_ids": validated["task_ids"],
        "incumbent": {"implementation_id": incumbent_key[0],
                      "version": incumbent_key[1], "hard_gate_failures": incumbent_failures},
        "challenger": {"implementation_id": challenger_key[0],
                       "version": challenger_key[1], "hard_gate_failures": challenger_failures},
        "metrics": metrics,
        "recommendation": recommendation,
        "promotion_authorized": False,
        "promotion_gate": ["held_out_validation", "owner_approval", "rollback_target"],
    }
