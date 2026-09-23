"""Lineage graph tests."""
from __future__ import annotations

import unittest

from ml.pipelines.lineage.graph import from_pairs


class TestLineage(unittest.TestCase):
    def test_roots_and_children(self) -> None:
        graph = from_pairs(
            [
                ("run-1", "run", ""),
                ("recon", "stage", "run-1"),
                ("ingest", "stage", "recon"),
            ]
        )
        self.assertEqual(graph.roots(), ["run-1"])
        self.assertEqual(graph.children_of("recon"), ["ingest"])

    def test_cycle_rejected(self) -> None:
        with self.assertRaises(ValueError):
            from_pairs([("a", "x", "b"), ("b", "x", "a")])


if __name__ == "__main__":
    unittest.main()
