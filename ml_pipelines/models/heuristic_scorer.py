"""Combine hygiene + minesweeper into a support score. Observe-only."""
from __future__ import annotations

from typing import Any

from ml_pipelines.features.moneyball import pr_moneyball
from ml_pipelines.minesweeper.classify import classify_pr

DISPOSITION_BIAS = {
    "MERGE_CANDIDATE": 0.12,
    "EXTRACT_CANDIDATE": 0.06,
    "HOLD": 0.0,
    "LANE_DUPLICATE": -0.08,
    "MEGA_REVIEW": -0.12,
    "DIRTY_HOLD": -0.18,
    "NO_GO": -0.4,
}


def score_pr(pr: dict[str, Any], lane_size: int = 1) -> dict[str, Any]:
    money = pr_moneyball(pr, lane_size=lane_size)
    classified = classify_pr(pr, lane_size=lane_size)
    bias = DISPOSITION_BIAS.get(str(classified["disposition"]), 0.0)
    support = max(0.0, min(1.0, money["support_score"] + bias))
    return {
        **money,
        "support_score": round(support, 3),
        "lane": classified["lane"],
        "disposition": classified["disposition"],
        "authority": "observe_only",
    }
