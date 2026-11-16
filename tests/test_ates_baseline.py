import unittest

from she.metrics.ates_baseline import BaselineCohort, fingerprint_task


class ATESBaselineTests(unittest.TestCase):
    def cohort(self):
        return BaselineCohort.from_mapping({
            "schema_version": "ates.baseline.v1",
            "cohort_id": "repair-v1",
            "task_contract_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "environment_fingerprint": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "tasks": [
                {
                    "task_id": "t1",
                    "task_fingerprint": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                    "repetitions_sec": [10, 14, 12],
                    "median_sec": 12,
                },
                {
                    "task_id": "t2",
                    "task_fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                    "repetitions_sec": [20, 22, 18],
                },
            ],
        })

    def test_median_and_exact_task_resolution(self):
        cohort = self.cohort()
        self.assertEqual(cohort.tasks[0].median_sec, 12)
        self.assertEqual(cohort.sequential_seconds(["cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]), 32)

    def test_unknown_task_fails_closed(self):
        with self.assertRaises(KeyError):
            self.cohort().sequential_seconds(["bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"])

    def test_duplicate_task_request_fails_closed(self):
        with self.assertRaises(ValueError):
            self.cohort().sequential_seconds(["cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc", "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"])

    def test_invalid_median_cannot_override_measurements(self):
        with self.assertRaises(ValueError):
            BaselineCohort.from_mapping({
                "schema_version": "ates.baseline.v1",
                "cohort_id": "repair-v1",
                "task_contract_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "environment_fingerprint": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "tasks": [{
                    "task_id": "t1",
                    "task_fingerprint": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                    "repetitions_sec": [10, 14, 12],
                    "median_sec": 99,
                }],
            })

    def test_task_fingerprint_is_canonical(self):
        self.assertEqual(
            fingerprint_task({"b": 2, "a": 1}),
            fingerprint_task({"a": 1, "b": 2}),
        )
        self.assertEqual(len(fingerprint_task({"a": 1})), 64)


if __name__ == "__main__":
    unittest.main()
