#!/usr/bin/env python3
"""Validate vendor skill registries and the execution receipt JSON Schema."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRIES = {
    ROOT / "docs/ops/amd-skills-registry.json": {"prefix": "amd.", "statuses": {"installed_in_assistant_environment"}},
    ROOT / "docs/ops/nvidia-skills-registry.json": {"prefix": "nvidia.", "statuses": {"discovered_reference_only"}},
}
SCHEMA = ROOT / "docs/ops/AMD-NVIDIA-SKILL-EXECUTION-RECEIPT.schema.json"
FORBIDDEN_KEYS = re.compile(r"(api[_-]?key|access[_-]?token|password|secret|prompt|completion|private[_-]?key)", re.I)


def inspect_value(value, path="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            if FORBIDDEN_KEYS.search(key):
                raise ValueError(f"{path}: forbidden sensitive/payload field name: {key}")
            inspect_value(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            inspect_value(child, f"{path}[{index}]")


def validate():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = {"receipt_version", "skill_id", "status", "execution_status", "timestamp", "environment", "workload", "evaluation", "metrics", "result", "limitations"}
    if schema.get("type") != "object" or not required.issubset(set(schema.get("required", []))):
        raise ValueError(f"{SCHEMA}: missing required receipt contract fields")
    for path, policy in REGISTRIES.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list) or not data:
            raise ValueError(f"{path}: registry must be a non-empty JSON array")
        seen = set()
        for index, entry in enumerate(data):
            where = f"{path.name}[{index}]"
            if not isinstance(entry, dict):
                raise ValueError(f"{where}: entry must be an object")
            for field in ("id", "status", "upstream_ref", "execution_status"):
                if not isinstance(entry.get(field), str) or not entry[field].strip():
                    raise ValueError(f"{where}: missing/non-string {field}")
            if not entry["id"].startswith(policy["prefix"]):
                raise ValueError(f"{where}: id must start with {policy['prefix']}")
            if entry["id"] in seen:
                raise ValueError(f"{where}: duplicate id {entry['id']}")
            seen.add(entry["id"])
            if entry["status"] not in policy["statuses"]:
                raise ValueError(f"{where}: unapproved status {entry['status']}")
            if entry["execution_status"] not in {"not_run", "blocked", "executed", "validated"}:
                raise ValueError(f"{where}: invalid execution_status {entry['execution_status']}")
            if not (entry["upstream_ref"].startswith("https://") or entry["upstream_ref"].startswith("skills://")):
                raise ValueError(f"{where}: upstream_ref must be an https or skills reference")
            inspect_value(entry, where)
    print("Vendor skill registries and execution receipt schema: OK")


if __name__ == "__main__":
    try:
        validate()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
