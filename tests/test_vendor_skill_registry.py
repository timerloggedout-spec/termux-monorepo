"""Focused contract tests for AMD/NVIDIA skill registry metadata."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/ci/validate_vendor_skill_registry.py"
SPEC = importlib.util.spec_from_file_location("vendor_registry_validator", VALIDATOR_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class VendorSkillRegistryTests(unittest.TestCase):
    def test_registries_and_schema_validate(self):
        VALIDATOR.validate()

    def test_amd_entries_are_not_claimed_as_executed(self):
        entries = json.loads((ROOT / "docs/ops/amd-skills-registry.json").read_text())
        self.assertGreaterEqual(len(entries), 1)
        self.assertTrue(all(e["execution_status"] == "not_run" for e in entries))

    def test_nvidia_catalog_is_discovery_only(self):
        entries = json.loads((ROOT / "docs/ops/nvidia-skills-registry.json").read_text())
        self.assertEqual(entries[0]["status"], "discovered_reference_only")
        self.assertEqual(entries[0]["execution_status"], "not_run")

    def test_sensitive_field_names_are_rejected(self):
        with self.assertRaises(ValueError):
            VALIDATOR.inspect_value({"access_token": "do-not-store"})


if __name__ == "__main__":
    unittest.main()
