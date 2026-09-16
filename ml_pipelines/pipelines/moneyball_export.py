"""MoneyBall export. Decision support only."""
from __future__ import annotations

from typing import Any

from ml_pipelines.eval.leaderboard import leaderboard
from ml_pipelines.features.lane_overlap import cluster
from ml_pipelines.models.heuristic_scorer import score_pr


def run(snapshot: dict[str, Any]) -> dict[str, Any]:
    prs = list(snapshot.get("prs") or [])
    clusters = cluster(prs)
    scored = []
    for pr in prs:
        lane_size = 1
        for numbers in clusters.values():
            if int(pr["number"]) in numbers:
                lane_size = max(lane_size, len(numbers))
        scored.append(score_pr(pr, lane_size=lane_size))
    return {
        "leaderboard": leaderboard(scored),
        "authority": "observe_only",
    }
