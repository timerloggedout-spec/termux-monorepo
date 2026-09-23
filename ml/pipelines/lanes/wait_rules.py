from __future__ import annotations
from typing import Any, Mapping

def should_wait(pr: Mapping[str, Any]) -> bool:
    if str(pr.get("mergeable_state") or "") == "unstable":
        if not pr.get("hitl_risk") and not pr.get("draft"):
            return True
    if pr.get("stale_base") and pr.get("dual_gate") == "green":
        return True
    return False
