"""Tournament — meta-selection across DoE campaigns.

Given N trial results, rank by composite score, retain winner + losers to
Hindsight as memory, update leaderboard.
"""
from __future__ import annotations
from typing import Any
from .leaderboard import Leaderboard


def campaign(role: str, task: str, trial_results: list[dict],
             leaderboard: Leaderboard | None = None) -> dict:
    lb = leaderboard or Leaderboard()
    for r in trial_results:
        lb.record(
            role=role, task=task,
            provider=r.get("provider","?"), model=r.get("model","?"),
            score=r.get("composite", 0.0),
            cost=r.get("cost_usd", 0.0),
            latency_ms=r.get("latency_ms", 0),
            ok=r.get("ok", True),
        )
    winners = lb.top(role, task, k=3)
    losers = lb.worst(role, task, k=3)
    return {
        "role": role, "task": task,
        "trials": len(trial_results),
        "winners": winners,
        "losers": losers,
    }
