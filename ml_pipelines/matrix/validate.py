"""Validate the Issue #175 matrix. Fail closed on missing hard rules."""
from __future__ import annotations

from typing import Any

from ml_pipelines.contracts import PipelineError
from ml_pipelines.matrix.schema import PRIORITIES, REQUIRED_ITEM, REQUIRED_ROOT, STATUSES


HARD_RULES = {
    "no_force_push_master",
    "small_green_rebased_prs",
    "repo_gate_and_termux_smoke",
    "reject_class_3_4",
    "gitlab_non_blocking",
}


def validate_matrix(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_ROOT - set(doc)
    if missing:
        errors.append(f"missing root keys: {sorted(missing)}")
    if str(doc.get("issue")) not in {"175", 175}:
        # allow int or str
        if doc.get("issue") not in {175, "175"}:
            errors.append("issue must be 175")
    rules = doc.get("operator_rules") or {}
    if isinstance(rules, dict):
        absent = HARD_RULES - set(rules)
        if absent:
            errors.append(f"missing operator rules: {sorted(absent)}")
    else:
        errors.append("operator_rules must be a map")
    tiers = doc.get("tiers") or {}
    if not isinstance(tiers, dict) or not tiers:
        errors.append("tiers must be a non-empty map")
    items = doc.get("items") or {}
    if isinstance(items, dict):
        for item_id, item in items.items():
            if not isinstance(item, dict):
                errors.append(f"{item_id} is not a map")
                continue
            miss = REQUIRED_ITEM - set(item)
            if miss:
                errors.append(f"{item_id} missing {sorted(miss)}")
            if item.get("priority") not in PRIORITIES:
                errors.append(f"{item_id} bad priority")
            if item.get("status") not in STATUSES:
                errors.append(f"{item_id} bad status")
    if errors:
        raise PipelineError("; ".join(errors))
    return []
