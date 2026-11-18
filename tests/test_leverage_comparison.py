"""Tests for read-only comparison of canonical DoE experiment records."""
import unittest

from scripts.leverage.compare_experiment_records import ComparisonError, compare_records


CONTROL_KEY = "a" * 64
TREATMENT_KEY = "b" * 64
BASELINE = "1" * 40
CANDIDATE = "2" * 40


def record(arm, instance_key, repetition, outcome, cost, quality=1.0):
    return {
        "schema_version": "1.0",
        "experiment_id": "l3v-context-pilot",
        "observed_at": "2026-11-18T00:00:00Z",
        "baseline_sha": BASELINE,
        "candidate_sha": CANDIDATE,
        "suite": "repo-maintenance-v1",
        "cohort": "matched-task-cohort-v1",
        "treatment": {
            "manager_policy_id": "l3v-pilot-policy",
            "arm": arm,
            "instance": {"instance_key": instance_key},
        },
        "status": "passed",
        "provenance": "github",
        "confidence": "high",
        "metrics": {
            "repetition": repetition,
            "outcome_score": outcome,
            "resource_cost": cost,
            "quality_floor": quality,
            "task_fingerprint": f"{repetition:064x}",
            "environment_fingerprint": "e" * 64,
        },
    }


def compare(rows, **overrides):
    args = {
        "experiment_id": "l3v-context-pilot",
        "cohort": "matched-task-cohort-v1",
        "control_arm": "control",
        "treatment_arm": "treatment",
        "control_instance_key": CONTROL_KEY,
        "treatment_instance_key": TREATMENT_KEY,
        "outcome_key": "outcome_score",
        "outcome_direction": "higher",
        "cost_key": "resource_cost",
        "cost_unit": "normalized_units",
        "cost_status": "measured",
        "min_pairs": 2,
        "guardrails": [("quality_floor", 0.95)],
    }
    args.update(overrides)
    return compare_records(rows, **args)


class CompareExperimentRecordsTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            record("control", CONTROL_KEY, 1, 0.70, 10),
            record("control", CONTROL_KEY, 2, 0.80, 10),
            record("treatment", TREATMENT_KEY, 1, 0.80, 12),
            record("treatment", TREATMENT_KEY, 2, 0.90, 12),
        ]

    def test_computes_matched_delta_and_ratio(self):
        result = compare(self.rows)
        self.assertAlmostEqual(result["outcome"]["oriented_incremental_mean"], 0.10)
        self.assertAlmostEqual(result["resource_cost"]["incremental_mean"], 2.0)
        self.assertAlmostEqual(result["leverage_ratio"], 0.05)
        self.assertFalse(result["promotion_authorized"])

    def test_same_configured_instance_can_be_used_by_distinct_arms(self):
        for row in self.rows:
            if row["treatment"]["arm"] == "treatment":
                row["treatment"]["instance"]["instance_key"] = CONTROL_KEY
        result = compare(self.rows, treatment_instance_key=CONTROL_KEY)
        self.assertAlmostEqual(result["leverage_ratio"], 0.05)

    def test_guardrail_is_mandatory(self):
        with self.assertRaisesRegex(ComparisonError, "explicit quality guardrail"):
            compare(self.rows, guardrails=[])

    def test_estimated_cost_never_produces_realized_ratio(self):
        result = compare(self.rows, cost_status="estimated")
        self.assertIsNone(result["leverage_ratio"])
        self.assertIn("estimated", result["leverage_ratio_reason"])

    def test_usage_value_requires_matching_unit_and_status(self):
        rows = list(self.rows)
        for row in rows:
            row["usage"] = {
                "value": row["metrics"]["resource_cost"],
                "unit": "USD",
                "source": "provider billing receipt",
                "status": "measured",
            }
        result = compare(rows, cost_key="usage.value", cost_unit="USD")
        self.assertAlmostEqual(result["leverage_ratio"], 0.05)
        rows[0]["usage"]["unit"] = "tokens"
        with self.assertRaisesRegex(ComparisonError, "usage.unit"):
            compare(rows, cost_key="usage.value", cost_unit="USD")

    def test_lower_is_better_reverses_delta(self):
        rows = [
            record("control", CONTROL_KEY, 1, 10, 10),
            record("control", CONTROL_KEY, 2, 8, 10),
            record("treatment", TREATMENT_KEY, 1, 8, 12),
            record("treatment", TREATMENT_KEY, 2, 6, 12),
        ]
        result = compare(rows, outcome_direction="lower")
        self.assertAlmostEqual(result["outcome"]["oriented_incremental_mean"], 2.0)

    def test_zero_or_negative_incremental_cost_has_no_ratio(self):
        rows = [
            record("control", CONTROL_KEY, 1, 0.7, 12),
            record("control", CONTROL_KEY, 2, 0.8, 12),
            record("treatment", TREATMENT_KEY, 1, 0.8, 10),
            record("treatment", TREATMENT_KEY, 2, 0.9, 10),
        ]
        result = compare(rows)
        self.assertIsNone(result["leverage_ratio"])

    def test_guardrail_failure_suppresses_ratio(self):
        rows = list(self.rows)
        rows[-1] = record("treatment", TREATMENT_KEY, 2, 0.9, 12, quality=0.8)
        result = compare(rows)
        self.assertFalse(result["guardrails"]["satisfied"])
        self.assertIsNone(result["leverage_ratio"])

    def test_unmatched_repetitions_are_rejected(self):
        with self.assertRaisesRegex(ComparisonError, "identical repetition sets"):
            compare(self.rows[:-1])

    def test_superseded_rows_are_excluded(self):
        self.rows.append(record("control", CONTROL_KEY, 1, 0.1, 1))
        self.rows[-1]["status"] = "superseded"
        result = compare(self.rows)
        self.assertAlmostEqual(result["leverage_ratio"], 0.05)

    def test_malformed_fingerprint_is_rejected(self):
        self.rows[-1]["metrics"]["task_fingerprint"] = "placeholder"
        with self.assertRaisesRegex(ComparisonError, "64-character lowercase-hex"):
            compare(self.rows)

    def test_insufficient_pairs_are_rejected(self):
        with self.assertRaisesRegex(ComparisonError, "insufficient matched repetitions"):
            compare(self.rows, min_pairs=3)

    def test_missing_metric_is_rejected(self):
        del self.rows[-1]["metrics"]["resource_cost"]
        with self.assertRaisesRegex(ComparisonError, "missing metrics.resource_cost"):
            compare(self.rows)

    def test_duplicate_repetition_is_rejected(self):
        self.rows.append(record("control", CONTROL_KEY, 2, 0.75, 10))
        with self.assertRaisesRegex(ComparisonError, "duplicate repetition"):
            compare(self.rows)

    def test_task_fingerprint_mismatch_is_rejected(self):
        self.rows[-1]["metrics"]["task_fingerprint"] = "f" * 64
        with self.assertRaisesRegex(ComparisonError, "task_fingerprint"):
            compare(self.rows)

    def test_source_sha_mismatch_is_rejected(self):
        self.rows[-1]["candidate_sha"] = "3" * 40
        with self.assertRaisesRegex(ComparisonError, "source SHA changed"):
            compare(self.rows)


if __name__ == "__main__":
    unittest.main()
