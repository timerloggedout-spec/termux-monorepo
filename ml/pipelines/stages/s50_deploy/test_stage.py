"""Tests for stage 50_deploy."""
from __future__ import annotations

import unittest

from ml.pipelines.lib.types import StageStatus
from ml.pipelines.stages.s50_deploy.stage import DeployStage


class TestDeployStage(unittest.TestCase):
    def test_ok_on_empty_snapshot(self) -> None:
        result = DeployStage().run({"snapshot": {"master_sha": "abc", "prs": []}})
        self.assertEqual(result.stage_id, "50_deploy")
        self.assertEqual(result.status, StageStatus.OK)
        self.assertEqual(result.artifacts["pr_count"], 0)

    def test_counts_prs(self) -> None:
        result = DeployStage().run({"snapshot": {"prs": [{"number": 1}, {"number": 2}]}})
        self.assertEqual(result.artifacts["pr_count"], 2)


if __name__ == "__main__":
    unittest.main()
