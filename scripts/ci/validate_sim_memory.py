#!/usr/bin/env python3
"""Validate append-only Self-Improvement Memory JSONL streams.

The validator is read-only. It checks each event against the closed JSON Schema,
then checks ordering and identity invariants that span multiple JSONL records.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "docs" / "ops" / "SELF-IMPROVEMENT-MEMORY.schema.json"


class SimMemoryValidationError(ValueError):
    """Raised when a SIM event or stream invariant is invalid."""


def parse_timestamp(value: str) -> datetime:
    """Parse a schema-validated RFC 3339 timestamp into an aware datetime."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_records(path: Path) -> dict[str, int]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
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

            errors = sorted(
                validator.iter_errors(record),
                key=lambda error: (list(error.absolute_path), error.message),
            )
            if errors:
                first = errors[0]
                location = ".".join(str(part) for part in first.absolute_path)
                suffix = f" at {location}" if location else ""
                raise SimMemoryValidationError(
                    f"line {line_number}: schema violation{suffix}: {first.message}"
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
                opened[problem_id] = {"problem": problem, "last_ordinal": 0}
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
