import unittest
from ml.pipelines.lib.engine import run_dag
from ml.pipelines.lib.io import load_json
from ml.pipelines.lib.latest import latest_session_path
from ml.pipelines.stages import STAGES

class StagesTest(unittest.TestCase):
    def test_pipeline(self) -> None:
        ctx = {"snapshot": load_json(latest_session_path())}
        run_dag(STAGES, ctx)
        self.assertEqual(ctx["issue"], 175)
        self.assertIn("EXTRACT", ctx["lane_counts"])
        self.assertIn("cctv", ctx)

if __name__ == "__main__":
    unittest.main()
