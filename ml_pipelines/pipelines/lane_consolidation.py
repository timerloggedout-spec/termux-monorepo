"""Lane consolidation evidence for RL-19 follow-through."""
from __future__ import annotations

from typing import Any

from ml_pipelines.features.drift import drift_flags
from ml_pipelines.features.lane_overlap import cluster


def run(snapshot: dict[str, Any]) -> dict[str, Any]:
    clusters = cluster(list(snapshot.get("prs") or []))
    return {"clusters": clusters, "drift": drift_flags(clusters)}
