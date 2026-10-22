from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "tests/fixtures/classifier-question-bank.json"
RUNNER = ROOT / "scripts/classifier_eval.py"


class ClassifierQuestionBankTests(unittest.TestCase):
    def test_bank_ids_are_unique_and_splits_are_declared(self) -> None:
        bank = json.loads(BANK.read_text(encoding="utf-8"))
        ids = [item["question_id"] for item in bank["questions"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item.get("split") for item in bank["questions"]))
        self.assertIn("ood-language", {item["split"] for item in bank["questions"]})

    def test_span_offsets_match_source_text(self) -> None:
        bank = json.loads(BANK.read_text(encoding="utf-8"))
        item = next(q for q in bank["questions"] if q["task"] == "span_extraction")
        for span in item["expected_spans"]:
            self.assertEqual(item["input"][span["start"]:span["end"]], span["text"])

    def test_parallel_smoke_run_is_ordered_and_emits_receipts(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(RUNNER), "--workers", "4", "--run-id", "unit-test-run"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        rows = [json.loads(line) for line in completed.stdout.splitlines()]
        bank = json.loads(BANK.read_text(encoding="utf-8"))
        self.assertEqual([row["question_id"] for row in rows],
                         [q["question_id"] for q in bank["questions"]])
        self.assertTrue(all(row["schema_version"] == "classifier-eval.v1" for row in rows))
        self.assertTrue(all(row["run_id"] == "unit-test-run" for row in rows))
        self.assertTrue(all(row["status"] == "OK" for row in rows))
        self.assertTrue(all(row["correct"] is True for row in rows))

    def test_candidate_matrix_is_parallel_bounded_and_deterministically_ordered(self) -> None:
        completed = subprocess.run(
            [
                sys.executable, str(RUNNER), "--workers", "6",
                "--per-candidate-workers", "2", "--run-id", "matrix-test",
                "--candidates", "deterministic-baseline", "laya-mock", "jev",
            ],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        rows = [json.loads(line) for line in completed.stdout.splitlines()]
        bank = json.loads(BANK.read_text(encoding="utf-8"))
        expected_order = [
            (question["question_id"], candidate)
            for question in bank["questions"]
            for candidate in ("deterministic-baseline", "laya-mock", "jev")
        ]
        self.assertEqual([(row["question_id"], row["candidate_id"]) for row in rows], expected_order)
        self.assertTrue(all(row["run_id"] == "matrix-test" for row in rows))
        self.assertTrue(all(row["schema_version"] == "classifier-eval.v1" for row in rows))
        self.assertTrue(all(row["correct"] is True for row in rows if row["candidate_id"] == "deterministic-baseline"))
        self.assertTrue(all(row["status"] == "MOCK" for row in rows if row["candidate_id"] == "laya-mock" and row["task"] in {"text_classification", "typed_choice"}))
        self.assertTrue(all(row["status"] == "UNAVAILABLE" for row in rows if row["candidate_id"] == "jev" and row["task"] in {"text_classification", "typed_choice"}))
        self.assertTrue(all(row["status"] == "NOT_APPLICABLE" for row in rows if row["task"] in {"multilabel_classification", "span_extraction"} and row["candidate_id"] != "deterministic-baseline"))
        self.assertTrue(all(row["correct"] is None for row in rows if row["candidate_id"] != "deterministic-baseline"))

    def test_live_adapters_are_opt_in(self) -> None:
        completed = subprocess.run(
            [
                sys.executable, str(RUNNER), "--run-id", "no-live-test",
                "--candidates", "jev",
            ],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        rows = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertTrue(all(row["status"] in {"UNAVAILABLE", "NOT_APPLICABLE"} for row in rows))
        self.assertTrue(all(row["correct"] is None for row in rows))


if __name__ == "__main__":
    unittest.main()
