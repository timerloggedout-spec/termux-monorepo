#!/usr/bin/env python3
"""Validate WFC v1 structure and dependency-graph integrity (stdlib only)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,127}$")
TASK_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
SIDE_EFFECTS = {
    "read_only", "repository_write", "external_write", "deployment", "financial"
}
BUDGET_UNITS = {
    "inference_tokens", "usd_credits", "cpu_seconds", "wall_seconds", "requests"
}
WRITE_POLICIES = {"forbidden", "approval_required", "permitted_by_policy"}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_contract(data: Any) -> list[str]:
    """Return deterministic validation errors; an empty list means structurally valid."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root: expected an object"]

    required = ("schema_version", "workflow_id", "objective", "scope",
                "tasks", "constraints", "success", "evidence")
    for key in required:
        if key not in data:
            errors.append(f"missing required field: {key}")

    if data.get("schema_version") != "wfc/v1":
        errors.append("schema_version: expected wfc/v1")
    if not isinstance(data.get("workflow_id"), str) or not WORKFLOW_ID.fullmatch(data["workflow_id"]):
        errors.append("workflow_id: expected 3-128 lowercase letters, digits, dots, underscores or hyphens")
    if not _nonempty_string(data.get("objective")):
        errors.append("objective: expected a non-empty string")

    scope = data.get("scope")
    if not isinstance(scope, dict):
        errors.append("scope: expected an object")
    else:
        if not _nonempty_string(scope.get("repository")) or "/" not in scope["repository"]:
            errors.append("scope.repository: expected owner/repository")
        if not isinstance(scope.get("base_sha"), str) or not SHA.fullmatch(scope["base_sha"]):
            errors.append("scope.base_sha: expected a lowercase 40-character Git SHA")
        if not _nonempty_string(scope.get("cohort")):
            errors.append("scope.cohort: expected a non-empty string")

    tasks = data.get("tasks")
    task_ids: set[str] = set()
    dependencies: dict[str, list[str]] = {}
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks: expected a non-empty array")
    else:
        for index, task in enumerate(tasks):
            prefix = f"tasks[{index}]"
            if not isinstance(task, dict):
                errors.append(f"{prefix}: expected an object")
                continue
            task_id = task.get("id")
            if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
                errors.append(f"{prefix}.id: invalid task identifier")
                continue
            if task_id in task_ids:
                errors.append(f"{prefix}.id: duplicate task identifier {task_id}")
            task_ids.add(task_id)
            if not _nonempty_string(task.get("type")):
                errors.append(f"{prefix}.type: expected a non-empty string")
            deps = task.get("depends_on")
            if not isinstance(deps, list) or not all(isinstance(dep, str) for dep in deps):
                errors.append(f"{prefix}.depends_on: expected an array of task identifiers")
                deps = []
            if len(deps) != len(set(deps)):
                errors.append(f"{prefix}.depends_on: duplicate dependency")
            if task_id in deps:
                errors.append(f"{prefix}.depends_on: task cannot depend on itself")
            dependencies[task_id] = deps
            if "side_effect_class" in task and task["side_effect_class"] not in SIDE_EFFECTS:
                errors.append(f"{prefix}.side_effect_class: unsupported value")
            if "max_attempts" in task and (
                isinstance(task["max_attempts"], bool)
                or not isinstance(task["max_attempts"], int)
                or task["max_attempts"] < 1
                or task["max_attempts"] > 20
            ):
                errors.append(f"{prefix}.max_attempts: expected integer from 1 to 20")

        for task_id, deps in dependencies.items():
            for dep in deps:
                if dep not in task_ids:
                    errors.append(f"tasks.{task_id}: unresolved dependency {dep}")

        # Kahn's algorithm detects cycles without relying on input ordering.
        indegree = {task_id: 0 for task_id in task_ids}
        children = {task_id: [] for task_id in task_ids}
        for task_id, deps in dependencies.items():
            for dep in deps:
                if dep in task_ids:
                    indegree[task_id] += 1
                    children[dep].append(task_id)
        ready = [task_id for task_id, degree in indegree.items() if degree == 0]
        visited = 0
        while ready:
            current = ready.pop()
            visited += 1
            for child in children[current]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    ready.append(child)
        if visited != len(task_ids):
            errors.append("tasks: dependency graph contains a cycle")

    constraints = data.get("constraints")
    if not isinstance(constraints, dict):
        errors.append("constraints: expected an object")
    else:
        for key in ("max_parallel", "max_attempts"):
            if key in constraints and (
                isinstance(constraints[key], bool)
                or not isinstance(constraints[key], int)
                or constraints[key] < 1
                or (key == "max_attempts" and constraints[key] > 20)
            ):
                errors.append(f"constraints.{key}: expected a positive integer")
        if "external_writes" in constraints and constraints["external_writes"] not in WRITE_POLICIES:
            errors.append("constraints.external_writes: unsupported policy")
        if "budget" in constraints:
            budget = constraints["budget"]
            if not isinstance(budget, dict):
                errors.append("constraints.budget: expected an object")
            else:
                if budget.get("unit") not in BUDGET_UNITS:
                    errors.append("constraints.budget.unit: unsupported unit")
                limit = budget.get("limit")
                if isinstance(limit, bool) or not isinstance(limit, (int, float)) or limit <= 0:
                    errors.append("constraints.budget.limit: expected a positive number")

    for key in ("success", "evidence"):
        value = data.get(key)
        if not isinstance(value, list) or not value or not all(_nonempty_string(item) for item in value):
            errors.append(f"{key}: expected a non-empty array of non-empty strings")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", nargs="?", type=Path,
                        default=ROOT / "docs" / "examples" / "workflow-contract-routing-example.json")
    parser.add_argument("--json", action="store_true", help="emit machine-readable validation receipt")
    args = parser.parse_args()
    try:
        data = json.loads(args.contract.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors = [f"cannot load {args.contract}: {exc}"]
    else:
        errors = validate_contract(data)

    receipt = {
        "schema_version": "wfc-validation-receipt/v1",
        "contract": str(args.contract),
        "valid": not errors,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(receipt, sort_keys=True))
    elif errors:
        print("Workflow contract validation FAILED:")
        for error in errors:
            print(f"- {error}")
    else:
        print("Workflow contract validation PASSED.")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
