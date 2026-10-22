import json
import tempfile
import unittest
from pathlib import Path

from she.observability.orchestrator_trace import JsonlTraceSink, OrchestratorTracer


class OrchestratorTraceTests(unittest.TestCase):
    def test_trace_is_hierarchical(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.jsonl"
            tracer = OrchestratorTracer(JsonlTraceSink(path), benchmark_case_id="case-1")
            with tracer.span("orchestrator", role="orchestrator", deterministic=True, input_value={"value": 1}):
                with tracer.span("actor", role="actor", input_value={"value": 2}):
                    pass
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["kind"], "actor")
            self.assertEqual(rows[1]["kind"], "orchestrator")
            self.assertEqual(rows[0]["parent_span_id"], rows[1]["span_id"])
            self.assertEqual(rows[0]["trace_id"], rows[1]["trace_id"])
            self.assertIn("ended_at", rows[0])

    def test_isolated_spawn_breaks_parent_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.jsonl"
            tracer = OrchestratorTracer(JsonlTraceSink(path), benchmark_case_id="case-2")
            with tracer.span("orchestrator"):
                child = tracer.spawn(isolated=True)
                with child.span("spawn", spawn_mode="SPAWN", inherit_parent_context=False):
                    pass
            row = json.loads(path.read_text().splitlines()[0])
            self.assertEqual(row["spawn_mode"], "SPAWN")
            self.assertFalse(row["inherit_parent_context"])
            self.assertNotEqual(row["trace_id"], tracer.trace_id)


if __name__ == "__main__":
    unittest.main()
