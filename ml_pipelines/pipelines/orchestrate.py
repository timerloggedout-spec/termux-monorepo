"""Run the default observe-mode DAG."""
from __future__ import annotations

from typing import Any

from ml_pipelines.contracts import CONTRACT, digest
from ml_pipelines.pipelines import actions_health
from ml_pipelines.pipelines import commit_analysis
from ml_pipelines.pipelines import extract_ledger
from ml_pipelines.pipelines import gitmodules_audit
from ml_pipelines.pipelines import issue_175_matrix
from ml_pipelines.pipelines import lane_consolidation
from ml_pipelines.pipelines import manus_harvester
from ml_pipelines.pipelines import moneyball_export
from ml_pipelines.pipelines import pr_minesweeper
from ml_pipelines.pipelines import provider_attribution
from ml_pipelines.registry import PipelineRegistry

STAGES = {
    "issue_175_matrix": issue_175_matrix.run,
    "pr_minesweeper": pr_minesweeper.run,
    "commit_analysis": commit_analysis.run,
    "actions_health": actions_health.run,
    "provider_attribution": provider_attribution.run,
    "lane_consolidation": lane_consolidation.run,
    "moneyball_export": moneyball_export.run,
    "extract_ledger": extract_ledger.run,
    "gitmodules_audit": gitmodules_audit.run,
    "manus_harvester": manus_harvester.run,
}


def build_registry() -> PipelineRegistry:
    registry = PipelineRegistry()
    for name, fn in STAGES.items():
        registry.register(name, fn)
    return registry


def run_all(snapshot: dict[str, Any]) -> dict[str, Any]:
    registry = build_registry()
    results = {name: registry.run(name, snapshot) for name in registry.names()}
    envelope = {"contract": CONTRACT, "stages": results}
    envelope["digest"] = digest({"contract": CONTRACT, "stage_names": sorted(results)})
    return envelope
