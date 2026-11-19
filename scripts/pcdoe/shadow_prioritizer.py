#!/usr/bin/env python3
"""Evaluate PCDOE prioritization policies against a frozen, read-only task snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def number(task: dict, key: str) -> float | None:
    value = task.get(key)
    if value is None:
        return None
    result = float(value)
    if not 0 <= result <= 1:
        raise ValueError(f"{task.get('task_id')}: {key} must be within [0, 1]")
    return result


def mean_known(values: list[float | None]) -> tuple[float, float, list[int]]:
    known = [value for value in values if value is not None]
    score = sum(known) / len(known) if known else 0.0
    confidence = len(known) / len(values) if values else 0.0
    unknown = [index for index, value in enumerate(values) if value is None]
    return score, confidence, unknown


def evaluate_policy(policy: dict, tasks: list[dict], risk_limit: float) -> dict:
    ranked = []
    for task in tasks:
        value = number(task, "value")
        confidence = number(task, "value_confidence")
        effort = number(task, "effort")
        urgency = number(task, "urgency")
        unlock = number(task, "dependency_unlock")
        critical = number(task, "critical_path")
        uncertainty = number(task, "uncertainty")
        recovery = number(task, "recovery_cost")
        reversibility = number(task, "reversibility")
        age = number(task, "age")
        risk = number(task, "risk")
        adjusted_value = value * confidence if value is not None and confidence is not None else None
        efficiency = 1.0 - effort if effort is not None else None
        treatment = policy["treatment_type"]
        components: dict[str, float | None] = {}
        if treatment == "incumbent":
            score = float(task.get("incumbent_rank", 10**9))
            components["incumbent_rank"] = score
            sort_key = (0, score, task["task_id"])
        else:
            factors: list[float | None]
            if treatment == "value_density":
                factors = [adjusted_value, efficiency]
                score, certainty, unknown = mean_known(factors)
                score = (adjusted_value / max(effort, 0.01)) if adjusted_value is not None and effort is not None else 0.0
                components = {"value_confidence_adjusted": adjusted_value, "effort_efficiency": efficiency}
            elif treatment == "critical_path":
                factors = [critical, urgency]
                score, certainty, unknown = mean_known(factors)
                score = 0.55 * (critical or 0.0) + 0.45 * (urgency or 0.0)
                components = {"critical_path": critical, "urgency": urgency}
            elif treatment == "dependency_unlock":
                factors = [unlock, number(task, "blocked_time_reduction")]
                score, certainty, unknown = mean_known(factors)
                score = 0.75 * (unlock or 0.0) + 0.25 * (number(task, "blocked_time_reduction") or 0.0)
                components = {"dependency_unlock": unlock, "blocked_time_reduction": number(task, "blocked_time_reduction")}
            elif treatment == "risk_adjusted":
                factors = [adjusted_value, uncertainty, recovery]
                score, certainty, unknown = mean_known(factors)
                score = 0.6 * (adjusted_value or 0.0) - 0.2 * (uncertainty or 0.0) - 0.2 * (recovery or 0.0)
                components = {"value_confidence_adjusted": adjusted_value, "uncertainty": uncertainty, "recovery_cost": recovery}
            elif treatment == "balanced":
                factors = [adjusted_value, urgency, unlock, efficiency, reversibility, age]
                score, certainty, unknown = mean_known(factors)
                score = (0.30 * (adjusted_value or 0.0) + 0.20 * (urgency or 0.0)
                         + 0.20 * (unlock or 0.0) + 0.15 * (efficiency or 0.0)
                         + 0.10 * (reversibility or 0.0) + 0.05 * (age or 0.0))
                components = {"value_confidence_adjusted": adjusted_value, "urgency": urgency,
                              "dependency_unlock": unlock, "effort_efficiency": efficiency,
                              "reversibility": reversibility, "age": age}
            else:
                raise ValueError(f"Unsupported treatment_type: {treatment}")
            unknown_fields = [key for key, val in components.items() if val is None]
            certainty = sum(val is not None for val in components.values()) / max(len(components), 1)
            sort_key = (1, -score, -certainty, task["task_id"])
        eligible = risk is not None and risk <= risk_limit
        ranked.append({
            "task_id": task["task_id"],
            "score": score,
            "confidence": certainty if treatment != "incumbent" else 1.0,
            "components": components,
            "unknown_inputs": unknown_fields if treatment != "incumbent" else [],
            "eligible": eligible,
            "eligibility_reason": "risk_within_snapshot_limit" if eligible else "risk_unknown_or_above_snapshot_limit",
            "_sort": sort_key,
        })
    ranked.sort(key=lambda item: item["_sort"])
    for index, item in enumerate(ranked, 1):
        item["rank"] = index
        del item["_sort"]
    return {
        "policy_id": policy["policy_id"],
        "policy_version": policy["version"],
        "policy_sha256": canonical_hash(policy),
        "recommendation_only": True,
        "recommendations": ranked,
    }


def evaluate_snapshot(catalog: dict, snapshot: dict) -> dict:
    if snapshot.get("mode") != "read_only_shadow":
        raise ValueError("Snapshot mode must be read_only_shadow")
    tasks = snapshot.get("tasks", [])
    if not tasks:
        raise ValueError("Snapshot must contain at least one task")
    if len({task.get("task_id") for task in tasks}) != len(tasks) or any(not task.get("task_id") for task in tasks):
        raise ValueError("Task IDs must be present and unique")
    risk_limit = float(snapshot.get("risk_limit", 0.7))
    if not 0 <= risk_limit <= 1:
        raise ValueError("risk_limit must be within [0, 1]")
    policies = catalog["policies"]
    if len({policy["policy_id"] for policy in policies}) != len(policies):
        raise ValueError("Policy IDs must be unique")
    results = [evaluate_policy(policy, tasks, risk_limit) for policy in policies]
    return {
        "schema_version": "pcdoe.shadow-result.v1",
        "mode": "read_only_shadow",
        "side_effects": [],
        "snapshot_ref": snapshot.get("snapshot_ref", "inline-fixture"),
        "snapshot_sha256": canonical_hash(snapshot),
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "recommendations_only": True,
        "policies": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policies", required=True, type=Path)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    catalog = json.loads(args.policies.read_text(encoding="utf-8"))
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    result = evaluate_snapshot(catalog, snapshot)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
