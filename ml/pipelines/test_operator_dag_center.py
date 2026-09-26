import unittest
from ml.pipelines.keepalive_dag import default_dag, iter_ready_nodes, operator_dag, validate_dag

class OperatorDagCenterTest(unittest.TestCase):
    def test_command_center_tail(self) -> None:
        spec = operator_dag()
        self.assertEqual(validate_dag(spec), [])
        self.assertIn("command_center", spec.node_ids())
        done = [
            "ingest_events", "schema_validate", "score_throughput", "write_ledger",
            "export_status", "recon_lanes", "evaluate_gates", "bind_sha", "monitor_cctv",
        ]
        self.assertEqual(iter_ready_nodes(spec, done), ["command_center"])
        self.assertTrue(spec.node_ids() >= default_dag().node_ids())
