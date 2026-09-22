from __future__ import annotations
from typing import Any, MutableMapping
from ml.pipelines.lib.context import snapshot
from ml.pipelines.lib.types import StageResult, StageStatus

def run(ctx: MutableMapping[str, Any]) -> StageResult:
    snap = snapshot(ctx)
    return StageResult(
        stage_id="00_recon",
        status=StageStatus.OK,
        artifacts={"master_sha": snap.get("master_sha"), "issue": snap.get("issue", 175)},
    )
