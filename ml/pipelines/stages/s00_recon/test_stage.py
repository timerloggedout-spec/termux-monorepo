"""Tests for stage 00_recon."""
from __future__ import annotations

import unittest

from ml.pipelines.lib.types import StageStatus
from ml.pipelines.stages.s00_recon.stage import ReconStage


class TestReconStage(unittest.TestCase):
    def test_ok_on_empty_snapshot(self) -> None:
        result = ReconStage().run({"snapshot": {"master_sha": "abc", "prs": []}})
        self.assertEqual(result.stage_id, "00_recon")
        self.assertEqual(result.status, StageStatus.OK)
        self.assertEqual(result.artifacts["pr_count"], 0)

    def test_counts_prs(self) -> None:
        result = ReconStage().run({"snapshot": {"prs": [{"number": 1}, {"number": 2}]}})
        self.assertEqual(result.artifacts["pr_count"], 2)


if __name__ == "__main__":
    unittest.main()
