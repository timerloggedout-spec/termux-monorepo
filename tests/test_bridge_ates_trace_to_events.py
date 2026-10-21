import json
import tempfile
import unittest
from pathlib import Path

from scripts.ci.bridge_ates_trace_to_events import convert_record


class TraceBridgeTests(unittest.TestCase):
    def test_converts_whitelisted_tool_span_and_adds_run_linkage(self):
        record = {
            "kind": "tool_call", "started_at": "2026-10-20T10:00:00Z",
            "ended_at": "2026-10-20T10:00:01Z", "duration_ms": 1000,
            "status": "ok", "benchmark_case_id": "case-7", "role": "critic",
            "tool": "pytest", "input_fingerprint": "secret-not-copied",
        }
        event = convert_record(record, run_id=123, attempt=2, source_sha="a" * 40)
        self.assertEqual(event["event"], "tool_call")
        self.assertEqual(event["status"], "success")
        self.assertEqual(event["agent_id"], "critic")
        self.assertEqual(event["gha_run_id"], 123)
        self.assertEqual(event["gha_run_attempt"], 2)
        self.assertNotIn("input_fingerprint", event)
        self.assertNotIn("started_at", event)
        self.assertNotIn("ended_at", event)

    def test_ignores_unknown_kind_without_inventing_mapping(self):
        self.assertIsNone(convert_record({"kind": "model_call", "started_at": "x"}))

    def test_rejects_invalid_status_and_missing_tool(self):
        base = {"kind": "tool_call", "started_at": "2026-10-20T10:00:00Z", "benchmark_case_id": "x"}
        with self.assertRaises(ValueError):
            convert_record({**base, "status": "maybe", "tool": "pytest"})
        with self.assertRaises(ValueError):
            convert_record(base)

    def test_rejects_invalid_sha_and_negative_duration(self):
        base = {"kind": "task_completed", "ended_at": "2026-10-20T10:00:00Z", "benchmark_case_id": "x"}
        with self.assertRaises(ValueError):
            convert_record(base, source_sha="bad")
        with self.assertRaises(ValueError):
            convert_record({**base, "duration_ms": -1})

    def test_output_events_are_compatible_with_contract_shape(self):
        event = convert_record({
            "kind": "task_completed", "ended_at": "2026-10-20T10:00:00Z",
            "benchmark_case_id": "case-9", "status": "error", "duration_ms": 2.5,
        })
        allowed = {"timestamp", "event", "agent_id", "task_id", "tool", "status", "duration_ms",
                   "latency_ms", "active_seconds", "inference_seconds", "tokens_in", "tokens_out",
                   "complexity_score", "metrics", "gha_run_id", "gha_run_attempt", "source_sha"}
        self.assertTrue(set(event).issubset(allowed))
        self.assertEqual(event["status"], "error")


if __name__ == "__main__":
    unittest.main()
