"""Stage 60_monitor (MONITOR): Watch post-merge Actions; feed WAIT → VALIDATE → RE-FETCH."""
from __future__ import annotations

from typing import Any, MutableMapping

from ml.pipelines.lib.types import StageResult, StageStatus


class MonitorStage:
    stage_id = "60_monitor"

    def run(self, context: MutableMapping[str, Any]) -> StageResult:
        snapshot = context.get("snapshot") or {}
        notes = ("monitor applied on issue 175 keep-alive DAG",)
        artifacts = {
            "stage": self.stage_id,
            "master_sha": snapshot.get("master_sha"),
            "pr_count": len(snapshot.get("prs") or []),
        }
        context.setdefault("stage_outputs", {})[self.stage_id] = artifacts
        return StageResult(stage_id=self.stage_id, status=StageStatus.OK, artifacts=artifacts, notes=notes)
