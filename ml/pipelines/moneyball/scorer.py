"""scorer: Transparent weighted lane classifier."""
from __future__ import annotations

from typing import Any, Mapping

from ml.pipelines.lib.types import Lane
from ml.pipelines.lib.weights import FILES_WHOLESALE, THRESHOLDS, WEIGHTS
from ml.pipelines.moneyball.features import features as _features


def score(pr: Mapping[str, Any]) -> float:
    feats = _features(pr)
    return round(sum(WEIGHTS[key] * value for key, value in feats.items()), 4)


def classify(points: float, pr: Mapping[str, Any]) -> Lane:
    state = str(pr.get("mergeable_state") or "")
    files = int(pr.get("changed_files") or 0)
    if pr.get("ml_wholesale") or (files > FILES_WHOLESALE and state == "dirty"):
        return Lane.EXTRACT
    if pr.get("master_staging_base") or pr.get("stacked_feature_base"):
        return Lane.HOLD
    if pr.get("hitl_risk"):
        return Lane.HOLD
    if pr.get("draft"):
        return Lane.OBSERVE
    if pr.get("supersede"):
        return Lane.SUPERSEDE
    if state == "dirty" or pr.get("minesweeper"):
        return Lane.HOLD if files <= FILES_WHOLESALE else Lane.EXTRACT
    if points >= THRESHOLDS["promote"] and pr.get("dual_gate") == "green" and state == "clean":
        return Lane.PROMOTE
    if state == "unstable" or points >= THRESHOLDS["wait"]:
        return Lane.WAIT
    if points >= THRESHOLDS["hold"]:
        return Lane.OBSERVE
    return Lane.HOLD
