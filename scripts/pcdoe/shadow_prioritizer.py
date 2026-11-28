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


def score_components(policy: dict, components: dict[str, float | None]) -> tuple[float | None, float, list[str]]:
    """Score known factors from the versioned catalog; preserve missing values."""
    weighted_total = 0.0
    known_weight = 0.0
    total_weight = 0.0
    unknown: list[str] = []
    for factor in policy["factors"]:
        direction = factor["direction"]
        weight = float(factor["weight"])
        if direction not in {"maximize", "minimize"} or weight == 0:
            continue
        factor_id = factor["factor_id"]
        total_weight += weight
        value = components.get(factor_id)
        if value is None:
            unknown.append(factor_id)
            continue
        normalized = value if direction == "maximize" else 1.0 - value
        weighted_total += normalized * weight
        known_weight += weight
    score = weighted_total / known_weight if known_weight else None
    confidence = known_weight / total_weight if total_weight else 0.0
    return score, confidence, unknown


def policy_components(treatment: str, task: dict) -> dict[str, float | None]:
    value = number(task, "value")
    value_confidence = number(task, "value_confidence")
    effort = number(task, "effort")
    return {
        "value_confidence_adjusted": value * value_confidence if value is not None and value_confidence is not None else None,
        "effort_efficiency": 1.0 - effort if effort is not None else None,
        "critical_path_position": number(task, "critical_path"),
        "urgency": number(task, "urgency"),
        "dependency_unlock": number(task, "dependency_unlock"),
        "blocked_time_reduction": number(task, "blocked_time_reduction"),
        "uncertainty": number(task, "uncertainty"),
        "recovery_cost": number(task, "recovery_cost"),
        "reversibility": number(task, "reversibility"),
        "age": number(task, "age"),
    }


def evaluate_policy(policy: dict, tasks: list[dict], risk_limit: float) -> dict:
    ranked = []
    for task in tasks:
        risk = number(task, "risk")
        treatment = policy["treatment_type"]
        if treatment == "incumbent":
            incumbent_rank = task.get("incumbent_rank")
            score = float(incumbent_rank) if incumbent_rank is not None else None
            confidence = 1.0 if incumbent_rank is not None else 0.0
            components = {"incumbent_rank": score}
            unknown_fields = [] if score is not None else ["incumbent_rank"]
            sort_key = (0, score is None, score if score is not None else 0.0, -confidence, task["task_id"])
        else:
            components = policy_components(treatment, task)
            score, confidence, unknown_fields = score_components(policy, components)
            sort_key = (1, score is None, -(score if score is not None else 0.0), -confidence, task["task_id"])
        eligible = risk is not None and risk <= risk_limit
        ranked.append({
            "task_id": task["task_id"],
            "score": score,
            "confidence": confidence,
            "components": components,
            "unknown_inputs": unknown_fields,
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
