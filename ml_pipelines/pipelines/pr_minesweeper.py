"""MLP-03: classify every open PR. No writes."""
from __future__ import annotations

from typing import Any

from ml_pipelines.features.lane_overlap import cluster
from ml_pipelines.minesweeper.classify import classify_pr
from ml_pipelines.minesweeper.overlap import overlap_summary


def run(snapshot: dict[str, Any]) -> dict[str, Any]:
    prs = list(snapshot.get("prs") or [])
    clusters = cluster(prs)
    classified = []
    for pr in prs:
        hay_lane = None
        for lane, numbers in clusters.items():
            if int(pr["number"]) in numbers and lane != "unclassified":
                hay_lane = lane
                break
        lane_size = len(clusters.get(hay_lane, [])) if hay_lane else 1
        classified.append(classify_pr(pr, lane_size=lane_size))
    return {
        "classified": classified,
        "clusters": clusters,
        "summary": overlap_summary(classified),
    }
