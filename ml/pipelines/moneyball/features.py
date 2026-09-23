"""Feature vector for a PR packet."""
from __future__ import annotations

from typing import Any, Mapping

from ml.pipelines.lib.weights import FILES_OVER_40, FILES_SMALL


def features(pr: Mapping[str, Any]) -> dict[str, float]:
    files = int(pr.get("changed_files") or 0)
    state = str(pr.get("mergeable_state") or "unknown")
    return {
        "dual_gate_green": 1.0 if pr.get("dual_gate") == "green" else 0.0,
        "mergeable_clean": 1.0 if state == "clean" else 0.0,
        "files_small": 1.0 if files and files <= FILES_SMALL else 0.0,
        "tests_present": 1.0 if pr.get("tests") else 0.0,
        "security_fix": 1.0 if pr.get("security") else 0.0,
        "docs_only": 1.0 if pr.get("docs_only") else 0.0,
        "stale_base": 1.0 if pr.get("stale_base") else 0.0,
        "mergeable_dirty": 1.0 if state == "dirty" else 0.0,
        "mergeable_unstable": 1.0 if state == "unstable" else 0.0,
        "changed_files_over_40": 1.0 if files > FILES_OVER_40 else 0.0,
        "minesweeper_overlap": 1.0 if pr.get("minesweeper") else 0.0,
        "ml_wholesale": 1.0 if pr.get("ml_wholesale") else 0.0,
        "jules_bot": 1.0 if pr.get("author") == "google-labs-jules[bot]" else 0.0,
        "master_staging_base": 1.0 if pr.get("master_staging_base") else 0.0,
        "stacked_feature_base": 1.0 if pr.get("stacked_feature_base") else 0.0,
        "hitl_risk": 1.0 if pr.get("hitl_risk") else 0.0,
        "draft": 1.0 if pr.get("draft") else 0.0,
        "replay_landed": 1.0 if pr.get("replay_landed") else 0.0,
    }
