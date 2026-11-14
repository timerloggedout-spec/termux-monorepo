"""Contract tests for the QUE device-validation registry."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
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


class DeviceValidationRegistryTests(unittest.TestCase):
    def test_repository_registry_is_valid(self) -> None:
        self.assertEqual([], MODULE.validate_registry(REGISTRY, ROOT))

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

    def test_available_requires_fresh_runtime_observation(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["tool_profiles"][0]["availability_state"] = "available"
        self.assertTrue(any("timestamped runtime_observation" in e for e in MODULE.validate_registry(data)))

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
        lane = next(x for x in data["module_lanes"] if x["lane_state"] == "planned")
        self.assertFalse(any("module_path does not exist" in e for e in MODULE.validate_registry(data, ROOT)))

    def test_complete_inventory_requires_reconciliation_date(self) -> None:
        data = copy.deepcopy(REGISTRY)
        data["inventory"]["coverage"] = "complete"
        data["inventory"]["last_reconciled_at"] = None
        self.assertTrue(any("complete inventory requires last_reconciled_at" in e for e in MODULE.validate_registry(data)))

    def test_non_object_root_is_rejected(self) -> None:
        self.assertEqual(["registry root must be an object"], MODULE.validate_registry([]))


if __name__ == "__main__":
    unittest.main()
