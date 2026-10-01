#!/usr/bin/env python3
"""Minimal tests for ops_event_seeklog (stdlib unittest)."""

import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _ROOT / "scripts" / "ops"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import unittest
from ops_event_seeklog import OpsEvent, SeekLog, evidence_envelope_to_ops_event


class TestSeekLog(unittest.TestCase):
    def setUp(self):
        self.events = [
            OpsEvent(ts=100, actor="a", op="A", path="/x", colour="FF0000"),
            OpsEvent(ts=200, actor="b", op="M", path="/y"),
            OpsEvent(ts=300, actor="c", op="D", path="/z", lane="dual-gate", status="passed"),
        ]
        self.log = SeekLog(self.events)

    def test_len_and_percent(self):
        self.assertEqual(len(self.log), 3)
        self.log.seek_to(0.0)
        self.assertAlmostEqual(self.log.percent, 0.0)
        self.log.seek_to(1.0)
        self.assertTrue(self.log.is_finished() or self.log.get_pointer() == 3)

    def test_seek_and_next(self):
        self.log.seek_to(0.5)
        ev = self.log.get_next()
        self.assertIsNotNone(ev)
        self.assertEqual(ev.path, "/y")

    def test_slice(self):
        mid = self.log.slice(1 / 3, 2 / 3)
        self.assertEqual(len(mid), 1)
        self.assertEqual(mid.get_next().path, "/y")

    def test_gource_roundtrip(self):
        text = self.log.to_gource_log()
        rt = SeekLog.from_lines(text.splitlines())
        self.assertEqual(len(rt), 3)
        self.assertEqual(rt._events[0].colour, "FF0000")
        self.assertEqual(rt._events[2].op, "D")

    def test_jsonl_roundtrip(self):
        text = self.log.to_jsonl()
        rt = SeekLog.from_lines(text.splitlines())
        self.assertEqual(len(rt), 3)
        self.assertEqual(rt._events[2].lane, "dual-gate")

    def test_evidence_bridge(self):
        env = {
            "experiment_id": "exp-1",
            "source": "github",
            "source_id": "run-9",
            "commit_sha": "a" * 40,
            "baseline_sha": "b" * 40,
            "observed_at": "2026-09-21T16:00:00Z",
            "status": "passed",
            "outcome": "ok",
            "provenance": {"kind": "github"},
            "confidence": 0.9,
        }
        ev = evidence_envelope_to_ops_event(env)
        self.assertEqual(ev.op, "A")
        self.assertEqual(ev.status, "passed")
        self.assertIn("evidence/github", ev.path)


if __name__ == "__main__":
    unittest.main()
