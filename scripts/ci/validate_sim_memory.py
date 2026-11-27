#!/usr/bin/env python3
"""Validate append-only Self-Improvement Memory JSONL streams.

The validator is read-only and stdlib-only. It evaluates the JSON Schema subset
used by the SIM contract, then checks ordering and identity invariants across
multiple JSONL records.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "docs" / "ops" / "SELF-IMPROVEMENT-MEMORY.schema.json"
RFC3339_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")


class SimMemoryValidationError(ValueError):
    """Raised when a SIM event or stream invariant is invalid."""


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def _schema_errors(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Evaluate the closed JSON Schema keywords used by this contract."""
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None:
        types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_type_matches(value, item) for item in types):
            return [f"{path}: expected {' or '.join(types)}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} is outside the allowed enum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is shorter than minLength")
        pattern = schema.get("pattern")
        if pattern and re.fullmatch(pattern, value) is None:
            errors.append(f"{path}: string does not match required pattern")
        if schema.get("format") == "date-time":
            try:
                if RFC3339_RE.fullmatch(value) is None:
                    raise ValueError("timestamp must use RFC 3339 date-time form")
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    raise ValueError("timestamp requires a timezone")
            except ValueError:
                errors.append(f"{path}: invalid RFC 3339 date-time")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: number is below minimum")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = sorted(set(value) - set(properties))
            if extras:
                errors.append(f"{path}: additional properties are forbidden: {extras}")
        for key, child_schema in properties.items():
            if key in value:
                errors.extend(_schema_errors(value[key], child_schema, f"{path}.{key}"))

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: array has fewer than minItems")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: array items must be unique")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                errors.extend(_schema_errors(item, item_schema, f"{path}[{index}]"))

    for index, child_schema in enumerate(schema.get("allOf", [])):
        errors.extend(_schema_errors(value, child_schema, f"{path}.allOf[{index}]"))

    condition = schema.get("if")
    if condition is not None:
        condition_errors = _schema_errors(value, condition, f"{path}.if")
        branch = schema.get("then") if not condition_errors else schema.get("else")
        if branch is not None:
            errors.extend(_schema_errors(value, branch, f"{path}.conditional"))

    negative_schema = schema.get("not")
    if negative_schema is not None and not _schema_errors(value, negative_schema, f"{path}.not"):
        errors.append(f"{path}: value matches a forbidden schema")

    return errors


def parse_timestamp(value: str) -> datetime:
    """Parse a schema-validated RFC 3339 timestamp into an aware datetime."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_records(path: Path) -> dict[str, int]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    opened: dict[str, dict[str, Any]] = {}
    record_ids: set[str] = set()
    attempt_ids: set[str] = set()
    event_count = 0
    attempt_count = 0

    with path.open(encoding="utf-8") as stream:
        for line_number, raw in enumerate(stream, start=1):
            if not raw.strip():
                continue
            try:
                record = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise SimMemoryValidationError(
                    f"line {line_number}: invalid JSON: {exc.msg}"
                ) from exc

            errors = _schema_errors(record, schema)
            if errors:
                raise SimMemoryValidationError(
                    f"line {line_number}: schema violation: {errors[0]}"
                )

            record_id = record["record_id"]
            if record_id in record_ids:
                raise SimMemoryValidationError(
                    f"line {line_number}: duplicate record_id {record_id!r}"
                )
            record_ids.add(record_id)
            event_count += 1

            problem_id = record["problem_id"]
            problem = record["problem"]
            if record["record_type"] == "problem_opened":
                if problem_id in opened:
                    raise SimMemoryValidationError(
                        f"line {line_number}: problem_id {problem_id!r} opened twice"
                    )
                opened[problem_id] = {
                    "problem": problem,
                    "last_ordinal": 0,
                    "opened_round": problem["opened_round"],
                }
                continue

            state = opened.get(problem_id)
            if state is None:
                raise SimMemoryValidationError(
                    f"line {line_number}: attempt references unopened problem_id {problem_id!r}"
                )
            if problem != state["problem"]:
                raise SimMemoryValidationError(
                    f"line {line_number}: problem definition changed for {problem_id!r}; open a new problem identity"
                )

            attempt = record["attempt"]
            predicted_at = parse_timestamp(attempt["predicted_at"])
            observed_at = parse_timestamp(attempt["observed_at"])
            recorded_at = parse_timestamp(record["recorded_at"])
            if not predicted_at < observed_at <= recorded_at:
                raise SimMemoryValidationError(
                    f"line {line_number}: expected predicted_at < observed_at <= recorded_at"
                )

            context = attempt["context"]
            if context["round"] < state["opened_round"]:
                raise SimMemoryValidationError(
                    f"line {line_number}: attempt round precedes problem opened_round"
                )

            observation = attempt["observation"]
            if observation["passed"] > observation["total"]:
                raise SimMemoryValidationError(
                    f"line {line_number}: passed count exceeds total evaluation count"
                )

            predicted = set(attempt["prediction"]["predicted_task_ids"])
            fixed = set(observation["fixed_task_ids"])
            missed = set(observation["missed_task_ids"])
            unresolved = set(observation.get("unresolved_task_ids", []))
            if fixed & missed or fixed & unresolved or missed & unresolved:
                raise SimMemoryValidationError(
                    f"line {line_number}: fixed, missed and unresolved task sets overlap"
                )
            if not (fixed | missed | unresolved).issubset(predicted):
                raise SimMemoryValidationError(
                    f"line {line_number}: observed task outcomes exceed the predicted task set"
                )

            attempt_id = attempt["attempt_id"]
            if attempt_id in attempt_ids:
                raise SimMemoryValidationError(
                    f"line {line_number}: duplicate attempt_id {attempt_id!r}"
                )
            attempt_ids.add(attempt_id)

            expected_ordinal = state["last_ordinal"] + 1
            if attempt["ordinal"] != expected_ordinal:
                raise SimMemoryValidationError(
                    f"line {line_number}: problem {problem_id!r} expected attempt ordinal "
                    f"{expected_ordinal}, received {attempt['ordinal']}"
                )
            state["last_ordinal"] = attempt["ordinal"]
            attempt_count += 1

    return {
        "events": event_count,
        "problems": len(opened),
        "attempts": attempt_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True, type=Path, help="Existing SIM JSONL ledger")
    args = parser.parse_args()

    try:
        summary = validate_records(args.path)
    except (OSError, json.JSONDecodeError, SimMemoryValidationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(
        "PASS: "
        f"{summary['events']} events, "
        f"{summary['problems']} problems, "
        f"{summary['attempts']} attempts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
