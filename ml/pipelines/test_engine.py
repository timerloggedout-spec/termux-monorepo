import unittest
from ml.pipelines.lib.engine import run_dag, summarize

class EngineTest(unittest.TestCase):
    def test_run(self) -> None:
        ctx = {"n": 0}
        def bump(c):
            c["n"] += 1
        results = run_dag([("a", bump), ("b", bump)], ctx)
        self.assertEqual(ctx["n"], 2)
        self.assertTrue(summarize(results)["ok"])

if __name__ == "__main__":
    unittest.main()
