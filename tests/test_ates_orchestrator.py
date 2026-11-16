import unittest
from she.metrics.ates_orchestrator import reduce_benchmark_results

class ATESOrchestratorReducerTests(unittest.TestCase):
    def test_reduces_deterministic_results(self):
        rows=[
            {"outcome":"PASS","net_score":1.0,"failures":[]},
            {"outcome":"FAIL_DETERMINISTIC","net_score":0.0,"failures":["actor:distractor_leak","critic:required_fragment_mismatch"]},
        ]
        result=reduce_benchmark_results(rows)
        self.assertEqual(result.cases,2)
        self.assertEqual(result.deterministic_pass_rate,0.5)
        self.assertEqual(result.boundary_failure_rate,0.5)
        self.assertEqual(result.omission_failure_rate,0.5)
        self.assertEqual(result.mean_net_score,0.5)

if __name__ == "__main__": unittest.main()