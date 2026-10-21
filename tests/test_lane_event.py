"""Offline tests for scripts/ops/lane_event.py (no network, no database)."""
import importlib.util
import json
import os
import pathlib
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lane_event", ROOT / "scripts/ops/lane_event.py")
le = importlib.util.module_from_spec(spec)
spec.loader.exec_module(le)

BASE = {"lane": "help-wanted", "workflow": "help-wanted scout", "event_type": "run_completed",
        "repo": "o/r", "run_id": 1, "run_attempt": 1}


class LaneEventTests(unittest.TestCase):
    def test_key_is_stable_and_attempt_sensitive(self):
        a = le.normalize(dict(BASE))
        b = le.normalize(dict(BASE))
        c = le.normalize(dict(BASE, run_attempt=2))
        self.assertEqual(a["key"], b["key"])
        self.assertNotEqual(a["key"], c["key"])

    def test_subject_changes_key(self):
        a = le.normalize(dict(BASE, subject_url="https://github.com/x/y/pull/1"))
        b = le.normalize(dict(BASE, subject_url="https://github.com/x/y/pull/2"))
        self.assertNotEqual(a["key"], b["key"])

    def test_requires_subject(self):
        with self.assertRaises(ValueError):
            le.normalize({"lane": "she", "workflow": "w", "event_type": "t", "repo": "o/r"})

    def test_payload_truncated(self):
        ev = le.normalize(dict(BASE, payload={"x": "y" * 20000}))
        self.assertEqual(json.loads(ev["payload"])["truncated"], True)

    def test_noop_without_credentials(self):
        with mock.patch.dict(os.environ, {"LANE_EVENTS_DATABASE_URL": "", "NEON_API_KEY": ""}):
            self.assertEqual(le.main(["record", "--lane", "she", "--workflow", "w", "--repo", "o/r",
                                      "--event-type", "t", "--run-id", "1"]), 0)

    def test_errors_never_fail_caller(self):
        with mock.patch.dict(os.environ, {"LANE_EVENTS_DATABASE_URL": "postgresql://u@127.0.0.1:1/db"}):
            self.assertEqual(le.main(["count"]), 0)


if __name__ == "__main__":
    unittest.main()
