"""Offline contract checks for the Pinecone vector-store DoE registration."""
from __future__ import annotations
import json
import unittest
from pathlib import Path

from scripts.doe.pinecone_vector_store_metrics import evaluate_arm, paired_bootstrap_ci
ROOT = Path(__file__).resolve().parents[1]
def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
class PineconeDoEContractTests(unittest.TestCase):
    def test_campaign_is_registered_as_design_only(self):
        design = read_json("experiments/doe/pinecone-vector-store/DESIGN.json")
        feed = read_json("apps/tribute-dashboard/data/doe-feed.json")
        rows = [c for c in feed["data"]["campaigns"] if c["campaign_id"] == "pinecone-vector-store"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["state"], "admitted_design_only")
        self.assertEqual(rows[0]["runs"], 0)
        self.assertIsNone(rows[0]["results"])
        self.assertIn("admitted_design_only", feed["data"]["family"]["shared"]["intake_rule"])
        self.assertEqual(design["status"], "design_only")
        self.assertFalse(design["execution"]["dispatch_authorized"])
        self.assertEqual(design["execution"]["live_runs"], 0)
    def test_three_engine_arms_share_one_vector_matrix(self):
        design = read_json("experiments/doe/pinecone-vector-store/DESIGN.json")
        arms = design["design"]["arms"]
        self.assertEqual({arm["engine"] for arm in arms}, {"pgvector", "pg_pinecone-native", "pg_pinecone-remote"})
        self.assertEqual({arm["vector_source"] for arm in arms}, {"shared-precomputed-vectors"})
        self.assertEqual(design["design"]["baseline_arm"], "pgvector-hnsw")
        self.assertEqual(design["design"]["unit"], "query_task")
        self.assertEqual(design["design"]["sample_size"]["independent_query_tasks"], 30)
    def test_offline_metric_fixture_has_expected_ranking_behavior(self):
        fixture = read_json("tests/fixtures/pinecone-vector-store-metrics.json")
        queries = fixture["queries"]
        control = evaluate_arm(queries, fixture["rankings"]["pgvector-hnsw"])
        native = evaluate_arm(queries, fixture["rankings"]["pg-pinecone-native"])
        remote = evaluate_arm(queries, fixture["rankings"]["pg-pinecone-remote"])
        expected = fixture["expected_macro_recall_at_5"]
        self.assertAlmostEqual(control["mean_recall_at_5"], expected["pgvector-hnsw"])
        self.assertAlmostEqual(native["mean_recall_at_5"], expected["pg-pinecone-native"])
        self.assertAlmostEqual(remote["mean_recall_at_5"], expected["pg-pinecone-remote"])
        effect = paired_bootstrap_ci(
            control["per_query_recall_at_5"],
            native["per_query_recall_at_5"],
            seed=17,
            resamples=1000,
        )
        self.assertAlmostEqual(effect["mean_difference"], 0.5)
        self.assertLessEqual(effect["ci_lower"], effect["mean_difference"])
        self.assertGreaterEqual(effect["ci_upper"], effect["mean_difference"])

    def test_integrated_inference_remains_a_separate_system_path(self):
        design = read_json("experiments/doe/pinecone-vector-store/DESIGN.json")
        incumbent = design["design"]["separate_system_path"]
        self.assertEqual(incumbent["index"], "termux-knowledge")
        self.assertEqual(incumbent["namespace"], "repo-docs")
        self.assertFalse(incumbent["included_in_primary_storage_engine_estimate"])
    def test_reference_registry_and_capability_graph_are_wired(self):
        registry = read_json("docs/integrations/registry.json")
        names = {item["name"] for item in registry["integrations"]}
        self.assertTrue({"Pinecone", "pg_pinecone", "pgvector"} <= names)
        graph = read_json("docs/integrations/capability-opportunity-graph.json")
        node_ids = {node["id"] for node in graph["nodes"]}
        self.assertTrue({"pinecone", "pg-pinecone", "pgvector", "doe-family"} <= node_ids)
        index = (ROOT / "refTemplates/00_Index/README.md").read_text(encoding="utf-8")
        self.assertIn("18_Vector_Databases/", index)
        metadata = read_json("refTemplates/18_Vector_Databases/pinecone/metadata.json")
        self.assertEqual(metadata["smod"]["state"], "candidate_pending_custom_fork")
        self.assertFalse(metadata["smod"]["gitlink_present"])
if __name__ == "__main__":
    unittest.main()
