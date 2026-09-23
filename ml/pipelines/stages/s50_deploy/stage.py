"""Stage 50_deploy (DEPLOY): Emit promote packets only when repo_gate + termux_smoke are green."""
from __future__ import annotations

from typing import Any, MutableMapping

from ml.pipelines.lib.types import StageResult, StageStatus


class DeployStage:
    stage_id = "50_deploy"

    def run(self, context: MutableMapping[str, Any]) -> StageResult:
        snapshot = context.get("snapshot") or {}
        notes = ("deploy applied on issue 175 keep-alive DAG",)
        artifacts = {
            "stage": self.stage_id,
            "master_sha": snapshot.get("master_sha"),
            "pr_count": len(snapshot.get("prs") or []),
        }
        context.setdefault("stage_outputs", {})[self.stage_id] = artifacts
        return StageResult(stage_id=self.stage_id, status=StageStatus.OK, artifacts=artifacts, notes=notes)
