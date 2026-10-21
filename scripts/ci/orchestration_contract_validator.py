#!/usr/bin/env python3
"""Validate native orchestration schemas using only the Python standard library."""

from __future__ import annotations

import json
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
        errors.append(f"missing required schema: {path.as_posix()}")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read valid JSON from {path.as_posix()}: {exc}")
    else:
        if not isinstance(value, dict):
            errors.append(f"schema root must be an object: {path.as_posix()}")
        else:
            return value
    return None


def _check_schema(name: str, schema: dict[str, Any], errors: list[str]) -> bool:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append(f"{name}: unexpected or missing JSON Schema draft")
    if schema.get("type") != "object":
        errors.append(f"{name}: root type must be object")
    if schema.get("additionalProperties") is not False:
        errors.append(f"{name}: root must reject undeclared properties")

    properties = schema.get("properties")
    required = schema.get("required")
    structurally_valid = True
    if not isinstance(properties, dict):
        errors.append(f"{name}: properties must be an object")
        structurally_valid = False
    if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
        errors.append(f"{name}: required must be a string array")
        structurally_valid = False
    if not structurally_valid:
        return False
    missing = sorted(set(required) - set(properties))
    if missing:
        errors.append(f"{name}: required keys lack property definitions: {', '.join(missing)}")
        return False
    return True


def validate_contracts(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    schema_dir = root / "docs" / "ops"
    treatment = _load(schema_dir / TREATMENT, errors)
    receipt = _load(schema_dir / RECEIPT, errors)

    if treatment is not None and _check_schema(TREATMENT, treatment, errors):
        props = treatment["properties"]
        status = props.get("status")
        status_enum = status.get("enum") if isinstance(status, dict) else None
        if not isinstance(status_enum, list) or not all(isinstance(x, str) for x in status_enum) or set(status_enum) != EXPECTED_TREATMENT_STATUSES:
            errors.append(f"{TREATMENT}: status lifecycle enum drifted")
        if "wait_policy" not in treatment["required"]:
            errors.append(f"{TREATMENT}: wait_policy must be required")
        if "evidence_contract" not in treatment["required"]:
            errors.append(f"{TREATMENT}: evidence_contract must be required")
        sha = props.get("source_sha", {})
        if not isinstance(sha, dict) or sha.get("pattern") != "^[0-9a-f]{40}$":
            errors.append(f"{TREATMENT}: source_sha must be a lowercase 40-character commit SHA")

    if receipt is not None and _check_schema(RECEIPT, receipt, errors):
        props = receipt["properties"]
        for field, expected in (
            ("state", EXPECTED_STATES),
            ("outcome", EXPECTED_OUTCOMES),
            ("promotion", EXPECTED_PROMOTIONS),
        ):
            field_schema = props.get(field)
            actual = field_schema.get("enum") if isinstance(field_schema, dict) else None
            if not isinstance(actual, list) or not all(isinstance(x, str) for x in actual) or set(actual) != expected:
                errors.append(f"{RECEIPT}: {field} enum drifted")
        required_ids = {
            "orchestration_id", "cycle_id", "attempt_id", "action_id",
            "event_id", "repo", "ref", "sha", "evidence_ids",
        }
        missing_ids = sorted(required_ids - set(receipt["required"]))
        if missing_ids:
            errors.append(f"{RECEIPT}: missing required identity/evidence fields: {', '.join(missing_ids)}")
        sha = props.get("sha")
        if not isinstance(sha, dict) or sha.get("pattern") != "^[0-9a-f]{40}$":
            errors.append(f"{RECEIPT}: sha must be a lowercase 40-character commit SHA")
        observed_at = props.get("observed_at")
        if not isinstance(observed_at, dict) or observed_at.get("format") != "date-time":
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
