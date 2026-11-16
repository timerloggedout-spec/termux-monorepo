import unittest

from she.edge.conformance import validate_run
from she.evaluation.tournament import CohortSpec, comparable_cohort


class ForesightExecutionTest(unittest.TestCase):
    def test_manager_runs_must_share_the_cohort_contract(self):
        spec = CohortSpec("fixture-v1", "rubric-v1", "env-a", "tools-a", "budget-a")
        runs = [
            {
                "task_fixture": "fixture-v1",
                "rubric_version": "rubric-v1",
                "environment_fingerprint": "env-a",
                "tool_inventory_fingerprint": "tools-a",
                "budget": "budget-a",
            },
            {
                "task_fixture": "fixture-v1",
                "rubric_version": "rubric-v1",
                "environment_fingerprint": "env-a",
                "tool_inventory_fingerprint": "tools-a",
                "budget": "budget-a",
            },
        ]
        self.assertTrue(comparable_cohort(spec, runs))

    def test_edge_energy_requires_method(self):
        record = {
            "target": "termux",
            "device": "fixture",
            "soc": "fixture",
            "ram": "8GB",
            "os_version": "android",
            "runtime": "llama.cpp",
            "runtime_version": "UNPINNED",
            "model_digest": "sha256:x",
            "quantization": "Q4",
            "backend": "cpu",
            "accelerator": "cpu",
            "workload_fixture": "fixture-v1",
            "tokens_per_second": 10,
            "peak_rss_bytes": 100,
            "wall_time_ms": 100,
            "failure_class": "none",
            "energy_mwh": 2,
        }
        self.assertIn("energy_mwh requires energy_method", validate_run(record))


if __name__ == "__main__":
    unittest.main()
