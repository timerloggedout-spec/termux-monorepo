#!/usr/bin/env python3
"""Validate the L3VERAGE mechanism catalog using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "docs/leverage/mechanisms.json"
CLASSES = {"capability", "knowledge", "coordination", "automation", "measurement"}
STATES = {
    "discovered", "designed", "admitted", "experimenting", "validated",
    "promoted", "monitored", "rejected", "deferred", "blocked",
    "superseded", "retired",
}
RESOURCES = {
    "tokens", "wall_time", "compute_cost", "provider_cost", "retries",
    "human_minutes", "integration_effort", "maintenance_burden",
}
EVIDENCE_KINDS = {
    "experiment", "evidence_envelope", "commit", "pull_request",
    "workflow_run", "document",
}
ID_RE = re.compile(r"^L3V-[A-Z0-9-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["catalog must be a JSON object"]
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    if not isinstance(data.get("updated_at"), str) or not data["updated_at"]:
        errors.append("updated_at must be a non-empty timestamp string")
    mechanisms = data.get("mechanisms")
    if not isinstance(mechanisms, list):
        return errors + ["mechanisms must be an array"]

    seen: set[str] = set()
    required = {
        "id", "name", "primary_class", "lifecycle_state", "hypothesis",
        "trigger", "intervention", "target_outcomes", "resource_dimensions",
        "guardrails", "owner", "evidence_refs", "confidence",
    }
    allowed = required | {
        "secondary_classes", "related_capability_ids", "related_integration_ids",
        "experiment_id", "notes",
    }
    for index, item in enumerate(mechanisms):
        prefix = f"mechanisms[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(required - item.keys())
        if missing:
            errors.append(f"{prefix} missing required fields: {', '.join(missing)}")
            continue
        extra = sorted(item.keys() - allowed)
        if extra:
            errors.append(f"{prefix} contains unsupported fields: {', '.join(extra)}")
        identifier = item["id"]
        if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier):
            errors.append(f"{prefix}.id has invalid format")
        elif identifier in seen:
            errors.append(f"duplicate mechanism id: {identifier}")
        else:
            seen.add(identifier)

        if not isinstance(item["primary_class"], str) or item["primary_class"] not in CLASSES:
            errors.append(f"{prefix}.primary_class is invalid")
        if not isinstance(item["lifecycle_state"], str) or item["lifecycle_state"] not in STATES:
            errors.append(f"{prefix}.lifecycle_state is invalid")
        secondary = item.get("secondary_classes", [])
        if not isinstance(secondary, list) or any(not isinstance(value, str) or value not in CLASSES for value in secondary):
            errors.append(f"{prefix}.secondary_classes is invalid")
        for field in ("name", "hypothesis", "trigger", "intervention", "owner"):
            if not isinstance(item[field], str) or not item[field].strip():
                errors.append(f"{prefix}.{field} must be a non-empty string")
        for field in ("target_outcomes", "guardrails", "resource_dimensions", "evidence_refs"):
            if not isinstance(item[field], list):
                errors.append(f"{prefix}.{field} must be an array")
        for field in ("target_outcomes", "guardrails"):
            values = item[field]
            if isinstance(values, list) and (not values or any(not isinstance(value, str) or not value.strip() for value in values)):
                errors.append(f"{prefix}.{field} must contain non-empty strings")
        if isinstance(item["resource_dimensions"], list):
            dimensions = item["resource_dimensions"]
            invalid = {value for value in dimensions if not isinstance(value, str) or value not in RESOURCES}
            if not dimensions or invalid:
                errors.append(f"{prefix}.resource_dimensions contains invalid or empty values: {sorted(map(str, invalid))}")
        confidence = item["confidence"]
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
            errors.append(f"{prefix}.confidence must be between 0 and 1")
        refs = item["evidence_refs"]
        if isinstance(refs, list):
            for ref_index, ref in enumerate(refs):
                if not isinstance(ref, dict) or ref.get("kind") not in EVIDENCE_KINDS or not isinstance(ref.get("ref"), str) or not ref["ref"]:
                    errors.append(f"{prefix}.evidence_refs[{ref_index}] is malformed")
                elif "sha" in ref and (not isinstance(ref["sha"], str) or not SHA_RE.fullmatch(ref["sha"])):
                    errors.append(f"{prefix}.evidence_refs[{ref_index}].sha must be a 40-character lowercase SHA")
        if item["lifecycle_state"] in {"validated", "promoted", "monitored"}:
            if not isinstance(refs, list) or not refs:
                errors.append(f"{prefix} cannot be {item['lifecycle_state']} without evidence_refs")
            if not isinstance(item.get("experiment_id"), str) or not item["experiment_id"].strip():
                errors.append(f"{prefix} cannot be {item['lifecycle_state']} without experiment_id")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    args = parser.parse_args()
    try:
        data = json.loads(args.catalog.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read catalog: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {len(data['mechanisms'])} L3VERAGE mechanism hypotheses validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
