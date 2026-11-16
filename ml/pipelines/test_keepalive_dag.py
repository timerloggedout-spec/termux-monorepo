#!/usr/bin/env python3
"""Stdlib tests for the slim keep-alive DAG."""

from __future__ import annotations

import unittest

from ml.pipelines.keepalive_dag import (
    DagEdge,
    DagNode,
    DagSpec,
    default_dag,
    iter_ready_nodes,
    operator_dag,
    render_mermaid,
    validate_dag,
)


class KeepaliveDagTest(unittest.TestCase):
    def test_default_valid(self) -> None:
        spec = default_dag()
        self.assertEqual(validate_dag(spec), [])
        self.assertEqual(spec.mode, "observe")
        self.assertIn("flowchart LR", render_mermaid(spec))

    def test_ready_order(self) -> None:
        spec = default_dag()
        ready = iter_ready_nodes(spec, [])
        self.assertEqual(ready, ["ingest_events"])
        ready = iter_ready_nodes(spec, ["ingest_events"])
        self.assertEqual(ready, ["schema_validate"])

    def test_rejects_bad_kind(self) -> None:
        spec = DagSpec(
            name="bad",
            nodes=(DagNode("a", "remote", "nope"),),
            edges=(),
            mode="observe",
        )
        self.assertTrue(validate_dag(spec))

    def test_rejects_missing_edge_target(self) -> None:
        spec = DagSpec(
            name="bad",
            nodes=(DagNode("a", "ingest", "ok"),),
            edges=(DagEdge("a", "missing"),),
        )
        self.assertTrue(any("missing target" in e for e in validate_dag(spec)))

    def test_operator_extends_default(self) -> None:
        spec = operator_dag()
        self.assertEqual(validate_dag(spec), [])
        self.assertTrue(spec.node_ids() >= default_dag().node_ids())
        ready = iter_ready_nodes(spec, ["ingest_events", "schema_validate", "score_throughput", "write_ledger", "export_status"])
        self.assertEqual(ready, ["recon_lanes"])


if __name__ == "__main__":
    unittest.main()
