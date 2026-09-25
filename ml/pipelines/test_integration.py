import unittest
from ml.pipelines.lanes.vocab import INVALID_PARKING
from ml.pipelines.lib.engine import run_dag
from ml.pipelines.lib.io import load_json
from ml.pipelines.lib.latest import latest_session_path
from ml.pipelines.stages import STAGES

class IntegrationTest(unittest.TestCase):
    def test_no_parking_labels(self) -> None:
        ctx = {"snapshot": load_json(latest_session_path())}
        run_dag(STAGES, ctx)
        for row in ctx["lanes"]:
            self.assertNotIn(row["lane"], INVALID_PARKING)

if __name__ == "__main__":
    unittest.main()
