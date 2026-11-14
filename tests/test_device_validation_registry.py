"""Contract tests for the QUE device-validation registry and JSON Schema."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "device_validation" / "validate_registry.py"
SPEC = importlib.util.spec_from_file_location("device_validation_registry", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

REGISTRY = json.loads(
    (ROOT / "ops" / "device-validation" / "registry.json").read_text(encoding="utf-8")
)
FIXED_NOW = datetime(2026, 11, 14, 12, 0, tzinfo=timezone.utc)


class DeviceValidationRegistryTests(unittest.TestCase):
    def test_repository_registry_is_valid(self) -> None:
        self.assertEqual([], MODULE.validate_registry(REGISTRY, ROOT, now=FIXED_NOW))

    def test_duplicate_tool_profile_is_rejected(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["tool_profiles"].append(copy.deepcopy(data["tool_profiles"][0]))
        self.assertTrue(any("duplicate tool_profile_id" in e for e in MODULE.validate_registry(data)))

    def test_duplicate_module_lane_is_rejected(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["module_lanes"].append(copy.deepcopy(data["module_lanes"][0]))
        self.assertTrue(any("duplicate module_lane_id" in e for e in MODULE.validate_registry(data)))

    def test_unregistered_backend_reference_is_rejected(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["module_lanes"][0]["validation_profiles"] = ["missing-profile"]
        self.assertTrue(any("references unknown tool_profile_id" in e for e in MODULE.validate_registry(data)))

    def test_unadvertised_lane_capability_is_rejected(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["module_lanes"][0]["required_capabilities"].append("sensor.accelerometer")
        self.assertTrue(any("requires capability not advertised" in e for e in MODULE.validate_registry(data)))

    def test_available_requires_fresh_runtime_observation(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["tool_profiles"][0]["availability_state"] = "available"
        self.assertTrue(any("current, verified runtime_observation" in e for e in MODULE.validate_registry(data, now=FIXED_NOW)))

    def test_fresh_verified_observation_supports_available(self) -> None:
        data = copy.deepcopy(REGISTRY)
        profile = data["tool_profiles"][0]
        profile["availability_state"] = "available"
        profile["evidence"].append({
            "kind": "runtime_observation",
            "ref": "workflow-run:123",
            "classification": "verified",
            "observed_at": "2026-11-14T00:00:00Z",
            "expires_at": "2026-11-15T00:00:00Z",
            "notes": "fresh test fixture"
        })
        self.assertEqual([], MODULE.validate_registry(data, ROOT, now=FIXED_NOW))

    def test_expired_observation_cannot_claim_available(self) -> None:
        data = copy.deepcopy(REGISTRY)
        profile = data["tool_profiles"][0]
        profile["availability_state"] = "available"
        profile["evidence"].append({
            "kind": "runtime_observation",
            "ref": "workflow-run:expired",
            "classification": "stale",
            "observed_at": "2020-01-01T00:00:00Z",
            "expires_at": "2020-01-02T00:00:00Z",
            "notes": "expired test fixture"
        })
        self.assertTrue(any("current, verified runtime_observation" in e for e in MODULE.validate_registry(data, now=FIXED_NOW)))

    def test_future_observation_cannot_claim_available(self) -> None:
        data = copy.deepcopy(REGISTRY)
        profile = data["tool_profiles"][0]
        profile["availability_state"] = "available"
        profile["evidence"].append({
            "kind": "runtime_observation",
            "ref": "workflow-run:future",
            "classification": "verified",
            "observed_at": "2026-11-15T00:00:00Z",
            "expires_at": "2026-11-16T00:00:00Z",
            "notes": "future test fixture"
        })
        self.assertTrue(any("current, verified runtime_observation" in e for e in MODULE.validate_registry(data, now=FIXED_NOW)))

    def test_verified_requires_verified_evidence(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["tool_profiles"][0]["evidence"][0]["classification"] = "candidate"
        data["tool_profiles"][0]["evidence"][1]["classification"] = "candidate"
        self.assertTrue(any("verified profile requires verified evidence" in e for e in MODULE.validate_registry(data)))

    def test_hardware_lane_requires_physical_backend(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["module_lanes"][0]["hardware_requirements"] = {
            "required": True,
            "capabilities": ["usb.device"],
        }
        self.assertTrue(any("must include a physical_device profile" in e for e in MODULE.validate_registry(data)))

    def test_planned_lane_may_point_to_not_yet_created_module(self) -> None:
        data = copy.deepcopy(REGISTRY)
        next(x for x in data["module_lanes"] if x["lane_state"] == "planned")
        self.assertFalse(any("module_path does not exist" in e for e in MODULE.validate_registry(data, ROOT)))

    def test_module_path_traversal_is_rejected(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["module_lanes"][0]["module_path"] = "../../outside"
        self.assertTrue(any("repository-relative path without traversal" in e for e in MODULE.validate_registry(data)))

    def test_schema_rejects_missing_required_fields(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data.pop("updated_at")
        data["tool_profiles"][0].pop("host_requirements")
        data["tool_profiles"][0].pop("resource_profile")
        data["tool_profiles"][0].pop("exclusions")
        data["tool_profiles"][0]["evidence"][0].pop("kind")
        errors = MODULE.validate_registry(data)
        self.assertTrue(any("updated_at" in e for e in errors))
        self.assertTrue(any("host_requirements" in e for e in errors))
        self.assertTrue(any("resource_profile" in e for e in errors))
        self.assertTrue(any("exclusions" in e for e in errors))
        self.assertTrue(any("kind" in e for e in errors))

    def test_schema_rejects_unknown_properties(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["tool_profiles"][0]["unregistered_extra"] = True
        self.assertTrue(any("unknown property 'unregistered_extra'" in e for e in MODULE.validate_registry(data)))

    def test_schema_rejects_nested_types_and_enum_values(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["tool_profiles"][0]["family"] = "imaginary-emulator"
        data["tool_profiles"][0]["host_requirements"]["os"] = "linux"
        errors = MODULE.validate_registry(data)
        self.assertTrue(any("not in enum" in e for e in errors))
        self.assertTrue(any("expected type 'array'" in e for e in errors))

    def test_schema_enforces_unique_items_and_numeric_bounds(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["tool_profiles"][0]["capabilities"].append(data["tool_profiles"][0]["capabilities"][0])
        data["tool_profiles"][0]["resource_profile"]["cpu"] = 0
        errors = MODULE.validate_registry(data)
        self.assertTrue(any("array items must be unique" in e for e in errors))
        self.assertTrue(any("below minimum" in e for e in errors))

    def test_complete_inventory_requires_reconciliation_date(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["inventory"]["coverage"] = "complete"
        data["inventory"]["last_reconciled_at"] = None
        self.assertTrue(any("complete inventory requires last_reconciled_at" in e for e in MODULE.validate_registry(data)))

    def test_non_object_root_is_rejected(self) -> None:
        self.assertEqual(["registry root must be an object"], MODULE.validate_registry([]))


if __name__ == "__main__":
    unittest.main()
