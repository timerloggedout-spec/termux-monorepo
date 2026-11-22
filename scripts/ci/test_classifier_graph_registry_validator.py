"""Offline regression tests for the classifier graph registry validator."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))
from classifier_graph_registry_validator import validate_registry


class ClassifierGraphRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(
            (ROOT / "config/classifier_graph_registry.json").read_text(encoding="utf-8")
        )
        cls.catalog = json.loads(
            (ROOT / "config/system_one_catalog.json").read_text(encoding="utf-8")
        )
        cls.estate = json.loads(
            (ROOT / "ops/classifiers/classifiers-feed.json").read_text(encoding="utf-8")
        )
        cls.plan = json.loads(
            (ROOT / "config/classifier_tournament_experiment_plan.json").read_text(encoding="utf-8")
        )

    def validate(self, registry):
        return validate_registry(ROOT, registry, self.catalog, self.estate, self.plan)

    def test_checked_in_registry_is_valid(self):
        self.assertEqual(self.validate(copy.deepcopy(self.registry)), [])

    def test_classifier_estate_snapshot_matches_71_unit_feed(self):
        registry = copy.deepcopy(self.registry)
        self.assertEqual(registry["classifier_estate"]["unit_count"], 71)
        self.assertEqual(len(self.estate["units"]), 71)
        self.assertEqual(registry["classifier_estate"]["states"],
                         {"live": 43, "dormant": 26, "dead": 2})

    def test_classifier_estate_count_drift_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["classifier_estate"]["unit_count"] = 72
        self.assertTrue(any("unit_count: snapshot count mismatch" in error
                            for error in self.validate(registry)))

    def test_all_model_catalog_entries_are_registered_as_candidates(self):
        model_ids = {entry["id"] for entry in self.catalog["entries"]
                     if entry["layer"] == "model"}
        registered = {item["catalog_entry_id"] for item in self.registry["candidates"]
                      if item["kind"] == "catalog"}
        self.assertEqual(len(model_ids), 61)
        self.assertEqual(registered, model_ids)

    def test_non_model_catalog_entries_remain_infrastructure(self):
        expected = {entry["id"] for entry in self.catalog["entries"]
                    if entry["layer"] != "model"}
        registered = {item["catalog_entry_id"] for item in self.registry["infrastructure"]}
        self.assertEqual(len(expected), 27)
        self.assertEqual(registered, expected)

    def test_unclassified_models_remain_out_of_role_claims(self):
        unclassified = [item for item in self.registry["candidates"]
                        if item["qualification_state"] == "unclassified"]
        self.assertGreaterEqual(len(unclassified), 1)
        self.assertTrue(all(item["roles"] == ["unclassified"] for item in unclassified))

    def test_implementation_competition_has_matched_cohort_gates(self):
        competition = self.registry["implementation_competition"]
        self.assertEqual(competition["canonical_cohort"], "manager.tournament.v1")
        self.assertTrue(competition["protocol"]["matched_cohort_required"])
        self.assertTrue(competition["protocol"]["held_out_required"])
        self.assertTrue(competition["protocol"]["independent_evaluator_required"])
        self.assertFalse(competition["challengers"][0]["execution_ready"])

    def test_model_screen_covers_all_61_catalog_models(self):
        graph = next(item for item in self.registry["graphs"]
                     if item["graph_id"] == "model-catalog-screen")
        candidate_ids = {node["candidate_id"] for node in graph["nodes"]}
        model_candidate_ids = {item["candidate_id"] for item in self.registry["candidates"]
                               if item["kind"] == "catalog"}
        self.assertEqual(len(graph["nodes"]), 61)
        self.assertEqual(candidate_ids, model_candidate_ids)
        self.assertEqual(graph["status"], "design_only")

    def test_full_model_inventory_and_infrastructure_coverage(self):
        model_ids = {entry["id"] for entry in self.catalog["entries"]
                     if entry["layer"] == "model"}
        infrastructure_ids = {entry["id"] for entry in self.catalog["entries"]
                               if entry["layer"] != "model"}
        registered_models = {item["catalog_entry_id"] for item in self.registry["candidates"]
                             if item["kind"] == "catalog"}
        registered_infrastructure = {item["catalog_entry_id"]
                                      for item in self.registry["infrastructure"]}
        self.assertEqual(len(model_ids), 61)
        self.assertEqual(len(infrastructure_ids), 27)
        self.assertEqual(registered_models, model_ids)
        self.assertEqual(registered_infrastructure, infrastructure_ids)

    def test_classifier_estate_groups_reconcile_to_all_71_units(self):
        groups = self.registry["classifier_estate"]["groups"]
        self.assertEqual(len(groups), 12)
        self.assertEqual(sum(group["units"] for group in groups), 71)
        self.assertEqual(sum(group["live"] for group in groups), 43)
        self.assertEqual(sum(group["dormant"] for group in groups), 26)
        self.assertEqual(sum(group["dead"] for group in groups), 2)

    def test_model_candidate_claims_match_catalog_provenance(self):
        entries = {item["id"]: item for item in self.catalog["entries"]}
        for candidate in self.registry["candidates"]:
            if candidate["kind"] != "catalog":
                continue
            source = entries[candidate["catalog_entry_id"]]
            self.assertEqual(candidate["catalog_claim"], source["note"])
            self.assertEqual(candidate["catalog_source_url"], source["source_url"])

    def test_duplicate_classifier_estate_groups_are_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["classifier_estate"]["groups"].append(
            copy.deepcopy(registry["classifier_estate"]["groups"][0])
        )
        errors = validate_registry(ROOT, registry, self.catalog, self.estate, self.plan)
        self.assertTrue(any("unique group names" in error for error in errors))

    def test_unclassified_candidates_make_no_role_claim(self):
        candidates = [item for item in self.registry["candidates"]
                      if item["qualification_state"] == "unclassified"]
        self.assertEqual(len(candidates), 56)
        self.assertTrue(all(item["roles"] == ["unclassified"] for item in candidates))

    def test_model_catalog_screen_is_complete_and_design_only(self):
        graph = next(item for item in self.registry["graphs"]
                     if item["graph_id"] == "model-catalog-screen")
        self.assertEqual(graph["status"], "design_only")
        self.assertEqual(len(graph["nodes"]), 61)
        self.assertEqual({node["candidate_id"] for node in graph["nodes"]},
                         {item["candidate_id"] for item in self.registry["candidates"]
                          if item["kind"] == "catalog"})

    def test_matched_cohort_comparator_is_versioned_and_present(self):
        comparator = self.registry["implementation_competition"]["comparison_engine"]
        self.assertEqual(comparator["implementation_id"], "matched-cohort-comparator")
        self.assertEqual(comparator["version"], "0.1.0")
        self.assertTrue((ROOT / comparator["source_ref"]).is_file())

    def test_tournament_implementation_competition_is_gated(self):
        competition = self.registry["implementation_competition"]
        self.assertEqual(competition["schema"], "tournament.implementation-competition.v1")
        self.assertEqual(competition["canonical_cohort"], "manager.tournament.v1")
        self.assertEqual(competition["incumbent"]["status"], "incumbent")
        self.assertFalse(competition["challengers"][0]["execution_ready"])
        self.assertTrue(competition["protocol"]["matched_cohort_required"])
        self.assertTrue(competition["protocol"]["held_out_required"])
        self.assertTrue(competition["protocol"]["independent_evaluator_required"])
        self.assertTrue(competition["protocol"]["rollback_target_required"])

    def test_experiment_plan_preserves_four_competition_units(self):
        self.assertEqual(set(self.plan["comparison_units"]), {
            "classifier_capability", "routing_policy",
            "composition_graph", "tournament_implementation"
        })
        self.assertEqual(len(self.plan["phases"]), 5)
        self.assertFalse(self.plan["execution_ready"])
        self.assertEqual(self.plan["status"], "design_only")

    def test_experiment_plan_requires_nulls_and_raw_objectives(self):
        plan = copy.deepcopy(self.plan)
        plan["analysis"]["missing_observation"] = "zero"
        self.assertTrue(any("preserve null observations" in error
                            for error in validate_registry(ROOT, self.registry,
                                self.catalog, self.estate, plan)))

    def test_local_jev_is_dispatch_only_and_external_jev_is_paid_gated(self):
        registry = copy.deepcopy(self.registry)
        candidates = {item["candidate_id"]: item for item in registry["candidates"]}
        self.assertEqual(candidates["local.deepcli.jev"]["operational_state"],
                         "dispatch_only_baseline")
        self.assertEqual(candidates["catalog.S1-01"]["operational_state"],
                         "blocked_paid_owner_gate")

    def test_missing_operational_state_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["candidates"][0].pop("operational_state")
        self.assertTrue(any("operational_state" in error for error in self.validate(registry)))

    def test_unknown_catalog_reference_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        candidate = next(item for item in registry["candidates"] if item["kind"] == "catalog")
        candidate["catalog_entry_id"] = "S1-DOES-NOT-EXIST"
        self.assertTrue(any("unknown catalog entry" in error for error in self.validate(registry)))

    def test_candidate_role_mismatch_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        node = registry["graphs"][0]["nodes"][0]
        node["role_id"] = "typed_decision"
        self.assertTrue(any("does not implement role" in error for error in self.validate(registry)))

    def test_dependency_cycle_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        nodes = registry["graphs"][0]["nodes"]
        nodes[0]["depends_on"] = ["reducer"]
        self.assertTrue(any("dependency cycle" in error for error in self.validate(registry)))

    def test_duplicate_node_identity_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        nodes = registry["graphs"][0]["nodes"]
        nodes[1]["node_id"] = nodes[0]["node_id"]
        self.assertTrue(any("duplicate node ID" in error for error in self.validate(registry)))


if __name__ == "__main__":
    unittest.main()
