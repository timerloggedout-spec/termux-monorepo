from __future__ import annotations

from typing import Any

from ml.pipelines.lanes.classify import classify_pr
from ml.pipelines.moneyball.scorer import score


def stage_features(context: dict[str, Any]) -> None:
    rows = []
    for pr in context.get("prs") or []:
        lane = classify_pr(pr)
        rows.append(
            {
                "number": pr["number"],
                "lane": lane.value,
                "score": score(pr),
                "title": pr.get("title"),
                "why": pr.get("why"),
            }
        )
    context["lanes"] = rows
