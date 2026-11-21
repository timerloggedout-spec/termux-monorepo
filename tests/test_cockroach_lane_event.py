"""Offline contract tests for the CockroachDB lane-event projection."""
import importlib.util
import os
import pathlib
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "cockroach_lane_event", ROOT / "scripts/ops/cockroach_lane_event.py"
)
cr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cr)


class CockroachLaneEventTests(unittest.TestCase):
    def test_requires_verified_tls_by_default(self):
        with mock.patch.dict(os.environ, {"CI": "", "COCKROACH_ALLOW_INSECURE_TEST": ""}):
            with self.assertRaisesRegex(ValueError, "sslmode"):
                cr.connection_parts("postgresql://user:secret@db.example:26257/app?sslmode=require")

    def test_verified_tls_uri_moves_password_out_of_process_argument(self):
        uri, env = cr.connection_parts(
            "postgresql://user:p%40ss@db.example:26257/app?sslmode=verify-full"
        )
        self.assertNotIn("p%40ss", uri)
        self.assertEqual(env["PGPASSWORD"], "p@ss")
        self.assertIn("sslmode=verify-full", uri)

    def test_insecure_mode_requires_explicit_ci_test_switch(self):
        with mock.patch.dict(os.environ, {"CI": "true", "COCKROACH_ALLOW_INSECURE_TEST": "1"}):
            uri, _ = cr.connection_parts("postgresql://root@127.0.0.1:26257/defaultdb?sslmode=disable")
            self.assertIn("sslmode=disable", uri)

    def test_missing_sink_is_an_explicit_skip(self):
        with mock.patch.dict(os.environ, {"COCKROACH_DATABASE_URL": ""}):
            self.assertEqual(cr.main(["record", "--strict"]), 1)
            self.assertEqual(cr.main(["record"]), 0)

    def test_event_identity_reuses_canonical_normalizer(self):
        from pathlib import Path
        import sys
        sys.path.insert(0, str(ROOT / "scripts/ops"))
        from lane_event import normalize
        event = normalize({
            "lane": "she", "workflow": "quality", "event_type": "run_completed",
            "repo": "timerloggedout-spec/termux-monorepo", "run_id": 42, "run_attempt": 1,
        })
        self.assertEqual(len(event["key"]), 64)


if __name__ == "__main__":
    unittest.main()
