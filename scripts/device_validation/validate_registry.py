#!/usr/bin/env python3
"""Validate QUE device-validation tool profiles and module lanes (stdlib only)."""
from __future__ import annotations

import argparse
import json
import re
import sys
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
EVIDENCE_CLASSES = {"verified", "candidate", "unknown", "stale"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]+$")
LANE_ID_RE = re.compile(r"^device-lane:[a-z0-9][a-z0-9._-]+$")


def _is_nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_registry(data: Any, repo_root: Path | None = None) -> list[str]:
    """Return deterministic validation errors; never mutate repository state."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["registry root must be an object"]

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
        if inventory.get("coverage") not in {"partial", "complete", "stale"}:
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

        required_strings = (
            "name", "family", "adapter_contract", "owner", "next_recon"
        )
        for field in required_strings:
            if not _is_nonempty(tool.get(field)):
                errors.append(f"{prefix}.{field} must be non-empty")
        enum_fields = (
            ("registration_state", REGISTRATION_STATES),
            ("implementation_state", IMPLEMENTATION_STATES),
            ("discovery_state", DISCOVERY_STATES),
            ("verification_state", VERIFICATION_STATES),
            ("availability_state", AVAILABILITY_STATES),
        )
        for field, allowed in enum_fields:
            if tool.get(field) not in allowed:
                errors.append(f"{prefix}.{field} has invalid value {tool.get(field)!r}")

        capabilities = tool.get("capabilities")
        if not isinstance(capabilities, list) or not all(_is_nonempty(x) for x in capabilities):
            errors.append(f"{prefix}.capabilities must be an array of non-empty strings")
        elif len(capabilities) != len(set(capabilities)):
            errors.append(f"{prefix}.capabilities contains duplicates")

        provenance = tool.get("provenance")
        if not isinstance(provenance, dict):
            errors.append(f"{prefix}.provenance must be an object")
        else:
            if "upstream_url" not in provenance or "revision" not in provenance or "license" not in provenance:
                errors.append(f"{prefix}.provenance must declare upstream_url, revision and license (null is allowed)")

        evidence = tool.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{prefix}.evidence must contain at least one evidence reference")
            evidence = []
        for e_index, item in enumerate(evidence):
            if not isinstance(item, dict) or not _is_nonempty(item.get("ref")):
                errors.append(f"{prefix}.evidence[{e_index}] must contain a non-empty ref")
            elif item.get("classification") not in EVIDENCE_CLASSES:
                errors.append(f"{prefix}.evidence[{e_index}].classification is invalid")

        if tool.get("verification_state") == "verified" and not any(
            isinstance(item, dict) and item.get("classification") == "verified"
            for item in evidence
        ):
            errors.append(f"{prefix}: verified profile requires verified evidence")

        if tool.get("availability_state") != "unknown" and not any(
            isinstance(item, dict)
            and item.get("kind") == "runtime_observation"
            and _is_nonempty(item.get("observed_at"))
            for item in evidence
        ):
            errors.append(f"{prefix}: non-unknown availability requires a timestamped runtime_observation")

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
        elif module_path in lane_paths:
            errors.append(f"duplicate module_path across lanes: {module_path}")
        else:
            lane_paths.add(module_path)

        for field in ("module_name", "evidence_policy", "reset_contract", "owner"):
            if not _is_nonempty(lane.get(field)):
                errors.append(f"{prefix}.{field} must be non-empty")
        if lane.get("lane_state") not in LANE_STATES:
            errors.append(f"{prefix}.lane_state is invalid")
        if lane.get("inventory_classification") not in {
            "verified_device_component", "candidate_device_component", "planned_device_component"
        }:
            errors.append(f"{prefix}.inventory_classification is invalid")

        profiles = lane.get("validation_profiles")
        if not isinstance(profiles, list) or not profiles:
            errors.append(f"{prefix}.validation_profiles must be a non-empty array")
        else:
            for profile_id in profiles:
                if profile_id not in tool_ids:
                    errors.append(f"{prefix} references unknown tool_profile_id: {profile_id}")

        hardware = lane.get("hardware_requirements")
        if not isinstance(hardware, dict) or not isinstance(hardware.get("required"), bool):
            errors.append(f"{prefix}.hardware_requirements.required must be boolean")
        elif hardware["required"]:
            referenced = [
                tool_by_id.get(profile_id, {})
                for profile_id in (profiles if isinstance(profiles, list) else [])
            ]
            if not any(profile.get("family") == "physical_device" for profile in referenced):
                errors.append(f"{prefix}: hardware-required lane must include a physical_device profile")

        evidence = lane.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{prefix}.evidence must contain at least one evidence reference")
        else:
            for e_index, item in enumerate(evidence):
                if not isinstance(item, dict) or not _is_nonempty(item.get("ref")):
                    errors.append(f"{prefix}.evidence[{e_index}] must contain a non-empty ref")
                elif item.get("classification") not in EVIDENCE_CLASSES:
                    errors.append(f"{prefix}.evidence[{e_index}].classification is invalid")

        if repo_root is not None and _is_nonempty(module_path):
            if lane.get("lane_state") in {"active", "discovered"}:
                if not (repo_root / module_path).exists():
                    errors.append(f"{prefix}: active/discovered module_path does not exist: {module_path}")

    if inventory and inventory.get("coverage") == "complete":
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
    args = parser.parse_args(argv)

    try:
        data = json.loads(args.registry.read_text(encoding="utf-8"))
        # Parse the schema as a structural artifact even when jsonschema is not installed.
        json.loads(args.schema.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: unable to read registry/schema: {exc}", file=sys.stderr)
        return 2

    errors = validate_registry(data, ROOT)
    result = {"ok": not errors, "errors": errors, "registry": str(args.registry)}
    if args.json:
        print(json.dumps(result, indent=2))
    elif errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
    else:
        print(f"OK: {len(data['tool_profiles'])} tool profiles; {len(data['module_lanes'])} module lanes; coverage={data['inventory']['coverage']}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
