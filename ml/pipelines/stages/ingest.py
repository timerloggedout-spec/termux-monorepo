from __future__ import annotations
from typing import Any, MutableMapping
from ml.pipelines.lib.context import prs
from ml.pipelines.lib.types import StageResult, StageStatus

def run(ctx: MutableMapping[str, Any]) -> StageResult:
    items = prs(ctx)
    return StageResult(stage_id="10_ingest", status=StageStatus.OK, artifacts={"n": len(items)})
