import unittest

from she.orchestration.dag import (
    GraphValidationError,
    dependency_state,
    plan_dag,
)


class KahnPlanTests(unittest.TestCase):
    def test_empty_graph(self):
        plan = plan_dag([], [])
        self.assertTrue(plan.is_acyclic)
        self.assertEqual(plan.topological_order, ())
        self.assertEqual(plan.cycle_or_blocked_nodes, ())
        self.assertEqual(plan.ready_frontiers, ())
        self.assertEqual(plan.algorithm_version, "kahn-reference-v2")

    def test_chain_and_fan_in_fan_out(self):
        plan = plan_dag(
            ["a", "b", "c", "d", "e"],
            [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"), ("d", "e")],
        )
        self.assertTrue(plan.is_acyclic)
        order = plan.topological_order
        self.assertLess(order.index("a"), order.index("b"))
        self.assertLess(order.index("a"), order.index("c"))
        self.assertLess(order.index("b"), order.index("d"))
        self.assertLess(order.index("c"), order.index("d"))
        self.assertLess(order.index("d"), order.index("e"))

    def test_disconnected_components_and_deterministic_ties(self):
        first = plan_dag(["z", "b", "a", "y"], [("a", "y"), ("b", "z")])
        second = plan_dag(["y", "a", "z", "b"], [("b", "z"), ("a", "y")])
        self.assertEqual(first.topological_order, second.topological_order)
        self.assertEqual(first.graph_sha256, second.graph_sha256)
        self.assertEqual(first.topological_order, ("a", "b", "y", "z"))

    def test_ready_frontiers_are_concurrent_waves_not_heap_pop_snapshots(self):
        plan = plan_dag(["a", "b", "c", "d"], [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")])
        self.assertEqual(plan.ready_frontiers, (("a",), ("b", "c"), ("d",)))

        disconnected = plan_dag(["z", "b", "a", "y"], [("a", "y"), ("b", "z")])
        self.assertEqual(disconnected.ready_frontiers, (("a", "b"), ("y", "z")))
        self.assertEqual(plan_dag(["a", "b"], []).ready_frontiers, (("a", "b"),))

    def test_duplicate_edges_are_deduplicated(self):
        plan = plan_dag(["a", "b"], [("a", "b"), ("a", "b")])
        self.assertEqual(plan.edge_count, 1)
        self.assertEqual(plan.topological_order, ("a", "b"))

    def test_unknown_endpoint_is_rejected(self):
        with self.assertRaises(GraphValidationError):
            plan_dag(["a"], [("a", "missing")])

    def test_malformed_nodes_are_rejected_before_hashing(self):
        for nodes in ([[]], [None], [""]):
            with self.subTest(nodes=nodes), self.assertRaises(GraphValidationError):
                plan_dag(nodes, [])

    def test_malformed_edge_shapes_and_endpoints_are_rejected(self):
        for edge in ("ab", 7, ["a"], ("a", []), (None, "b"), ("", "b")):
            with self.subTest(edge=edge), self.assertRaises(GraphValidationError):
                plan_dag(["a", "b"], [edge])

    def test_node_and_edge_iterables_preserve_valid_graph_behavior(self):
        plan = plan_dag(iter(["a", "b", "a"]), iter([["a", "b"], ("a", "b")]))
        self.assertEqual(plan.node_count, 2)
        self.assertEqual(plan.edge_count, 1)
        self.assertEqual(plan.topological_order, ("a", "b"))

    def test_cycle_reports_residual_including_downstream_blocked_node(self):
        plan = plan_dag(["a", "b", "c", "free"], [
            ("a", "b"), ("b", "a"), ("b", "c")
        ])
        self.assertFalse(plan.is_acyclic)
        self.assertEqual(plan.cycle_or_blocked_nodes, ("a", "b", "c"))
        self.assertIn("free", plan.topological_order)
        self.assertEqual(plan.ready_frontiers, (("free",),))

    def test_dependency_state_requires_success_by_default(self):
        deps = ["a", "b"]
        self.assertEqual(dependency_state("c", deps, {"a": "succeeded"}), "unknown")
        self.assertEqual(
            dependency_state("c", deps, {"a": "succeeded", "b": "failed"}),
            "blocked",
        )
        self.assertEqual(
            dependency_state("c", deps, {"a": "succeeded", "b": "succeeded"}),
            "ready",
        )
        self.assertEqual(
            dependency_state(
                "c", deps, {"a": "skipped", "b": "succeeded"},
                allowed_success_states=frozenset({"succeeded", "skipped"}),
            ),
            "ready",
        )


if __name__ == "__main__":
    unittest.main()
