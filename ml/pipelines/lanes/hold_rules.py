from __future__ import annotations
from typing import Any, Mapping

def should_hold(pr: Mapping[str, Any]) -> bool:
    if pr.get("master_staging_base") or pr.get("stacked_feature_base"):
        return True
    if pr.get("hitl_risk"):
        return True
    if str(pr.get("mergeable_state") or "") == "dirty" and int(pr.get("changed_files") or 0) <= 80:
        if not pr.get("ml_wholesale"):
            return True
    return False
