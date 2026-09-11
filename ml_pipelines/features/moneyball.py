"""Decision-support MoneyBall features. Authority always dominates score."""
from __future__ import annotations

from typing import Any

from .merge_hygiene import merge_hygiene_score


def pr_moneyball(pr: dict[str, Any], lane_size: int = 1) -> dict[str, Any]:
    hygiene = merge_hygiene_score(pr)
    overlap_penalty = min(0.4, max(0.0, (lane_size - 1) * 0.08))
    files = int(pr.get("changedFiles") or 0)
    size_penalty = 0.2 if files >= 40 else 0.0
    support = max(0.0, hygiene["score"] - overlap_penalty - size_penalty)
    return {
        "number": pr.get("number"),
        "support_score": round(support, 3),
        "overlap_penalty": round(overlap_penalty, 3),
        "size_penalty": size_penalty,
        "authority": "observe_only",
        "note": "Hard gates and operator rules dominate this score.",
    }
