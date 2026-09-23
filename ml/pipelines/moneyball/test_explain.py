import unittest

from ml.pipelines.moneyball.explain import explain


class ExplainTests(unittest.TestCase):
    def test_terms(self) -> None:
        row = explain({"number": 1, "changed_files": 2, "dual_gate": "green", "mergeable_state": "clean", "tests": True})
        self.assertIn("dual_gate_green", row["terms"])
        self.assertEqual(row["lane"], "promote")
