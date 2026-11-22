"""Regression tests for matched tournament implementation comparison."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "deepcli"))
from deepcli.observatory.implementation_competition import compare_implementations


def receipt(implementation, version, task, quality, latency, *, accepted=True):
    return {
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
        "metrics": {
            "task_quality": quality,
            "latency_ms": latency,
            "compute_cost": None,
        },
    }


class ImplementationCompetitionTests(unittest.TestCase):
    def setUp(self):
        self.receipts = []
        for task, quality, latency in [("a", .7, 120), ("b", .8, 100), ("c", .6, 140)]:
            self.receipts.append(receipt("incumbent", "1.0.0", task, quality, latency))
            self.receipts.append(receipt("challenger", "1.1.0", task, quality + .1, latency - 10))

    def test_matched_comparison_reports_paired_effects_and_uncertainty(self):
        report = compare_implementations(self.receipts)
        self.assertEqual(report["matched_task_count"], 3)
        self.assertEqual(report["metrics"]["task_quality"]["sample_count"], 3)
        self.assertAlmostEqual(report["metrics"]["task_quality"]["improvement_mean"], .1)
        self.assertIsNotNone(report["metrics"]["task_quality"]["ci95"])
        self.assertEqual(report["recommendation"], "challenger_for_human_review")

    def test_missing_metrics_remain_null_and_reduce_sample_count(self):
        self.receipts[0]["metrics"]["task_quality"] = None
        report = compare_implementations(self.receipts)
        self.assertEqual(report["metrics"]["task_quality"]["sample_count"], 2)
        self.assertEqual(report["metrics"]["compute_cost"]["sample_count"], 0)
        self.assertIsNone(report["metrics"]["compute_cost"]["improvement_mean"])

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
        duplicate["implementation_role"] = "incumbent"
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
