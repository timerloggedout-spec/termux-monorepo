import unittest
from ml.pipelines.lib.engine import run_dag, summarize
from ml.pipelines.stages import STAGES

SNAP = {
    "master_sha": "d10a7a54",
    "issue": 175,
    "prs": [
        {"number": 707, "changed_files": 3, "mergeable_state": "clean", "dual_gate": "green", "tests": True},
        {"number": 48, "changed_files": 73, "mergeable_state": "dirty", "master_staging_base": True},
    ],
}

class StageTests(unittest.TestCase):
    def test_dag(self) -> None:
        ctx: dict = {"snapshot": SNAP}
        results = run_dag(STAGES, ctx)
        self.assertEqual(len(results), 7)
        self.assertTrue(all(v == "ok" for v in summarize(results).values()))
        lanes = {row["number"]: row["lane"] for row in ctx["lanes"]}
        self.assertEqual(lanes[707], "promote")
        self.assertEqual(lanes[48], "hold")
