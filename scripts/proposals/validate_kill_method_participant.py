#!/usr/bin/env python3
"""Validate the draft, non-executable kill-method participant contract.

Stdlib-only by design: safe to run in repo_gate and on constrained Termux.
This validates the schema subset used by the contract and its policy invariants;
it is not a general-purpose JSON Schema implementation.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "docs/proposals/active/siglary-doe-kill-method-participant/schemas/kill-method-participant.schema.json"
FIXTURE_PATH = ROOT / "docs/proposals/active/siglary-doe-kill-method-participant/fixtures/kill-method-participant.valid.json"


def _type_ok(expected, value):
    types = expected if isinstance(expected, list) else [expected]
    for kind in types:
        if kind == "null" and value is None:
            return True
        if kind == "object" and isinstance(value, dict):
            return True
        if kind == "array" and isinstance(value, list):
            return True
        if kind == "string" and isinstance(value, str):
            return True
        if kind == "boolean" and isinstance(value, bool):
            return True
        if kind == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if kind == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
    return False


def validate(schema, value, path="$"):
    """Validate the JSON Schema keywords used by this closed contract."""
    errors = []

    for sub in schema.get("allOf", []):
        errors.extend(validate(sub, value, path))

    condition = schema.get("if")
    if condition is not None and not validate(condition, value, path):
        errors.extend(validate(schema.get("then", {}), value, path))

    if "type" in schema and not _type_ok(schema["type"], value):
        return [f"{path}: expected {schema['type']}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value is not in enum")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: shorter than minLength")
        if len(value) > schema.get("maxLength", sys.maxsize):
            errors.append(f"{path}: longer than maxLength")
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, value) is None:
            errors.append(f"{path}: pattern mismatch")
        fmt = schema.get("format")
        if fmt == "uri" and not urlsplit(value).scheme:
            errors.append(f"{path}: invalid URI")
        if fmt == "date-time":
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{path}: invalid date-time")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: fewer than minItems")
        if len(value) > schema.get("maxItems", sys.maxsize):
            errors.append(f"{path}: more than maxItems")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            errors.append(f"{path}: duplicate array items")
        if "items" in schema:
            for index, item in enumerate(value):
                errors.extend(validate(schema["items"], item, f"{path}[{index}]"))
        if "contains" in schema and not any(
            not validate(schema["contains"], item, f"{path}[*]") for item in value
        ):
            errors.append(f"{path}: required matching item absent")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: required property absent")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}.{key}: additional property forbidden")
        for key, subschema in properties.items():
            if key in value:
                errors.extend(validate(subschema, value[key], f"{path}.{key}"))

    return errors


def load_contract(schema_path=SCHEMA_PATH, fixture_path=FIXTURE_PATH):
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    fixture = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    return schema, fixture


def validate_record(record, schema=None):
    if schema is None:
        schema, _ = load_contract()
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        return ["schema: expected JSON Schema draft 2020-12"]
    if schema.get("properties", {}).get("schema_version", {}).get("const") != "kill-method-participant.v1":
        return ["schema: unexpected participant schema version"]
    return validate(schema, record)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--record", type=Path, default=FIXTURE_PATH)
    args = parser.parse_args(argv)
    try:
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    errors = validate_record(record, schema)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID: non-executable kill-method participant contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
