from __future__ import annotations
from typing import Any, Mapping

def should_observe(pr: Mapping[str, Any]) -> bool:
    if pr.get("draft"):
        return True
    author = str(pr.get("author") or "")
    if "jules" in author and not pr.get("minesweeper"):
        return True
    return False
