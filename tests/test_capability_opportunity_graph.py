"""Regression tests for the CEEL capability opportunity graph validator."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path
from scripts.integrations.validate_capability_graph import validate_graph

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "docs/integrations/capability-opportunity-graph.json"


class CapabilityOpportunityGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))

    def test_committed_graph_is_valid(self):
        self.assertEqual([], validate_graph(self.graph))

    def test_duplicate_node_id_is_rejected(self):
        graph = copy.deepcopy(self.graph)
        graph["nodes"].append(copy.deepcopy(graph["nodes"][0]))
        self.assertTrue(any("duplicate node IDs" in error for error in validate_graph(graph)))

    def test_unresolved_edge_endpoint_is_rejected(self):
        graph = copy.deepcopy(self.graph)
        graph["edges"].append({"from": "missing-node", "to": "doe-family", "relationship": "informs", "status": "hypothesis"})
        self.assertTrue(any("unknown node" in error for error in validate_graph(graph)))

    def test_unknown_lifecycle_state_is_rejected(self):
        graph = copy.deepcopy(self.graph)
        graph["nodes"][0]["lifecycle_state"] = "production-ready"
        self.assertTrue(any("lifecycle_state is unsupported" in error for error in validate_graph(graph)))

    def test_duplicate_edge_is_rejected(self):
        graph = copy.deepcopy(self.graph)
        graph["edges"].append(copy.deepcopy(graph["edges"][0]))
        self.assertTrue(any("duplicate edge" in error for error in validate_graph(graph)))

    def test_external_candidates_are_not_promoted_without_evidence(self):
        candidates = [n for n in self.graph["nodes"] if n["kind"] == "external_platform"]
        self.assertGreaterEqual(len(candidates), 4)
        for node in candidates:
            self.assertNotIn(node["lifecycle_state"], {"integrated", "monitored"})
            self.assertTrue(all(c["status"] in {"hypothesis", "unknown"} for c in node["capabilities"]))


if __name__ == "__main__":
    unittest.main()
