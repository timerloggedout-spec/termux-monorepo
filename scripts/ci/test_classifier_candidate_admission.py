"""Tests for evidence-aware classifier candidate admission."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))
from classifier_candidate_admission import build_report


class CandidateAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / "config/classifier_graph_registry.json").read_text())
        cls.catalog = json.loads((ROOT / "config/system_one_catalog.json").read_text())
        cls.report = build_report(cls.registry, cls.catalog)

    def test_report_covers_all_model_candidates(self):
        self.assertEqual(self.report["candidate_count"], 65)
        self.assertEqual(self.report["catalog_model_count"], 61)
        self.assertEqual(self.report["infrastructure_reference_count"], 27)

    def test_only_incumbents_and_evaluated_laya_are_trial_eligible(self):
        eligible = [row for row in self.report["candidates"]
                    if row["eligible_for_role_matched_trial"]]
        self.assertEqual(len(eligible), 5)
        self.assertEqual(sum(row["disposition"] == "incumbent_baseline" for row in eligible), 4)
        self.assertEqual(sum(row["disposition"] == "replication_candidate" for row in eligible), 1)

    def test_unclassified_candidates_remain_out_of_trial_admission(self):
        pending = [row for row in self.report["candidates"]
                   if row["disposition"] == "awaiting_capability_qualification"]
        self.assertEqual(len(pending), 56)
        self.assertTrue(all(not row["eligible_for_role_matched_trial"] for row in pending))

    def test_paid_and_composition_gates_are_explicit(self):
        by_id = {row["candidate_id"]: row for row in self.report["candidates"]}
        self.assertEqual(by_id["catalog.S1-01"]["disposition"], "requires_owner_paid_approval")
        self.assertEqual(by_id["catalog.S1-02"]["disposition"], "requires_serving_composition")
        self.assertEqual(by_id["catalog.S1-04"]["disposition"], "referenced_without_runnable_release")
        self.assertEqual(by_id["catalog.S1-05"]["disposition"], "host_or_egress_blocked")

    def test_admission_policy_is_role_and_task_scoped(self):
        self.assertEqual(self.report["policy"]["comparison_scope"], "within_role_and_task_contract")
        self.assertFalse(self.report["policy"]["catalog_presence_implies_capability"])
        self.assertFalse(self.report["policy"]["unclassified_candidates_enter_trials"])


if __name__ == "__main__":
    unittest.main()
