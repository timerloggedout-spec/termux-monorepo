from __future__ import annotations

from typing import Any

from ml.pipelines.lanes.classify import classify_pr
from ml.pipelines.moneyball.scorer import score
from ml.pipelines.moneyball.weights import WEIGHTS


def explain(pr: dict[str, Any]) -> dict[str, Any]:
    return {
        "number": pr.get("number"),
        "score": score(pr),
        "lane": classify_pr(pr).value,
        "weights": WEIGHTS,
        "why": pr.get("why"),
        "title": pr.get("title"),
    }
