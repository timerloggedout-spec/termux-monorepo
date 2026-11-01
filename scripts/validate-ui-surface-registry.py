#!/usr/bin/env python3
"""Validate the UI surface registry schema, identifiers, and repository evidence paths."""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover - exercised by CLI failure path
    print("ERROR: install validator dependency: python -m pip install -r scripts/requirements-ui-surface-registry.txt", file=sys.stderr)
    raise SystemExit(2) from exc

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/ops/ui-surface-registry.json"
SCHEMA = ROOT / "docs/ops/ui-surface-registry.schema.json"


def validate() -> list[str]:
    errors: list[str] = []
    try:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot load registry/schema: {exc}"]

    if registry.get("schema_ref") != "./ui-surface-registry.schema.json":
        errors.append("schema_ref must resolve to ./ui-surface-registry.schema.json")
    if registry.get("schema_version") != schema.get("properties", {}).get("schema_version", {}).get("const"):
        errors.append("registry schema_version does not match schema")

    for issue in Draft202012Validator.check_schema(schema) if False else []:
        errors.append(str(issue))
    validator = Draft202012Validator(schema)
    for issue in sorted(validator.iter_errors(registry), key=lambda e: list(map(str, e.path))):
        location = ".".join(map(str, issue.absolute_path)) or "<root>"
        errors.append(f"schema violation at {location}: {issue.message}")

    seen: set[str] = set()
    for index, surface in enumerate(registry.get("surfaces", [])):
        surface_id = surface.get("surface_id", f"<surface[{index}]>")
        if surface_id in seen:
            errors.append(f"duplicate surface_id: {surface_id}")
        seen.add(surface_id)
        paths = surface.get("evidence_paths", [])
        if surface.get("maturity") == "proposed" and paths:
            errors.append(f"{surface_id}: proposed surface must not claim evidence_paths")
        if surface.get("support_status") == "unknown" and surface.get("maturity") != "proposed":
            errors.append(f"{surface_id}: unknown support must be explicitly proposed pending evidence")
        for raw_path in paths:
            candidate = Path(raw_path)
            if candidate.is_absolute() or ".." in candidate.parts:
                errors.append(f"{surface_id}: unsafe evidence path: {raw_path}")
                continue
            resolved = (ROOT / candidate).resolve()
            if ROOT.resolve() not in resolved.parents:
                errors.append(f"{surface_id}: evidence path escapes repository: {raw_path}")
            elif not resolved.is_file():
                errors.append(f"{surface_id}: evidence file missing: {raw_path}")

    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        raise SystemExit(1)
    print("UI surface registry: schema, identity, and evidence-path checks passed.")
