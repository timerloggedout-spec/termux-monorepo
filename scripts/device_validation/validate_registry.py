#!/usr/bin/env python3
"""Validate the QUE device-validation registry and its JSON Schema (stdlib only)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "ops" / "device-validation" / "registry.json"
SCHEMA = ROOT / "ops" / "device-validation" / "registry.schema.json"

REGISTRATION_STATES = {"proposed", "registered", "retired"}
IMPLEMENTATION_STATES = {"absent", "planned", "implemented"}
DISCOVERY_STATES = {"not_checked", "discovered", "not_found"}
VERIFICATION_STATES = {"unverified", "verified", "failed", "stale"}
AVAILABILITY_STATES = {"unknown", "available", "unavailable", "degraded"}
LANE_STATES = {"discovered", "planned", "active", "retired"}
TOOL_FAMILIES = {"android_avd", "termux_native", "termux_container", "qemu", "waydroid", "physical_device", "linux_container", "other"}
EVIDENCE_CLASSES = {"verified", "candidate", "unknown", "stale"}
SUPPORTED_SCHEMA_KEYS = { "$schema", "$id", "$defs", "$ref", "title", "description", "type", "additionalProperties", "required", "properties", "items", "enum", "const", "pattern", "minLength", "minimum", "minItems", "uniqueItems", "format" }
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]+$")
LANE_ID_RE = re.compile(r"^device-lane:[a-z0-9][a-z0-9._-]+$")


def _is_nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


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
    return True


def _resolve_local_ref(root_schema: dict[str, Any], ref: str) -> dict[str, Any] | None:
    if not ref.startswith("#/"):
        return None
    current: Any = root_schema
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            return None
        current = current[token]
    return current if isinstance(current, dict) else None


def _format_valid(value: str, fmt: str) -> bool:
    try:
        if fmt == "date":
            date.fromisoformat(value)
            return True
        if fmt == "date-time":
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except (TypeError, ValueError, OverflowError):
        return False
    return True


def validate_schema_contract(schema: Any, path: str = "$") -> list[str]:
    """Fail closed if the registry schema starts using unsupported JSON Schema keywords."""
    if not isinstance(schema, dict):
        return [f"{path}: schema node must be an object"]
    errors = [f"{path}: unsupported schema keyword {key!r}" for key in schema if key not in SUPPORTED_SCHEMA_KEYS]
    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        for key, child in properties.items():
            errors.extend(validate_schema_contract(child, f"{path}.properties.{key}"))
    definitions = schema.get("$defs", {})
    if isinstance(definitions, dict):
        for key, child in definitions.items():
            errors.extend(validate_schema_contract(child, f"{path}.$defs.{key}"))
    if isinstance(schema.get("items"), dict):
        errors.extend(validate_schema_contract(schema["items"], f"{path}.items"))
    if isinstance(schema.get("additionalProperties"), dict):
        errors.extend(validate_schema_contract(schema["additionalProperties"], f"{path}.additionalProperties"))
    if schema.get("format") not in (None, "date", "date-time"):
        errors.append(f"{path}: unsupported format {schema.get('format')!r}")
    return errors


def validate_json_schema(
    value: Any, schema: dict[str, Any], root_schema: dict[str, Any] | None = None,
    path: str = "$",
) -> list[str]:
    """Validate the JSON Schema vocabulary used by this registry, without dependencies."""
    root = root_schema or schema
    errors: list[str] = []

    ref = schema.get("$ref")
    if ref:
        target = _resolve_local_ref(root, ref)
        if target is None:
            return [f"{path}: unresolved or unsupported schema reference {ref!r}"]
        return validate_json_schema(value, target, root, path)

    expected = schema.get("type")
    if expected is not None:
        types = expected if isinstance(expected, list) else [expected]
        if not any(_type_matches(value, kind) for kind in types):
            return [f"{path}: expected type {expected!r}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: value must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} is not in enum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string shorter than minLength")
        pattern = schema.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            errors.append(f"{path}: string does not match pattern {pattern!r}")
        fmt = schema.get("format")
        if fmt and not _format_valid(value, fmt):
            errors.append(f"{path}: invalid {fmt} value {value!r}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: value is below minimum {schema['minimum']}")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: array shorter than minItems")
        if schema.get("uniqueItems"):
            fingerprints = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in value]
            if len(fingerprints) != len(set(fingerprints)):
                errors.append(f"{path}: array items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_json_schema(item, item_schema, root, f"{path}[{index}]"))

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            errors.append(f"{path}: schema properties must be an object")
            properties = {}
        for key, child_schema in properties.items():
            if key in value and isinstance(child_schema, dict):
                errors.extend(validate_json_schema(value[key], child_schema, root, f"{path}.{key}"))
        additional = schema.get("additionalProperties")
        if additional is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}: unknown property {key!r}")
        elif isinstance(additional, dict):
            for key, child_value in value.items():
                if key not in properties:
                    errors.extend(validate_json_schema(child_value, additional, root, f"{path}.{key}"))

    return errors


def _parse_utc(value: Any) -> datetime | None:
    if not _is_nonempty(value):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError, OverflowError):
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def validate_registry(
    data: Any,
    repo_root: Path | None = None,
    schema: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> list[str]:
    """Return deterministic schema + semantic errors; never mutate repository state."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["registry root must be an object"]

    if schema is None and SCHEMA.exists():
        try:
            schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"unable to load registry schema: {exc}")
    if schema is not None:
        errors.extend(validate_schema_contract(schema))
        errors.extend(validate_json_schema(data, schema))

    expected = {
        "schema_version": "1.0.0",
        "registry_id": "termux-monorepo.device-validation",
        "repository": "timerloggedout-spec/termux-monorepo",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            errors.append(f"{key} must equal {value!r}")

    inventory = data.get("inventory")
    if not isinstance(inventory, dict):
        errors.append("inventory must be an object")
    else:
        if not isinstance(inventory.get("coverage"), str) or inventory.get("coverage") not in {"partial", "complete", "stale"}:
            errors.append("inventory.coverage must be partial, complete or stale")
        if not _is_nonempty(inventory.get("recon_scope")):
            errors.append("inventory.recon_scope must be non-empty")
        if inventory.get("last_reconciled_at") is not None and not _is_nonempty(inventory.get("last_reconciled_at")):
            errors.append("inventory.last_reconciled_at must be a date string or null")

    tools = data.get("tool_profiles")
    lanes = data.get("module_lanes")
    if not isinstance(tools, list):
        errors.append("tool_profiles must be an array")
        tools = []
    if not isinstance(lanes, list):
        errors.append("module_lanes must be an array")
        lanes = []

    reference_time = now or datetime.now(timezone.utc)
    if reference_time.tzinfo is None or reference_time.utcoffset() is None:
        errors.append("reference time must be timezone-aware")
        reference_time = reference_time.replace(tzinfo=timezone.utc)
    reference_time = reference_time.astimezone(timezone.utc)

    tool_ids: set[str] = set()
    tool_by_id: dict[str, dict[str, Any]] = {}
    for index, tool in enumerate(tools):
        prefix = f"tool_profiles[{index}]"
        if not isinstance(tool, dict):
            errors.append(f"{prefix} must be an object")
            continue
        tool_id = tool.get("tool_profile_id")
        if not _is_nonempty(tool_id) or not ID_RE.fullmatch(tool_id or ""):
            errors.append(f"{prefix}.tool_profile_id is missing or invalid")
        elif tool_id in tool_ids:
            errors.append(f"duplicate tool_profile_id: {tool_id}")
        else:
            tool_ids.add(tool_id)
            tool_by_id[tool_id] = tool

        if not isinstance(tool.get("family"), str) or tool.get("family") not in TOOL_FAMILIES:
            errors.append(f"{prefix}.family has invalid value")
        if not isinstance(tool.get("registration_state"), str) or tool.get("registration_state") not in REGISTRATION_STATES:
            errors.append(f"{prefix}.registration_state is invalid")
        if not isinstance(tool.get("implementation_state"), str) or tool.get("implementation_state") not in IMPLEMENTATION_STATES:
            errors.append(f"{prefix}.implementation_state is invalid")
        if not isinstance(tool.get("discovery_state"), str) or tool.get("discovery_state") not in DISCOVERY_STATES:
            errors.append(f"{prefix}.discovery_state is invalid")
        if not isinstance(tool.get("verification_state"), str) or tool.get("verification_state") not in VERIFICATION_STATES:
            errors.append(f"{prefix}.verification_state is invalid")
        if not isinstance(tool.get("availability_state"), str) or tool.get("availability_state") not in AVAILABILITY_STATES:
            errors.append(f"{prefix}.availability_state is invalid")

        evidence = tool.get("evidence")
        if not isinstance(evidence, list):
            evidence = []
        if tool.get("verification_state") == "verified" and not any(
            isinstance(item, dict) and item.get("classification") == "verified"
            for item in evidence
        ):
            errors.append(f"{prefix}: verified profile requires verified evidence")

        if tool.get("availability_state") != "unknown":
            fresh = False
            for item in evidence:
                if not isinstance(item, dict) or item.get("kind") != "runtime_observation":
                    continue
                observed = _parse_utc(item.get("observed_at"))
                expires = _parse_utc(item.get("expires_at"))
                if (
                    item.get("classification") == "verified"
                    and observed is not None
                    and expires is not None
                    and observed <= reference_time < expires
                    and expires > observed
                ):
                    fresh = True
                    break
            if not fresh:
                errors.append(
                    f"{prefix}: non-unknown availability requires a current, verified runtime_observation "
                    "with valid observed_at and expires_at"
                )

    lane_ids: set[str] = set()
    lane_paths: set[str] = set()
    for index, lane in enumerate(lanes):
        prefix = f"module_lanes[{index}]"
        if not isinstance(lane, dict):
            errors.append(f"{prefix} must be an object")
            continue
        lane_id = lane.get("module_lane_id")
        if not _is_nonempty(lane_id) or not LANE_ID_RE.fullmatch(lane_id or ""):
            errors.append(f"{prefix}.module_lane_id is missing or invalid")
        elif lane_id in lane_ids:
            errors.append(f"duplicate module_lane_id: {lane_id}")
        else:
            lane_ids.add(lane_id)

        module_path = lane.get("module_path")
        if not _is_nonempty(module_path):
            errors.append(f"{prefix}.module_path must be non-empty")
        elif Path(module_path).is_absolute() or ".." in Path(module_path).parts:
            errors.append(f"{prefix}.module_path must be a repository-relative path without traversal: {module_path}")
        elif module_path in lane_paths:
            errors.append(f"duplicate module_path across lanes: {module_path}")
        else:
            lane_paths.add(module_path)

        if not isinstance(lane.get("lane_state"), str) or lane.get("lane_state") not in LANE_STATES:
            errors.append(f"{prefix}.lane_state is invalid")
        if not isinstance(lane.get("inventory_classification"), str) or lane.get("inventory_classification") not in {
            "verified_device_component", "candidate_device_component", "planned_device_component"
        }:
            errors.append(f"{prefix}.inventory_classification is invalid")

        profiles = lane.get("validation_profiles")
        if not isinstance(profiles, list):
            profiles = []
        advertised: set[str] = set()
        for profile_id in profiles:
            if not _is_nonempty(profile_id) or profile_id not in tool_ids:
                errors.append(f"{prefix} references unknown tool_profile_id: {profile_id}")
                continue
            profile_capabilities = tool_by_id[profile_id].get("capabilities", [])
            if isinstance(profile_capabilities, list):
                advertised.update(capability for capability in profile_capabilities if _is_nonempty(capability))
        required = lane.get("required_capabilities", [])
        if isinstance(required, list):
            for capability in required:
                if _is_nonempty(capability) and capability not in advertised:
                    errors.append(f"{prefix} requires capability not advertised by its validation profiles: {capability}")

        hardware = lane.get("hardware_requirements")
        if isinstance(hardware, dict) and hardware.get("required") is True:
            referenced = [
                tool_by_id.get(profile_id, {})
                for profile_id in profiles
                if _is_nonempty(profile_id)
            ]
            if not any(profile.get("family") == "physical_device" for profile in referenced):
                errors.append(f"{prefix}: hardware-required lane must include a physical_device profile")

        if repo_root is not None and _is_nonempty(module_path):
            if lane.get("lane_state") in {"active", "discovered"}:
                if not (repo_root / module_path).exists():
                    errors.append(f"{prefix}: active/discovered module_path does not exist: {module_path}")

    if isinstance(inventory, dict) and inventory.get("coverage") == "complete":
        if not _is_nonempty(inventory.get("last_reconciled_at")):
            errors.append("complete inventory requires last_reconciled_at")
        if not lanes:
            errors.append("complete inventory requires at least one module lane")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--json", action="store_true", help="emit machine-readable result")
    parser.add_argument("--now", help="inject an RFC3339 reference time for deterministic freshness tests")
    args = parser.parse_args(argv)

    try:
        data = json.loads(args.registry.read_text(encoding="utf-8"))
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: unable to read registry/schema: {exc}", file=sys.stderr)
        return 2

    reference_time = _parse_utc(args.now) if args.now else None
    if args.now and reference_time is None:
        print("FAIL: --now must be a timezone-aware RFC3339 timestamp", file=sys.stderr)
        return 2

    errors = validate_registry(data, ROOT, schema=schema, now=reference_time)
    result = {
        "ok": not errors,
        "errors": errors,
        "registry": str(args.registry),
        "tool_profiles": len(data.get("tool_profiles", [])) if isinstance(data, dict) and isinstance(data.get("tool_profiles"), list) else None,
        "module_lanes": len(data.get("module_lanes", [])) if isinstance(data, dict) and isinstance(data.get("module_lanes"), list) else None,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    elif errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
    else:
        print(
            f"OK: {result['tool_profiles']} tool profiles; "
            f"{result['module_lanes']} module lanes; "
            f"coverage={data['inventory']['coverage']}"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
