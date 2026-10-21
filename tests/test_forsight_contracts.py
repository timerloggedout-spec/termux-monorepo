import json
import unittest
from datetime import datetime

from she.provenance.runtime_manifest import build_manifest
from she.telemetry.otel_projection import project_event


class ForesightContractsTest(unittest.TestCase):
    def test_otel_projection_is_payload_free(self):
        event = {
            "schema_version": 1,
            "event_id": "evt-1",
            "run_id": "run-1",
            "event_type": "tool.execute",
            "occurred_at": "2026-10-02T12:00:00Z",
            "agent_id": "agent-a",
            "task_id": "task-1",
            "protocol": "mcp",
            "status": "EXECUTED",
            "tool_name": "repo.read",
            "attributes": {"duration_ms": 12, "prompt": "must be removed"},
            "prompt": "must never appear",
        }
        projected = project_event(event)
        self.assertEqual(projected["name"], "execute_tool")
        self.assertNotIn("prompt", json.dumps(projected))

    def test_manifest_recursively_removes_sensitive_fields(self):
        manifest = build_manifest(
            run_id="run-1",
            source_sha="abc",
            environment={"os": "linux", "nested": {"token": "secret", "arch": "arm64"}},
            runtime={"name": "runtime", "version": "1"},
            model={"name": "model", "quantization": "Q4"},
            tools=[{"name": "repo.read", "version": "1", "credential": "secret"}],
            result={"accepted": True, "message": "private"},
        )
        self.assertEqual(manifest["environment"], {"os": "linux", "nested": {"arch": "arm64"}})
        self.assertEqual(manifest["tools"], [{"name": "repo.read", "version": "1"}])
        self.assertTrue(manifest["environment_digest"].startswith("sha256:"))
        self.assertTrue(manifest["model_digest"].startswith("sha256:"))
        self.assertIsNotNone(datetime.fromisoformat(
            manifest["generated_at"].replace("Z", "+00:00")
        ))

    def test_edge_matrix_contract_is_machine_readable(self):
        with open("config/edge_inference_matrix.json", encoding="utf-8") as handle:
            matrix = json.load(handle)
        self.assertIn("android", matrix["targets"])
        self.assertIn("energy_mwh", matrix["measurements"])
        self.assertFalse(matrix["procurement_policy"]["vendor_tops_is_measured_evidence"])


if __name__ == "__main__":
    unittest.main()
