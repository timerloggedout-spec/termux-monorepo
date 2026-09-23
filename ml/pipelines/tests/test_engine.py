"""Engine DAG tests."""
from __future__ import annotations

import unittest

from ml.pipelines.lib.engine import all_ok, run_dag, summarize
from ml.pipelines.lib.types import StageResult, StageStatus


class TestEngine(unittest.TestCase):
    def test_halts_on_fail(self) -> None:
        def ok(ctx):
            return StageResult("a", StageStatus.OK)

        def bad(ctx):
            return StageResult("b", StageStatus.FAILED)

        def never(ctx):
            raise AssertionError("should not run")

        results = run_dag([("a", ok), ("b", bad), ("c", never)], {})
        self.assertEqual([item.stage_id for item in results], ["a", "b"])
        self.assertFalse(all_ok(results))
        self.assertEqual(summarize(results)["b"], "failed")


if __name__ == "__main__":
    unittest.main()
