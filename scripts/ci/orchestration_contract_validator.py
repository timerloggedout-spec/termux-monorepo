#!/usr/bin/env python3
"""Validate native orchestration schemas using only the Python standard library."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "docs" / "ops"
TREATMENT = "ORCHESTRATION-TREATMENT.schema.json"
RECEIPT = "ORCHESTRATION-RECEIPT.schema.json"

EXPECTED_STATES = {
    "DISPATCHED", "QUEUED", "RUNNING", "WAITING", "STEERED",
    "RETRYING", "COMPLETED", "FAILED", "CANCELLED",
}
EXPECTED_OUTCOMES = {"TASK_PASS", "TASK_FAIL", "UNKNOWN"}
EXPECTED_PROMOTIONS = {"PROMOTABLE", "NOT_PROMOTABLE", "UNKNOWN"}
EXPECTED_TREATMENT_STATUSES = {
    "candidate", "experimental", "accepted", "deprecated", "rejected",
}


def _load(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing required schema: {path.relative_to(ROOT)}")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")
    else:
        if not isinstance(value, dict):
            errors.append(f"schema root must be an object: {path.relative_to(ROOT)}")
        else:
            return value
    return None


def _check_schema(name: str, schema: dict[str, Any], errors: list[str]) -> None:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append(f"{name}: unexpected or missing JSON Schema draft")
    if schema.get("type") != "object":
        errors.append(f"{name}: root type must be object")
    if schema.get("additionalProperties") is not False:
        errors.append(f"{name}: root must reject undeclared properties")

    properties = schema.get("properties")
    required = schema.get("required")
    if not isinstance(properties, dict):
        errors.append(f"{name}: properties must be an object")
        return
    if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
        errors.append(f"{name}: required must be a string array")
        return
    missing = sorted(set(required) - set(properties))
    if missing:
        errors.append(f"{name}: required keys lack property definitions: {', '.join(missing)}")


def validate_contracts(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    schema_dir = root / "docs" / "ops"
    treatment = _load(schema_dir / TREATMENT, errors)
    receipt = _load(schema_dir / RECEIPT, errors)

    if treatment is not None:
        _check_schema(TREATMENT, treatment, errors)
        props = treatment.get("properties", {})
        if props.get("status", {}).get("enum") is None or set(props["status"]["enum"]) != EXPECTED_TREATMENT_STATUSES:
            errors.append(f"{TREATMENT}: status lifecycle enum drifted")
        if "wait_policy" not in treatment.get("required", []):
            errors.append(f"{TREATMENT}: wait_policy must be required")
        if "evidence_contract" not in treatment.get("required", []):
            errors.append(f"{TREATMENT}: evidence_contract must be required")
        sha = props.get("source_sha", {})
        if sha.get("pattern") != "^[0-9a-f]{40}$":
            errors.append(f"{TREATMENT}: source_sha must be a lowercase 40-character commit SHA")

    if receipt is not None:
        _check_schema(RECEIPT, receipt, errors)
        props = receipt.get("properties", {})
        for field, expected in (
            ("state", EXPECTED_STATES),
            ("outcome", EXPECTED_OUTCOMES),
            ("promotion", EXPECTED_PROMOTIONS),
        ):
            actual = props.get(field, {}).get("enum")
            if not isinstance(actual, list) or set(actual) != expected:
                errors.append(f"{RECEIPT}: {field} enum drifted")
        required_ids = {
            "orchestration_id", "cycle_id", "attempt_id", "action_id",
            "event_id", "repo", "ref", "sha", "evidence_ids",
        }
        missing_ids = sorted(required_ids - set(receipt.get("required", [])))
        if missing_ids:
            errors.append(f"{RECEIPT}: missing required identity/evidence fields: {', '.join(missing_ids)}")
        if props.get("sha", {}).get("pattern") != "^[0-9a-f]{40}$":
            errors.append(f"{RECEIPT}: sha must be a lowercase 40-character commit SHA")
        if props.get("observed_at", {}).get("format") != "date-time":
            errors.append(f"{RECEIPT}: observed_at must use date-time format")

    skill_path = root / ".agents" / "skills" / "orchestration-treatment-registry" / "SKILL.md"
    try:
        skill = skill_path.read_text(encoding="utf-8")
    except OSError:
        errors.append("missing orchestration-treatment-registry skill")
    else:
        for required_ref in (
            TREATMENT, RECEIPT, "EVIDENCE-ENVELOPE.schema.json",
            "ACTION-EFFECT-EVENT.schema.json", "adaptive-wait",
            "context-relationship-graph",
        ):
            if required_ref not in skill:
                errors.append(f"orchestration-treatment-registry skill missing reference: {required_ref}")

    return errors


def main() -> int:
    errors = validate_contracts()
    if errors:
        print("Orchestration contract validation FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Orchestration contract validation PASSED (stdlib-only).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
