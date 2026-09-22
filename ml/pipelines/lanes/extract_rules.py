from __future__ import annotations
from typing import Any, Mapping

def should_extract(pr: Mapping[str, Any]) -> bool:
    files = int(pr.get("changed_files") or 0)
    if pr.get("ml_wholesale"):
        return True
    if files > 80 and str(pr.get("mergeable_state") or "") == "dirty":
        return True
    if pr.get("minesweeper") and files > 40:
        return True
    return False
