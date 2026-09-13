"""PR support score. Hard gates dominate; this is decision-support only."""
from __future__ import annotations

from typing import Any

from ml_pipelines.features.moneyball import pr_moneyball


def score_pr(pr: dict[str, Any], lane_size: int = 1) -> dict[str, Any]:
    row = pr_moneyball(pr, lane_size=lane_size)
    row["title"] = pr.get("title") or ""
    row["author"] = pr.get("author")
    row["changed_files"] = int(pr.get("changedFiles") or 0)
    return row
