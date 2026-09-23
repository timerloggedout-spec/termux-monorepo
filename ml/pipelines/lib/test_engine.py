import unittest
from typing import Any, MutableMapping

from ml.pipelines.lib.engine import run_dag, summarize
from ml.pipelines.lib.types import StageResult, StageStatus


def _ok(stage_id: str) -> StageResult:
    return StageResult(stage_id=stage_id, status=StageStatus.OK)


def _fail(stage_id: str) -> StageResult:
    return StageResult(stage_id=stage_id, status=StageStatus.FAILED)


class EngineTests(unittest.TestCase):
    def test_runs_in_order(self) -> None:
        ctx: MutableMapping[str, Any] = {}
        results = run_dag([("a", lambda c: _ok("a")), ("b", lambda c: _ok("b"))], ctx)
        self.assertEqual(summarize(results), {"a": "ok", "b": "ok"})

    def test_halts_on_fail(self) -> None:
        ctx: MutableMapping[str, Any] = {}
        results = run_dag(
            [("a", lambda c: _fail("a")), ("b", lambda c: _ok("b"))],
            ctx,
        )
        self.assertEqual([item.stage_id for item in results], ["a"])
