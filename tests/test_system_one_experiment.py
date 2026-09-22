from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SystemOneExperimentTests(unittest.TestCase):
    def test_control_policy_is_deterministic(self) -> None:
        from scripts.system_one_experiment import deterministic_decision
        state = {"body": "refund invoice payment"}
        self.assertEqual(deterministic_decision(state)["route"], "billing")
        self.assertEqual(deterministic_decision(state), deterministic_decision(state))

    def test_jev_is_unavailable_without_claiming_failure(self) -> None:
        from scripts.system_one_experiment import run_lane
        receipt = run_lane("C", "jev", "M1-fast-gate", {"body": "x"}, "exp", "cohort")
        self.assertEqual(receipt.status, "UNAVAILABLE")
        self.assertEqual(receipt.failure_class, "ENGINE_UNAVAILABLE")

    def test_smoke_emits_normalized_jsonl(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/system_one_experiment.py"),
             "--cohort", "test-cohort"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        rows = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual([row["lane_id"] for row in rows], ["A", "B", "C"])
        self.assertEqual(rows[0]["status"], "OK")
        self.assertIn(rows[2]["status"], {"UNAVAILABLE", "OK"})


if __name__ == "__main__":
    unittest.main()
