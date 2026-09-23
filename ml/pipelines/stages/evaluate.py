from __future__ import annotations
from typing import Any, MutableMapping
from ml.pipelines.lib.context import prs, put
from ml.pipelines.lib.types import StageResult, StageStatus
from ml.pipelines.moneyball.scorer import classify, score

def run(ctx: MutableMapping[str, Any]) -> StageResult:
    lanes = [
        {"number": pr.get("number"), "lane": classify(score(pr), pr).value, "score": score(pr)}
        for pr in prs(ctx)
    ]
    put(ctx, "lanes", lanes)
    return StageResult(stage_id="40_evaluate", status=StageStatus.OK, artifacts={"lanes": lanes})
