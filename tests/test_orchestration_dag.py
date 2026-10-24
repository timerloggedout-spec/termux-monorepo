import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "orchestration"))

from dag import DAGInputError, analyze_dag, evaluate_readiness  # noqa: E402

SHA = "a" * 40


class AnalyzeDAGTests(unittest.TestCase):
    def analyze(self, nodes, edges):
        return analyze_dag(nodes, edges, source_sha=SHA, run_id="test-run-1")

    def test_empty_graph_is_valid_and_has_explicit_empty_coverage(self):
        receipt = self.analyze([], [])
        self.assertEqual(receipt["validation"], "PASS")
        self.assertEqual(receipt["order"], [])
        self.assertEqual(receipt["node_count"], 0)
        self.assertEqual(receipt["edge_count"], 0)
        self.assertIsNone(receipt["coverage"])

    def test_chain_and_fan_in_fan_out_preserve_prerequisite_order(self):
        nodes = ["a", "b", "c", "d", "e", "f"]
        edges = [("a", "c"), ("b", "c"), ("c", "d"), ("c", "e"), ("d", "f"), ("e", "f")]
        receipt = self.analyze(nodes, edges)
        self.assertEqual(receipt["validation"], "PASS")
        positions = {node: index for index, node in enumerate(receipt["order"])}
        for prerequisite, dependent in edges:
            self.assertLess(positions[prerequisite], positions[dependent])

    def test_disconnected_components_are_valid_and_not_connected_implicitly(self):
        receipt = self.analyze(["b", "a", "x", "y"], [("a", "b"), ("x", "y")])
        self.assertEqual(receipt["validation"], "PASS")
        self.assertEqual(receipt["order"], ["a", "b", "x", "y"])
        self.assertEqual(receipt["edge_count"], 2)

    def test_duplicate_edges_are_deduplicated(self):
        receipt = self.analyze(["a", "b"], [("a", "b"), ("a", "b"), ("a", "b")])
        self.assertEqual(receipt["edge_count"], 1)
        self.assertEqual(receipt["order"], ["a", "b"])

    def test_unknown_endpoint_is_rejected(self):
        with self.assertRaisesRegex(DAGInputError, "unknown edge endpoint"):
            self.analyze(["a"], [("a", "missing")])

    def test_malformed_edge_is_rejected_without_type_error(self):
        for edges in ([("a",)], [42], ["ab"], [("a", None)]):
            with self.subTest(edges=edges):
                with self.assertRaises(DAGInputError):
                    self.analyze(["a", "b"], edges)

    def test_duplicate_node_ids_are_rejected(self):
        with self.assertRaisesRegex(DAGInputError, "duplicate node ID"):
            self.analyze(["a", "a"], [])

    def test_deterministic_tie_breaking_and_hash_ignore_input_order_and_duplicate_edges(self):
        first = self.analyze(["z", "b", "a"], [("a", "z"), ("a", "b")])
        second = self.analyze(["a", "b", "z"], [("a", "b"), ("a", "z"), ("a", "z")])
        self.assertEqual(first["order"], ["a", "b", "z"])
        self.assertEqual(first["order"], second["order"])
        self.assertEqual(first["graph_sha256"], second["graph_sha256"])
        self.assertEqual(first["frontier_transitions"], second["frontier_transitions"])

    def test_cycle_reports_cyclic_nodes_separately_from_downstream_blocked_nodes(self):
        receipt = self.analyze(["a", "b", "c", "d", "free"], [
            ("a", "b"), ("b", "a"), ("b", "c"), ("c", "d")
        ])
        self.assertEqual(receipt["validation"], "CYCLE")
        self.assertEqual(receipt["cyclic_nodes"], ["a", "b"])
        self.assertEqual(receipt["cycle_count"], 1)
        self.assertEqual(receipt["blocked_nodes"], ["c", "d"])
        self.assertEqual(receipt["unresolved_nodes"], ["a", "b", "c", "d"])
        self.assertEqual(receipt["order"], ["free"])
        self.assertEqual(receipt["coverage"], 0.2)

    def test_self_loop_is_reported_as_cycle(self):
        receipt = self.analyze(["a"], [("a", "a")])
        self.assertEqual(receipt["cyclic_nodes"], ["a"])
        self.assertEqual(receipt["validation"], "CYCLE")

    def test_provenance_receipt_contains_graph_hash_and_run_identity(self):
        receipt = self.analyze(["a"], [])
        self.assertEqual(receipt["source_sha"], SHA)
        self.assertEqual(receipt["run_id"], "test-run-1")
        self.assertEqual(len(receipt["graph_sha256"]), 64)
        self.assertEqual(receipt["algorithm"], "kahn-deterministic/v1")
        self.assertTrue(receipt["provenance_complete"])

    def test_source_sha_and_run_id_are_required(self):
        with self.assertRaises(DAGInputError):
            analyze_dag(["a"], [], source_sha="bad", run_id="r")
        with self.assertRaises(DAGInputError):
            analyze_dag(["a"], [], source_sha=SHA, run_id=" ")


class ReadinessTests(unittest.TestCase):
    def test_independent_node_ready_but_dependent_waits_for_all_prerequisites(self):
        states = evaluate_readiness(
            ["a", "b", "merge", "independent"],
            [("a", "merge"), ("b", "merge")],
            {"a": "SUCCEEDED", "b": "RUNNING"},
        )
        self.assertEqual(states, {
            "a": "SUCCEEDED", "b": "RUNNING", "merge": "WAITING", "independent": "READY"
        })

    def test_dependent_becomes_ready_only_when_every_prerequisite_succeeds(self):
        states = evaluate_readiness(
            ["a", "b", "merge"],
            [("a", "merge"), ("b", "merge")],
            {"a": "SUCCEEDED", "b": "SUCCEEDED"},
        )
        self.assertEqual(states["merge"], "READY")

    def test_failed_or_skipped_prerequisite_blocks_dependent(self):
        for failed_state in ("FAILED", "SKIPPED", "BLOCKED"):
            with self.subTest(failed_state=failed_state):
                states = evaluate_readiness(
                    ["a", "b"], [("a", "b")], {"a": failed_state}
                )
                self.assertEqual(states["b"], "BLOCKED")

    def test_unknown_prerequisite_never_counts_as_success(self):
        states = evaluate_readiness(["a", "b"], [("a", "b")], {"a": "UNKNOWN"})
        self.assertEqual(states["b"], "WAITING")

    def test_unknown_node_or_invalid_state_is_rejected(self):
        with self.assertRaisesRegex(DAGInputError, "unknown node"):
            evaluate_readiness(["a"], [], {"ghost": "SUCCEEDED"})
        with self.assertRaisesRegex(DAGInputError, "invalid state"):
            evaluate_readiness(["a"], [], {"a": "DONE"})


    def test_cycle_count_counts_components_not_vertices(self):
        receipt = self.analyze(["a", "b", "c", "d"], [
            ("a", "b"), ("b", "a"), ("c", "d"), ("d", "c")
        ])
        self.assertEqual(receipt["cycle_count"], 2)
        self.assertEqual(receipt["cyclic_nodes"], ["a", "b", "c", "d"])


if __name__ == "__main__":
    unittest.main()
