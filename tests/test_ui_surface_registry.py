"""Regression tests for the UI surface registry contract."""
import importlib.util
import unittest
from pathlib import Path

VALIDATOR_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate-ui-surface-registry.py"
SPEC = importlib.util.spec_from_file_location("validate_ui_surface_registry", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load registry validator from {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class RegistryContractTests(unittest.TestCase):
    def test_checked_in_registry_matches_schema_and_evidence_tree(self):
        self.assertEqual(VALIDATOR.validate(), [])


if __name__ == "__main__":
    unittest.main()
