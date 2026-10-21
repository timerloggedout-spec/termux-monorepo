"""Tests for the offline System One tournament scorer."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "eval_tournament.py"
SPEC = importlib.util.spec_from_file_location("eval_tournament", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class TournamentTests(unittest.TestCase):
    def test_accuracy_pairwise_and_latency_metrics(self):
        rows = [
            {"candidate_id": "fast", "question_id": "q1", "expected": "yes", "prediction": "yes", "latency_ms": 10},
            {"candidate_id": "fast", "question_id": "q2", "expected": "no", "prediction": "yes", "latency_ms": 30},
            {"candidate_id": "careful", "question_id": "q1", "expected": "yes", "prediction": "yes", "latency_ms": 20},
            {"candidate_id": "careful", "question_id": "q2", "expected": "no", "prediction": "no", "latency_ms": 40},
        ]
        report = module.score(rows)
        self.assertEqual(report["candidates"]["fast"]["exact_match_accuracy"], 0.5)
        self.assertEqual(report["candidates"]["careful"]["exact_match_accuracy"], 1.0)
        self.assertEqual(report["pairwise"][0]["left"], "careful")
        self.assertEqual(report["pairwise"][0]["right"], "fast")
        self.assertEqual(report["pairwise"][0]["left_wins"], 1)
        self.assertEqual(report["pairwise"][0]["right_wins"], 0)
        self.assertEqual(report["pairwise"][0]["ties_both_correct"], 1)
        self.assertEqual(report["candidates"]["fast"]["latency_ms"]["p95"], 29.0)

    def test_both_wrong_is_not_silently_dropped_from_pairwise_accounting(self):
        rows = [
            {"candidate_id": "a", "question_id": "q", "expected": 1, "prediction": 0},
            {"candidate_id": "b", "question_id": "q", "expected": 1, "prediction": 2},
        ]
        pair = module.score(rows)["pairwise"][0]
        self.assertEqual(pair["ties_both_incorrect"], 1)
        self.assertEqual(pair["decisive_questions"], 0)
        self.assertEqual(pair["comparable_questions"], 1)

    def test_non_ok_status_is_non_comparable_pairwise(self):
        rows = [
            {"candidate_id": "a", "question_id": "q", "expected": 1, "prediction": 1, "status": "timeout"},
            {"candidate_id": "b", "question_id": "q", "expected": 1, "prediction": 0},
        ]
        pair = module.score(rows)["pairwise"][0]
        self.assertEqual(pair["non_comparable_questions"], 1)
        self.assertEqual(pair["decisive_questions"], 0)

    def test_abstention_and_schema_invalid_are_counted_separately(self):
        report = module.score([
            {"candidate_id": "x", "question_id": "q1", "expected": "safe", "prediction": "ABSTAIN", "schema_valid": False},
            {"candidate_id": "x", "question_id": "q2", "expected": "ok", "prediction": "ok", "status": "timeout"},
        ])
        item = report["candidates"]["x"]
        self.assertEqual(item["abstention_count"], 1)
        self.assertEqual(item["schema_invalid_count"], 1)
        self.assertEqual(item["non_ok_status_count"], 1)
        self.assertEqual(item["scored_count"], 1)
        self.assertEqual(item["exact_match_accuracy"], 0.0)

    def test_duplicate_question_per_candidate_fails_closed(self):
        rows = [
            {"candidate_id": "x", "question_id": "q", "expected": 1, "prediction": 1},
            {"candidate_id": "x", "question_id": "q", "expected": 1, "prediction": 0},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate question_id"):
            module.score(rows)

    def test_jsonl_loader_rejects_missing_required_fields_and_non_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.jsonl"
            path.write_text(json.dumps({"candidate_id": "x"}) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing required keys"):
                module.load_rows(path)
            path.write_text(json.dumps(["not", "an", "object"]) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be an object"):
                module.load_rows(path)

    def test_invalid_latency_is_ignored(self):
        rows = [
            {"candidate_id": "x", "question_id": "q1", "expected": 1, "prediction": 1, "latency_ms": float("inf")},
            {"candidate_id": "x", "question_id": "q2", "expected": 1, "prediction": 1, "latency_ms": -1},
            {"candidate_id": "x", "question_id": "q3", "expected": 1, "prediction": 1, "latency_ms": True},
        ]
        self.assertEqual(module.score(rows)["candidates"]["x"]["latency_ms"]["count"], 0)


if __name__ == "__main__":
    unittest.main()
