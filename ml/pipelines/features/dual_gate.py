"""Named dual-gate feature. Combined commit status is not dual-gate."""
from __future__ import annotations
from typing import Any, Mapping

def dual_gate_green(pr: Mapping[str, Any]) -> bool:
    return pr.get("dual_gate") == "green"

def vercel_is_nongate(pr: Mapping[str, Any]) -> bool:
    """Issue #772: Vercel rate-limit / mergeable_state=unstable is non-gate."""
    return True
