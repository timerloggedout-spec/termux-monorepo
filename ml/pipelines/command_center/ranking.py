"""Rank EXTRACT / CANDIDATE rows for operator attention."""
from __future__ import annotations

from typing import Any

from ml.pipelines.command_center.board import project_row


def rank(prs: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    rows = [project_row(pr) for pr in prs]
    order = {"EXTRACT": 0, "CANDIDATE": 1, "NEED_EVIDENCE": 2, "SUPERSEDE": 3}
    rows.sort(key=lambda r: (order.get(r["lane"], 9), -float(r["score"]), r["number"]))
    return rows[:limit]
