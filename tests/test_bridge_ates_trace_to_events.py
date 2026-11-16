import hashlib
import json
import subprocess
import sys
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
        self.assertEqual(event["agent_id"], "ates-role:" + hashlib.sha256(b"role\0critic").hexdigest())
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


    def test_free_text_labels_are_domain_separated_fingerprints(self):
        sensitive = "private prompt https://example.test/?token=example-secret\ncompletion"
        record = {
            "kind": "tool_call", "started_at": "2026-10-20T10:00:00Z",
            "benchmark_case_id": sensitive, "role": sensitive, "tool": sensitive,
        }
        event = convert_record(record)
        self.assertEqual(event, convert_record(record))
        self.assertNotIn("private prompt", json.dumps(event))
        self.assertNotIn("example-secret", json.dumps(event))
        self.assertEqual(len({event["task_id"], event["agent_id"], event["tool"]}), 3)
        changed = convert_record({**record, "tool": "different"})
        self.assertNotEqual(event["tool"], changed["tool"])
        self.assertEqual(event["task_id"], changed["task_id"])

    def test_timestamp_is_normalized_and_invalid_text_is_not_echoed(self):
        base = {"kind": "task_started", "benchmark_case_id": "case-7"}
        event = convert_record({**base, "started_at": "2026-10-20T12:00:00+02:00"})
        self.assertEqual(event["timestamp"], "2026-10-20T10:00:00Z")
        for timestamp in ("secret-prompt", "2026-10-20T10:00:00", "2026-10-20"):
            with self.subTest(timestamp=timestamp), self.assertRaises(ValueError) as ctx:
                convert_record({**base, "started_at": timestamp})
            self.assertNotIn(timestamp, str(ctx.exception))

    def test_nonfinite_duration_is_rejected(self):
        base = {"kind": "task_completed", "ended_at": "2026-10-20T10:00:00Z", "benchmark_case_id": "case-7"}
        for duration in (float("nan"), float("inf"), float("-inf"), True):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                convert_record({**base, "duration_ms": duration})

    def test_cli_exports_no_raw_labels_and_invalid_input_does_not_overwrite(self):
        script = Path(__file__).resolve().parents[1] / "scripts/ci/bridge_ates_trace_to_events.py"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "trace.jsonl"
            output = Path(directory) / "events.jsonl"
            record = {
                "kind": "tool_call", "started_at": "2026-10-20T10:00:00Z",
                "benchmark_case_id": "sensitive-case", "role": "sensitive-role", "tool": "sensitive-tool",
            }
            source.write_text(json.dumps(record) + "\n", encoding="utf-8")
            result = subprocess.run([sys.executable, str(script), str(source), "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            original = output.read_text(encoding="utf-8")
            self.assertNotIn("sensitive-", original + result.stdout + result.stderr)
            source.write_text(json.dumps({**record, "started_at": "sensitive-timestamp"}) + "\n", encoding="utf-8")
            result = subprocess.run([sys.executable, str(script), str(source), "--output", str(output)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("sensitive-timestamp", result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
