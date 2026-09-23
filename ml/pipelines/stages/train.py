from __future__ import annotations
from typing import Any, MutableMapping
from ml.pipelines.lib.types import StageResult, StageStatus
from ml.pipelines.lib.weights import WEIGHTS

def run(ctx: MutableMapping[str, Any]) -> StageResult:
    return StageResult(
        stage_id="30_train",
        status=StageStatus.OK,
        artifacts={"note": "weights static", "n_weights": len(WEIGHTS)},
    )
