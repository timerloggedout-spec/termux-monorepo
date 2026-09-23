"""Tests for stage 10_ingest."""
from __future__ import annotations

import unittest

from ml.pipelines.lib.types import StageStatus
from ml.pipelines.stages.s10_ingest.stage import IngestStage


class TestIngestStage(unittest.TestCase):
    def test_ok_on_empty_snapshot(self) -> None:
        result = IngestStage().run({"snapshot": {"master_sha": "abc", "prs": []}})
        self.assertEqual(result.stage_id, "10_ingest")
        self.assertEqual(result.status, StageStatus.OK)
        self.assertEqual(result.artifacts["pr_count"], 0)

    def test_counts_prs(self) -> None:
        result = IngestStage().run({"snapshot": {"prs": [{"number": 1}, {"number": 2}]}})
        self.assertEqual(result.artifacts["pr_count"], 2)


if __name__ == "__main__":
    unittest.main()
