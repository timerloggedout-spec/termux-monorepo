import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/telemetry/emit_eps_event.py"

class TestEPSEmitter(unittest.TestCase):
    def run_emitter(self, payload):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
        )
        return proc

    def base(self):
        return {
            "schema_version": "eps.v1",
            "event_type": "pr.ledger_observed",
            "occurred_at": "2026-09-21T00:00:00Z",
            "source": "github.actions.pr-production-ledger",
            "repo": "timerloggedout-spec/termux-monorepo",
            "git_sha": "a" * 40,
            "run_id": 123,
            "run_attempt": 2,
            "entity_type": "pull_request",
            "entity_id": "pr:701",
            "status": "observed",
            "provenance": {"source_ref": "https://github.com/timerloggedout-spec/termux-monorepo/pull/701", "attribution_confidence": 1.0},
            "attributes": {"checks_total": 3, "checks_pending": 1},
        }

    def test_emits_deterministic_id(self):
        a = self.run_emitter(self.base())
        b = self.run_emitter(self.base())
        self.assertEqual(a.returncode, 0)
        self.assertEqual(a.stdout, b.stdout)
        self.assertIn('"event_id":"eps-', a.stdout)

    def test_rejects_sensitive_attributes(self):
        payload = self.base()
        payload["attributes"]["prompt"] = "must not leave telemetry"
        proc = self.run_emitter(payload)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("forbidden", proc.stderr)

    def test_rejects_short_sha(self):
        payload = self.base()
        payload["git_sha"] = "abc"
        proc = self.run_emitter(payload)
        self.assertNotEqual(proc.returncode, 0)

if __name__ == "__main__":
    unittest.main()
