"""Contract tests for the versioned telemetry equation registry.

These checks keep the machine-readable inventory, pure helper behavior, and
reference arithmetic aligned without evaluating arbitrary expression strings.
"""
import json
import math
import unittest
from pathlib import Path

from she.metrics.agent_throughput import (
    correlation_completeness,
    evidence_coverage_ratio,
    retry_amplification_ratio,
    retry_recovery_rate,
    validated_outcome_rate,
    validation_coverage,
    wilson_proportion_interval,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "docs/ops/TELEMETRY-EQUATION-REGISTRY.json"


class TelemetryEquationRegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_registry_has_version_and_unique_equation_ids(self):
        self.assertEqual(self.registry["schema_version"], "telemetry.equations.v1")
        records = self.registry["existing"] + self.registry["proposed"]
        ids = [record["id"] for record in records]
        self.assertEqual(len(ids), len(set(ids)), "equation IDs must be unique")
        for record in records:
            self.assertTrue(record["formula"].strip(), record["id"])
            self.assertTrue(record["name"].strip(), record["id"])
            self.assertTrue(record["status"].strip(), record["id"])

    def test_candidate_helpers_are_explicitly_not_runtime_metrics(self):
        candidates = {record["id"]: record for record in self.registry["proposed"]}
        expected = {
            "EQ-ECR-v1": evidence_coverage_ratio,
            "EQ-VOR-v1": validated_outcome_rate,
            "EQ-VCOV-v1": validation_coverage,
            "EQ-CORR-v1": correlation_completeness,
            "EQ-RAMP-v1": retry_amplification_ratio,
            "EQ-RREC-v1": retry_recovery_rate,
        }
        self.assertEqual(set(candidates), set(expected))
        for equation_id, helper in expected.items():
            record = candidates[equation_id]
            self.assertEqual(record["status"], "implemented-helper-not-emitted")
            self.assertIn("not emitted", record["integration_status"])
            self.assertEqual(record["implementation"], "she/metrics/agent_throughput.py")
            self.assertTrue(callable(helper))

    def test_wolfram_reference_fixtures_match_python_arithmetic(self):
        fixtures = {record["id"]: record for record in self.registry["wolfram_fixtures"]}
        expected_ids = {
            "WOLFRAM-C-01",
            "WOLFRAM-C-02",
            "WOLFRAM-ATES-01",
            "WOLFRAM-ECR-01",
            "WOLFRAM-VOR-01",
        }
        self.assertEqual(set(fixtures), expected_ids)
        calculated = {
            "WOLFRAM-C-01": math.log1p(9 + 1) * math.sqrt(1),
            "WOLFRAM-C-02": math.log1p(9 + 1) * math.sqrt(4),
            "WOLFRAM-ATES-01": 18 * (1 - 2 / 3) * (20 / (2 * 10)),
            "WOLFRAM-ECR-01": 4 / 5,
            "WOLFRAM-VOR-01": 3 / 4,
        }
        for fixture_id, value in calculated.items():
            with self.subTest(fixture=fixture_id):
                self.assertAlmostEqual(fixtures[fixture_id]["expected"], value, places=9)

    def test_candidate_ratio_examples_match_registry_contract(self):
        self.assertEqual(evidence_coverage_ratio(4, 5), 0.8)
        self.assertEqual(validated_outcome_rate(3, 4), 0.75)
        self.assertEqual(validation_coverage(4, 5), 0.8)
        self.assertEqual(correlation_completeness(9, 10), 0.9)

    def test_wilson_analysis_helper_is_registered_and_matches_fixture(self):
        helper = self.registry["analysis_helpers"]
        self.assertEqual(len(helper), 1)
        self.assertEqual(helper[0]["id"], "STAT-WILSON-v1")
        self.assertEqual(helper[0]["status"], "implemented-helper-not-emitted")
        self.assertIn("not emitted", helper[0]["integration_status"])
        self.assertEqual(wilson_proportion_interval(3, 4), (0.300636, 0.954414))
        self.assertEqual(wilson_proportion_interval(75, 100), (0.656954, 0.824549))

    def test_registry_preserves_no_standalone_merge_gate_invariant(self):
        self.assertIn("no-standalone-merge-gate", self.registry["invariants"])
        self.assertEqual(self.registry["status"], "documentation-proposal")


if __name__ == "__main__":
    unittest.main()
