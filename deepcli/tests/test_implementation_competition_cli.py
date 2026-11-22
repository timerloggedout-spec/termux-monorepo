"""CLI tests for matched tournament implementation comparison."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "tournament" / "compare_implementations.py"


def make_receipt(implementation, role, task, quality, latency, cost):
    return {
        "implementation_id": implementation,
        "implementation_version": "1.0.0",
        "competition_role": role,
        "cohort_id": "cli-cohort",
        "task_id": task,
        "task_contract_hash": "sha256:contract",
        "environment_fingerprint": "sha256:environment",
        "evaluator_version": "eval-1",
        "run_id": f"{implementation}-{task}",
        "outcome": "SUCCEEDED",
        "hard_gates": {
            "task_contract_valid": True,
            "schema_valid": True,
            "security_and_policy": True,
            "provenance_complete": True,
            "deterministic_checks": True,
        },
        "metrics": {
            "task_quality": quality,
            "latency_ms": latency,
            "compute_cost": cost,
        },
    }


class ImplementationCompetitionCliTests(unittest.TestCase):
    def test_cli_writes_and_prints_comparison_report(self):
        receipts = []
        for task, quality, latency in [("a", .7, 100), ("b", .8, 110)]:
            receipts.append(make_receipt("incumbent", "incumbent", task, quality, latency, 10))
            receipts.append(make_receipt("challenger", "challenger", task, quality + .1, latency - 5, 9))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "receipts.json"
            output = root / "comparison.json"
            source.write_text(json.dumps({"receipts": receipts}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--output", str(output)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["schema"], "tournament.implementation-comparison.v1")
            self.assertEqual(report["matched_task_count"], 2)
            self.assertFalse(report["promotion_authorized"])
            self.assertEqual(json.loads(result.stdout)["recommendation"],
                             "challenger_for_human_review")

    def test_cli_returns_structured_error_for_invalid_receipts(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "receipts.json"
            source.write_text('{"receipts": []}', encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("receipts must be a non-empty list", result.stderr)


if __name__ == "__main__":
    unittest.main()
