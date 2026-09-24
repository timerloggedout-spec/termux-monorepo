"""Human-readable score breakdown."""
from __future__ import annotations

from typing import Any, Mapping

from ml.pipelines.lib.weights import WEIGHTS
from ml.pipelines.moneyball.features import features
from ml.pipelines.moneyball.scorer import classify, score


def explain(pr: Mapping[str, Any]) -> dict[str, Any]:
    feats = features(pr)
    terms = {key: round(WEIGHTS[key] * value, 4) for key, value in feats.items() if value}
    points = score(pr)
    return {
        "number": pr.get("number"),
        "score": points,
        "lane": classify(points, pr).value,
        "terms": terms,
    }
