import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/ops/validate_flywheel_comms_registry.py"
SPEC = importlib.util.spec_from_file_location("flywheel_comms_registry_validator", VALIDATOR_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)


class FlywheelCommsRegistryTests(unittest.TestCase):
    def test_current_registry_passes(self):
        registry = json.loads(
            (ROOT / "docs/ops/flywheel-comms/REGISTRY.json").read_text(encoding="utf-8")
        )
        self.assertEqual(VALIDATOR.validate_registry(registry), [])

    def test_mandatory_is_valid_without_establishment_claim(self):
        registry = {"channels": [{"id": "FLY-014", "status": "mandatory"}]}
        self.assertEqual(VALIDATOR.validate_registry(registry), [])
        self.assertNotEqual(registry["channels"][0]["status"], "established")

    def test_established_still_requires_evidence_reference(self):
        registry = {"channels": [{"id": "FLY-014", "status": "established"}]}
        self.assertTrue(
            any("without an evidence reference" in error
                for error in VALIDATOR.validate_registry(registry))
        )

    def test_established_accepts_existing_round_trip_evidence_field(self):
        registry = {
            "channels": [{
                "id": "FLY-014",
                "status": "established",
                "established_evidence": "participant A message + participant B ACK",
            }]
        }
        self.assertEqual(VALIDATOR.validate_registry(registry), [])

    def test_unknown_status_and_duplicate_ids_fail(self):
        registry = {
            "channels": [
                {"id": "FLY-014", "status": "promoted"},
                {"id": "FLY-014", "status": "proposed"},
            ]
        }
        errors = VALIDATOR.validate_registry(registry)
        self.assertTrue(any(".status must be one of" in error for error in errors))
        self.assertTrue(any("duplicates FLY-014" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
