"""Local leaderboard from scored PRs. Repository-local evidence first."""
from __future__ import annotations

from typing import Any


def leaderboard(rows: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    ranked = sorted(rows, key=lambda row: row.get("support_score", 0), reverse=True)
    return ranked[:limit]
