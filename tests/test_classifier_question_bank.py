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


if __name__ == "__main__":
    unittest.main()
