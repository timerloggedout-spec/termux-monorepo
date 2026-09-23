from __future__ import annotations
from typing import Any, MutableMapping
from ml.pipelines.contracts.gate import assert_promotable
from ml.pipelines.lib.context import prs
from ml.pipelines.lib.errors import GateBlocked
from ml.pipelines.lib.types import StageResult, StageStatus
from ml.pipelines.moneyball.scorer import classify, score

def run(ctx: MutableMapping[str, Any]) -> StageResult:
    blocked = 0
    for pr in prs(ctx):
        lane = classify(score(pr), pr)
        try:
            assert_promotable(pr, lane)
        except GateBlocked:
            blocked += 1
    return StageResult(stage_id="50_deploy", status=StageStatus.OK, artifacts={"blocked": blocked})
