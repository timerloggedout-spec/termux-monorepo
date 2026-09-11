import unittest
from pathlib import Path

from ml_pipelines.ingest.snapshot import load_snapshot
from ml_pipelines.pipelines.orchestrate import run_all

FIX = Path(__file__).resolve().parents[2] / "ml_pipelines/fixtures/ops-snapshot.json"


class PipelineTests(unittest.TestCase):
    def test_run_all(self):
        envelope = run_all(load_snapshot(FIX).as_dict())
        self.assertIn("digest", envelope)
        self.assertIn("pr_minesweeper", envelope["stages"])
        self.assertIn("issue_175_matrix", envelope["stages"])
        classified = envelope["stages"]["pr_minesweeper"]["result"]["classified"]
        self.assertGreaterEqual(len(classified), 10)


if __name__ == "__main__":
    unittest.main()
