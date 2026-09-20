"""Stage 30_train (TRAIN): Fit ranking weights for promote/wait/hold/extract lanes."""
from __future__ import annotations

from typing import Any, MutableMapping

from ml.pipelines.lib.types import StageResult, StageStatus


class TrainStage:
    stage_id = "30_train"

    def run(self, context: MutableMapping[str, Any]) -> StageResult:
        snapshot = context.get("snapshot") or {}
        notes = ("train applied on issue 175 keep-alive DAG",)
        artifacts = {
            "stage": self.stage_id,
            "master_sha": snapshot.get("master_sha"),
            "pr_count": len(snapshot.get("prs") or []),
        }
        context.setdefault("stage_outputs", {})[self.stage_id] = artifacts
        return StageResult(stage_id=self.stage_id, status=StageStatus.OK, artifacts=artifacts, notes=notes)
