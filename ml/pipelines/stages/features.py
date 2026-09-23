from __future__ import annotations
from typing import Any, MutableMapping
from ml.pipelines.lib.context import prs, put
from ml.pipelines.lib.types import StageResult, StageStatus
from ml.pipelines.moneyball.scorer import score

def run(ctx: MutableMapping[str, Any]) -> StageResult:
    scored = [{"number": pr.get("number"), "score": score(pr)} for pr in prs(ctx)]
    put(ctx, "scored", scored)
    return StageResult(stage_id="20_features", status=StageStatus.OK, artifacts={"n": len(scored)})
