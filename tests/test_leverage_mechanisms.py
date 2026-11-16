"""Regression tests for the L3VERAGE mechanism catalog contract."""

import copy
import json
import unittest
from pathlib import Path

from scripts.leverage.validate_mechanisms import validate

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs/leverage/mechanisms.json"


class MechanismCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CATALOG.read_text(encoding="utf-8"))

    def test_seed_catalog_is_valid(self):
        self.assertEqual(validate(self.data), [])

    def test_duplicate_ids_are_rejected(self):
        data = copy.deepcopy(self.data)
        data["mechanisms"].append(copy.deepcopy(data["mechanisms"][0]))
        self.assertTrue(any("duplicate mechanism id" in error for error in validate(data)))

    def test_missing_required_field_is_rejected(self):
        data = copy.deepcopy(self.data)
        del data["mechanisms"][0]["intervention"]
        self.assertTrue(any("missing required fields" in error for error in validate(data)))

    def test_unknown_secondary_class_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["mechanisms"][0]["secondary_classes"] = ["magic"]
        self.assertTrue(any("secondary_classes is invalid" in error for error in validate(data)))

    def test_empty_required_arrays_are_rejected(self):
        data = copy.deepcopy(self.data)
        data["mechanisms"][0]["target_outcomes"] = []
        data["mechanisms"][0]["guardrails"] = []
        data["mechanisms"][0]["resource_dimensions"] = []
        errors = validate(data)
        self.assertTrue(any("target_outcomes" in error for error in errors))
        self.assertTrue(any("guardrails" in error for error in errors))
        self.assertTrue(any("resource_dimensions" in error for error in errors))

    def test_non_string_guardrail_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["mechanisms"][0]["guardrails"] = [42]
        self.assertTrue(any("guardrails" in error for error in validate(data)))

    def test_duplicate_resource_dimensions_are_rejected(self):
        data = copy.deepcopy(self.data)
        data["mechanisms"][0]["resource_dimensions"].append(data["mechanisms"][0]["resource_dimensions"][0])
        self.assertTrue(any("resource_dimensions contains duplicates" in error for error in validate(data)))

    def test_unknown_property_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["mechanisms"][0]["unreviewed_override"] = True
        self.assertTrue(any("unsupported fields" in error for error in validate(data)))

    def test_invalid_timestamp_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["updated_at"] = "yesterday"
        self.assertTrue(any("ISO 8601" in error for error in validate(data)))

    def test_malformed_lifecycle_type_is_rejected_without_crashing(self):
        data = copy.deepcopy(self.data)
        data["mechanisms"][0]["lifecycle_state"] = ["validated"]
        self.assertTrue(any("lifecycle_state is invalid" in error for error in validate(data)))

    def test_malformed_evidence_kind_is_rejected_without_crashing(self):
        data = copy.deepcopy(self.data)
        data["mechanisms"][0]["evidence_refs"] = [{"kind": [], "ref": "x"}]
        self.assertTrue(any("evidence_refs[0] is malformed" in error for error in validate(data)))

    def test_unknown_lifecycle_state_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["mechanisms"][0]["lifecycle_state"] = "deployed-ish"
        self.assertTrue(any("lifecycle_state is invalid" in error for error in validate(data)))

    def test_unknown_mechanism_class_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["mechanisms"][0]["primary_class"] = "magic"
        self.assertTrue(any("primary_class is invalid" in error for error in validate(data)))

    def test_validated_state_requires_evidence_and_experiment(self):
        data = copy.deepcopy(self.data)
        data["mechanisms"][0]["lifecycle_state"] = "validated"
        errors = validate(data)
        self.assertTrue(any("without evidence_refs" in error for error in errors))
        self.assertTrue(any("without experiment_id" in error for error in errors))

    def test_invalid_resource_dimension_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["mechanisms"][0]["resource_dimensions"].append("vibes")
        self.assertTrue(any("resource_dimensions contains invalid" in error for error in validate(data)))


if __name__ == "__main__":
    unittest.main()
