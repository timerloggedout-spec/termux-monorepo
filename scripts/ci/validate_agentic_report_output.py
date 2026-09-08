#!/usr/bin/env python3
"""Validate the only report payload shape permitted by the B3 agentic pilot."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_SCHEMA = Path("tests/fixtures/agentic-repo-report/output-schema.json")


def load_json_object(path: Path) -> dict[str, Any]:
    """Read a JSON object, rejecting all non-object JSON values."""
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def validate_report_output(
    payload: dict[str, Any], schema: dict[str, Any]
) -> list[str]:
    """Return every contract violation found in one B3 safe-output payload."""
    errors: list[str] = []
    required = schema["required_keys"]
    allowed = set(schema["allowed_keys"])

    for key in required:
        if key not in payload:
            errors.append(f"missing required key: {key}")
    for key in sorted(set(payload) - allowed):
        errors.append(f"unexpected key: {key}")

    if payload.get("type") != schema["type"]:
        errors.append(f"type must be {schema['type']!r}")

    title = payload.get("title")
    if not isinstance(title, str) or not re.fullmatch(schema["title_pattern"], title):
        errors.append("title does not match the fixed dated report format")

    body = payload.get("body")
    if not isinstance(body, str):
        errors.append("body must be a string")
        return errors
    if len(body) > schema["max_body_characters"]:
        errors.append("body exceeds the maximum permitted length")

    cursor = 0
    for heading in schema["required_headings"]:
        location = body.find(heading, cursor)
        if location < 0:
            errors.append(f"missing or out-of-order heading: {heading}")
            continue
        cursor = location + len(heading)
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an Issue #192 B3 repository-operations report safe output."
    )
    parser.add_argument("--output", required=True, type=Path, help="Candidate JSON output")
    parser.add_argument(
        "--schema", type=Path, default=DEFAULT_SCHEMA, help="Contract schema JSON"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        schema = load_json_object(args.schema)
        payload = load_json_object(args.output)
        errors = validate_report_output(payload, schema)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"B3 report-output validation error: {exc}", file=sys.stderr)
        return 2

    if errors:
        for error in errors:
            print(f"B3 report-output contract violation: {error}", file=sys.stderr)
        return 1
    print("B3 report-output contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
