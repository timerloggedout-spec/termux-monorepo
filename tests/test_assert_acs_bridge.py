"""Tests for the ASSERT × ACS blocked factorial evidence bridge."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.doe.assert_acs_bridge import (
    CELL_NAMES,
    assemble_results,
    build_plan,
    load_json,
    record_results,
)


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "experiments/doe/assert_acs_2x2/DESIGN.json"


class AssertAcsBridgeTests(unittest.TestCase):
    def setUp(self):
        self.design = load_json(DESIGN)
        self.plan = build_plan(self.design)

    def test_plan_is_deterministic_and_blocked_by_task(self):
        self.assertEqual(self.plan, build_plan(self.design))
        self.assertEqual(12, self.plan["planned_runs"])
        for task in self.design["tasks"]:
            rows = [row for row in self.plan["rows"] if row["task_id"] == task["task_id"]]
            self.assertEqual(CELL_NAMES, {row["cell"] for row in rows})
            self.assertEqual([1, 2, 3, 4], sorted(row["execution_sequence"] for row in rows))

    def test_assemble_accepts_assert_scores_and_native_score_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            score_args = []
            for cell in sorted(CELL_NAMES):
                evaluator = cell.split("/")[0]
                path = tmp_path / (cell.replace("/", "-") + ".jsonl")
                rows = []
                for task in self.design["tasks"]:
                    if evaluator == "assert":
                        rows.append({
                            "test_case_id": task["task_id"],
                            "judge_status": "ok",
                            "verdict": {"dimensions": {
                                "policy_violation": task["task_id"] == "test_case_000003",
                                "overrefusal": False,
                            }},
                        })
                    else:
                        rows.append({
                            "test_case_id": task["task_id"],
                            "policy_violation": task["task_id"] == "external-deny",
                            "overrefusal": False,
                        })
                path.write_text(
                    "".join(json.dumps(row) + "\n" for row in rows),
                    encoding="utf-8",
                )
                score_args.append(f"{cell}={path}")

            acs_path = tmp_path / "acs.jsonl"
            acs_rows = [
                {"test_case_id": "test_case_000001", "decision": "allow", "reason": None},
                {"test_case_id": "test_case_000002", "decision": "transform", "reason": "tracking_token_redacted"},
                {"test_case_id": "external-deny", "decision": "deny", "reason": "external_recipient_blocked"},
            ]
            acs_path.write_text(
                "".join(json.dumps(row) + "\n" for row in acs_rows),
                encoding="utf-8",
            )
            results = assemble_results(self.plan, score_args, acs_path)

        self.assertEqual(12, len(results))
        external_acs = [
            row for row in results
            if row["task_id"] == "external-deny" and row["governance"] == "acs"
        ]
        self.assertEqual({"deny"}, {row["acs_decision"] for row in external_acs})
        self.assertTrue(all(row["outcome"] == "fail" for row in external_acs))

    def test_record_emits_schema_shaped_records_and_factorial_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "batch-001"
            results = []
            for planned in self.plan["rows"]:
                fail = planned["task_id"] == "external-deny" and planned["governance"] == "native"
                results.append({
                    "run_id": planned["run_id"],
                    "task_id": planned["task_id"],
                    "evaluator": planned["evaluator"],
                    "governance": planned["governance"],
                    "outcome": "fail" if fail else "pass",
                    "policy_violation": fail,
                    "overrefusal": False,
                    "acs_decision": (
                        "deny" if planned["governance"] == "acs" and planned["task_id"] == "external-deny"
                        else "transform" if planned["governance"] == "acs" and planned["task_id"] == "tracking-redact"
                        else "allow" if planned["governance"] == "acs" else None
                    ),
                    "metrics": {"elapsed_ms": 2.5, "token_count": 10},
                    "evidence_refs": ["https://github.com/timerloggedout-spec/termux-monorepo/pull/5908"],
                    "observed_at": "2026-11-27T12:00:00Z",
                })
            summary = record_results(self.design, self.plan, results, output, "test-batch")
            records = list((output / "records").glob("*.json"))
            self.assertEqual(12, len(records))
            sample = json.loads(records[0].read_text(encoding="utf-8"))
            self.assertEqual("1.0", sample["schema_version"])
            self.assertEqual(self.design["baseline_sha"], sample["baseline_sha"])
            self.assertIn(sample["treatment"]["arm"], CELL_NAMES)
            self.assertEqual(12, summary["record_count"])
            self.assertEqual(3, summary["cell_summary"]["assert/acs"]["runs"])
            self.assertEqual(0.0, summary["cell_summary"]["assert/acs"]["policy_violation_rate"])

    def test_record_rejects_incomplete_cohort(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "missing 1 planned observations"):
                record_results(self.design, self.plan, [], Path(tmp) / "out", "test-batch")

    def test_record_rejects_acs_cell_without_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = []
            for planned in self.plan["rows"]:
                results.append({
                    "run_id": planned["run_id"],
                    "task_id": planned["task_id"],
                    "evaluator": planned["evaluator"],
                    "governance": planned["governance"],
                    "outcome": "pass",
                    "policy_violation": False,
                    "overrefusal": False,
                    "acs_decision": None,
                    "observed_at": "2026-11-27T12:00:00Z",
                })
            with self.assertRaisesRegex(ValueError, "ACS arm requires"):
                record_results(self.design, self.plan, results, Path(tmp) / "out", "test-batch")


if __name__ == "__main__":
    unittest.main()
