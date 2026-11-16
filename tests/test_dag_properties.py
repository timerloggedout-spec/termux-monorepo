"""Deterministic property checks for the Kahn reference planner.

NetworkX is an optional independent oracle: core invariants always run on the
stdlib-only Termux path; oracle comparisons run automatically when NetworkX is
available in the environment.
"""
from __future__ import annotations

import random
import unittest

from she.orchestration.dag import TERMINAL_STATES, dependency_state, plan_dag

try:
    import networkx as nx
except ImportError:  # Keep the required Termux test path offline and dependency-free.
    nx = None


class DagPropertyTests(unittest.TestCase):
    def test_seeded_dags_preserve_every_dependency_and_stable_hash(self):
        rng = random.Random(1443)
        for case in range(100):
            count = rng.randrange(0, 24)
            nodes = [f"n{i:02d}" for i in range(count)]
            permutation = nodes[:]
            rng.shuffle(permutation)
            rank = {node: index for index, node in enumerate(permutation)}
            edges = [
                (left, right)
                for left in nodes
                for right in nodes
                if rank[left] < rank[right] and rng.random() < 0.09
            ]
            shuffled_edges = edges[:]
            rng.shuffle(shuffled_edges)

            first = plan_dag(nodes, edges)
            second = plan_dag(reversed(nodes), shuffled_edges)
            self.assertTrue(first.is_acyclic, msg=f"case={case}")
            self.assertEqual(first.topological_order, second.topological_order)
            self.assertEqual(first.graph_sha256, second.graph_sha256)
            self.assertEqual(len(first.topological_order), len(set(nodes)))
            position = {node: index for index, node in enumerate(first.topological_order)}
            for prerequisite, dependent in edges:
                self.assertLess(
                    position[prerequisite],
                    position[dependent],
                    msg=f"case={case}: {prerequisite} !< {dependent}",
                )

    @unittest.skipIf(nx is None, "NetworkX is optional; install it to enable oracle comparisons")
    def test_seeded_dags_match_networkx_lexicographical_oracle(self):
        rng = random.Random(20261022)
        for case in range(50):
            count = rng.randrange(1, 30)
            nodes = [f"n{i:02d}" for i in range(count)]
            shuffled = nodes[:]
            rng.shuffle(shuffled)
            edges = []
            for i, source in enumerate(shuffled):
                for target in shuffled[i + 1 :]:
                    if rng.random() < 0.12:
                        edges.append((source, target))
            graph = nx.DiGraph()
            graph.add_nodes_from(nodes)
            graph.add_edges_from(edges)

            plan = plan_dag(nodes, edges)
            oracle = tuple(nx.lexicographical_topological_sort(graph, key=str))
            self.assertTrue(plan.is_acyclic, msg=f"case={case}")
            self.assertEqual(plan.topological_order, oracle, msg=f"case={case}")

    def test_dependency_admission_state_matrix(self):
        prerequisites = ("a", "b")
        cases = (
            ({"a": "succeeded", "b": "succeeded"}, frozenset({"succeeded"}), "ready"),
            ({"a": "succeeded", "b": "skipped"}, frozenset({"succeeded"}), "blocked"),
            ({"a": "succeeded", "b": "skipped"}, frozenset({"succeeded", "skipped"}), "ready"),
            ({"a": "succeeded", "b": "failed"}, frozenset({"succeeded"}), "blocked"),
            ({"a": "succeeded", "b": "blocked"}, frozenset({"succeeded"}), "blocked"),
            ({"a": "succeeded", "b": "running"}, frozenset({"succeeded"}), "blocked"),
            ({"a": "succeeded"}, frozenset({"succeeded"}), "unknown"),
            ({"a": "succeeded", "b": "unknown"}, frozenset({"succeeded"}), "unknown"),
            ({"a": "unknown", "b": "failed"}, frozenset({"succeeded"}), "blocked"),
        )
        for states, allowed, expected in cases:
            with self.subTest(states=states, allowed=allowed):
                self.assertEqual(
                    dependency_state(
                        "c", prerequisites, states, allowed_success_states=allowed
                    ),
                    expected,
                )

    def test_terminal_state_contract_is_explicit(self):
        self.assertEqual(
            TERMINAL_STATES, frozenset({"succeeded", "skipped", "failed", "blocked"})
        )


if __name__ == "__main__":
    unittest.main()
