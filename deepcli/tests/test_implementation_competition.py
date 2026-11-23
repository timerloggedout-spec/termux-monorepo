"""Regression tests for matched tournament implementation comparison."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "deepcli"))
from deepcli.observatory.implementation_competition import compare_implementations


def receipt(implementation, version, task, quality, latency, *, cost, accepted=True):
    return {
        "schema": "tournament.implementation-receipt.v1",
        "implementation_id": implementation,
        "implementation_version": version,
        "competition_role": "incumbent" if implementation == "incumbent" else "challenger",
        "cohort_id": "cohort-2026-11",
        "task_id": task,
        "task_contract_hash": "sha256:task-contract",
        "environment_fingerprint": "sha256:environment",
        "evaluator_version": "evaluator-1.0.0",
        "run_id": f"{implementation}-{task}",
        "outcome": "SUCCEEDED" if accepted else "FAILED",
        "hard_gates": {
            "task_contract_valid": True,
            "schema_valid": True,
            "security_and_policy": True,
            "provenance_complete": True,
            "deterministic_checks": True,
        },
        "metric_set": ["task_quality", "latency_ms", "compute_cost"],
        "metrics": {
            "task_quality": quality,
            "latency_ms": latency,
            "compute_cost": cost,
        },
    }


class ImplementationCompetitionTests(unittest.TestCase):
    def setUp(self):
        self.receipts = []
        for index, (task, quality, latency) in enumerate(
            [("a", .7, 120), ("b", .8, 100), ("c", .6, 140)]
        ):
            self.receipts.append(receipt("incumbent", "1.0.0", task, quality, latency, cost=10))
            self.receipts.append(receipt(
                "challenger", "1.1.0", task,
                quality + .1 + index * .001,
                latency - 10 - index * .1,
                cost=9 + index * .01,
            ))

    def test_matched_comparison_reports_paired_effects_and_uncertainty(self):
        report = compare_implementations(self.receipts)
        self.assertEqual(report["receipt_schema"], "tournament.implementation-receipt.v1")
        self.assertEqual(report["matched_task_count"], 3)
        self.assertEqual(report["metrics"]["task_quality"]["sample_count"], 3)
        self.assertAlmostEqual(report["metrics"]["task_quality"]["improvement_mean"], .1)
        self.assertIsNotNone(report["metrics"]["task_quality"]["ci95"])
        self.assertEqual(report["metrics"]["task_quality"]["interval_status"], "estimated")
        self.assertEqual(report["recommendation"], "challenger_for_human_review")

    def test_missing_metrics_remain_null_and_reduce_sample_count(self):
        self.receipts[0]["metrics"]["task_quality"] = None
        for item in self.receipts:
            item["metrics"]["compute_cost"] = None
        report = compare_implementations(self.receipts)
        self.assertEqual(report["metrics"]["task_quality"]["sample_count"], 2)
        self.assertEqual(report["metrics"]["compute_cost"]["sample_count"], 0)
        self.assertEqual(report["metrics"]["compute_cost"]["interval_status"], "no_observations")
        self.assertIn("compute_cost", report["unobserved_metrics"])
        self.assertIsNone(report["metrics"]["compute_cost"]["improvement_mean"])
        self.assertEqual(report["recommendation"], "pareto_tradeoff_or_insufficient_evidence")

    def test_partial_metric_coverage_blocks_dominance(self):
        self.receipts[3]["metrics"]["task_quality"] = None
        report = compare_implementations(self.receipts)
        self.assertIn("task_quality", report["incomplete_metrics"])
        self.assertEqual(report["recommendation"], "pareto_tradeoff_or_insufficient_evidence")

    def test_small_sample_interval_uses_student_t_critical_value(self):
        receipts = self.receipts[:4]
        receipts[3]["metrics"]["task_quality"] += .1
        report = compare_implementations(receipts)
        interval = report["metrics"]["task_quality"]["ci95"]
        self.assertGreater(interval[1] - interval[0], 1.0)

    def test_zero_observed_variance_does_not_create_degenerate_interval(self):
        receipts = self.receipts[:4]
        receipts[3]["metrics"]["task_quality"] = receipts[2]["metrics"]["task_quality"] + .1
        receipts[3]["metrics"]["latency_ms"] = receipts[2]["metrics"]["latency_ms"] - 10
        receipts[3]["metrics"]["compute_cost"] = receipts[2]["metrics"]["compute_cost"] - 1
        report = compare_implementations(receipts)
        self.assertIsNone(report["metrics"]["task_quality"]["ci95"])
        self.assertEqual(report["metrics"]["task_quality"]["interval_status"], "zero_observed_variance")
        self.assertEqual(report["recommendation"], "pareto_tradeoff_or_insufficient_evidence")

    def test_declared_metric_with_all_null_observations_blocks_dominance(self):
        for item in self.receipts:
            item["metric_set"].append("policy_violations")
            item["metrics"]["policy_violations"] = None
        report = compare_implementations(self.receipts)
        self.assertIn("policy_violations", report["unobserved_metrics"])
        self.assertEqual(report["recommendation"], "pareto_tradeoff_or_insufficient_evidence")

    def test_metric_set_must_match_across_receipts(self):
        self.receipts[-1]["metric_set"].append("policy_violations")
        self.receipts[-1]["metrics"]["policy_violations"] = None
        with self.assertRaisesRegex(ValueError, "same declared metric_set"):
            compare_implementations(self.receipts)

    def test_metric_keys_must_match_declared_metric_set(self):
        del self.receipts[0]["metrics"]["compute_cost"]
        with self.assertRaisesRegex(ValueError, "metrics keys must match metric_set"):
            compare_implementations(self.receipts)

    def test_unknown_receipt_schema_is_rejected(self):
        self.receipts[0]["schema"] = "tournament.implementation-receipt.v0"
        with self.assertRaisesRegex(ValueError, "receipt schema"):
            compare_implementations(self.receipts)

    def test_hard_gate_failure_blocks_recommendation(self):
        self.receipts[-1]["hard_gates"]["security_and_policy"] = False
        report = compare_implementations(self.receipts)
        self.assertEqual(report["recommendation"], "blocked_by_hard_gate")
        self.assertFalse(report["promotion_authorized"])

    def test_unmatched_task_sets_are_rejected(self):
        self.receipts.pop()
        with self.assertRaisesRegex(ValueError, "same matched task IDs"):
            compare_implementations(self.receipts)

    def test_environment_mismatch_is_rejected(self):
        self.receipts[-1]["environment_fingerprint"] = "sha256:other"
        with self.assertRaisesRegex(ValueError, "same cohort"):
            compare_implementations(self.receipts)

    def test_duplicate_implementation_task_receipt_is_rejected(self):
        self.receipts.append(self.receipts[0].copy())
        with self.assertRaisesRegex(ValueError, "duplicate receipt"):
            compare_implementations(self.receipts)

    def test_input_order_does_not_change_incumbent_and_challenger_roles(self):
        reversed_receipts = list(reversed(self.receipts))
        report = compare_implementations(reversed_receipts)
        self.assertEqual(report["incumbent"]["implementation_id"], "incumbent")
        self.assertEqual(report["challenger"]["implementation_id"], "challenger")

    def test_single_observation_cannot_establish_dominance(self):
        receipts = self.receipts[:2]
        report = compare_implementations(receipts)
        self.assertEqual(report["recommendation"], "pareto_tradeoff_or_insufficient_evidence")

    def test_duplicate_run_identity_is_rejected(self):
        duplicate = self.receipts[0].copy()
        duplicate["task_id"] = "other-task"
        self.receipts.append(duplicate)
        with self.assertRaisesRegex(ValueError, "duplicate run_id"):
            compare_implementations(self.receipts)

    def test_promotion_always_requires_separate_authorization(self):
        report = compare_implementations(self.receipts)
        self.assertFalse(report["promotion_authorized"])
        self.assertEqual(report["promotion_gate"],
                         ["held_out_validation", "owner_approval", "rollback_target"])


if __name__ == "__main__":
    unittest.main()
