#!/usr/bin/env python3
"""Contract tests for the machine-readable projection of the DoE settings register."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DoESettingsRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "ops/doe/settings-register.json").read_text())

    def test_schema_and_source_are_explicit(self):
        self.assertEqual(self.data["schema"], "doe.settings-register/v1")
        self.assertEqual(self.data["source"]["document"], "docs/ops/DOE-FAMILY.md")
        self.assertEqual(self.data["source"]["section"], "DoE version|settings register")

    def test_singular_global_version_is_not_invented(self):
        self.assertIsNone(self.data["doe_version"]["value"])
        self.assertEqual(self.data["doe_version"]["status"], "NOT_ESTABLISHED")

    def test_cycle_and_gate_values_match_register(self):
        cycle = self.data["cycle_parameters"]
        self.assertEqual(cycle["sets_per_cycle"], 3)
        self.assertEqual(cycle["rule_7"], {"floor_n": 3, "cap_n_per_trigger": 12})
        self.assertEqual(cycle["established_gate"], {
            "minimum_n": 30, "minimum_minority_n": 10, "p_value_less_than": 0.05
        })
        self.assertEqual(cycle["accumulation_bars_per_arm"]["mean_n"], 30)
        self.assertEqual(cycle["accumulation_bars_per_arm"]["variance_n"], 100)
        self.assertEqual(cycle["accumulation_bars_per_arm"]["claim_grade_proportion_n"], 384)

    def test_method_versions_and_epoch_artifacts_are_preserved(self):
        self.assertEqual(len(self.data["method_versions"]), 6)
        self.assertIn("doe-questions-matrix v1", self.data["method_versions"])
        self.assertIn("DOE-METHODS-EPOCH-2026-11-03", self.data["epoch_artifacts"])
        self.assertIn("DOE-ROLES-EPOCH-2026-11-03", self.data["epoch_artifacts"])

    def test_instance_aggregation_uses_configured_identity(self):
        rules = self.data["rules"]
        self.assertEqual(rules["instance_aggregation_key"], "instance_key")
        self.assertFalse(rules["model_alone_is_sufficient_instance_identity"])
        self.assertEqual(rules["missing_identity_representation"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
