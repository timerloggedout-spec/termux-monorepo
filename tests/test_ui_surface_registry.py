"""Regression tests for the UI surface registry contract."""
import unittest

from scripts.validate_ui_surface_registry import validate


class RegistryContractTests(unittest.TestCase):
    def test_checked_in_registry_matches_schema_and_evidence_tree(self):
        self.assertEqual(validate(), [])


if __name__ == "__main__":
    unittest.main()
