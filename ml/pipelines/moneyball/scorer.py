"""scorer: Transparent weighted lane classifier."""
from __future__ import annotations

from typing import Any, Mapping

from ml.pipelines.lib.types import Lane

WEIGHTS = {
    "dual_gate_green": 5.0,
    "mergeable_clean": 3.0,
    "files_small": 1.5,
    "tests_present": 1.0,
    "security_fix": 2.0,
    "docs_only": 0.5,
    "stale_base": -2.0,
    "mergeable_dirty": -8.0,
    "mergeable_unstable": -1.0,
    "changed_files_over_40": -3.0,
    "minesweeper_overlap": -6.0,
    "ml_wholesale": -10.0,
    "jules_bot": -0.25,
}

THRESHOLDS = {"promote": 4.0, "wait": 0.0, "hold": -3.0}


def _features(pr: Mapping[str, Any]) -> dict[str, float]:
    files = int(pr.get("changed_files") or 0)
    state = str(pr.get("mergeable_state") or "unknown")
    return {
        "dual_gate_green": 1.0 if pr.get("dual_gate") == "green" else 0.0,
        "mergeable_clean": 1.0 if state == "clean" else 0.0,
        "files_small": 1.0 if files and files <= 8 else 0.0,
        "tests_present": 1.0 if pr.get("tests") else 0.0,
        "security_fix": 1.0 if pr.get("security") else 0.0,
        "docs_only": 1.0 if pr.get("docs_only") else 0.0,
        "stale_base": 1.0 if pr.get("stale_base") else 0.0,
        "mergeable_dirty": 1.0 if state == "dirty" else 0.0,
        "mergeable_unstable": 1.0 if state == "unstable" else 0.0,
        "changed_files_over_40": 1.0 if files > 40 else 0.0,
        "minesweeper_overlap": 1.0 if pr.get("minesweeper") else 0.0,
        "ml_wholesale": 1.0 if pr.get("ml_wholesale") else 0.0,
        "jules_bot": 1.0 if pr.get("author") == "google-labs-jules[bot]" else 0.0,
    }


def score(pr: Mapping[str, Any]) -> float:
    feats = _features(pr)
    return round(sum(WEIGHTS[key] * value for key, value in feats.items()), 4)


def classify(points: float, pr: Mapping[str, Any]) -> Lane:
    state = str(pr.get("mergeable_state") or "")
    if pr.get("ml_wholesale") or (int(pr.get("changed_files") or 0) > 80 and state == "dirty"):
        return Lane.EXTRACT
    if state == "dirty" or pr.get("minesweeper"):
        return Lane.HOLD
    if points >= THRESHOLDS["promote"] and pr.get("dual_gate") == "green":
        return Lane.PROMOTE
    if state == "unstable" or points >= THRESHOLDS["wait"]:
        return Lane.WAIT
    if points >= THRESHOLDS["hold"]:
        return Lane.OBSERVE
    return Lane.HOLD
