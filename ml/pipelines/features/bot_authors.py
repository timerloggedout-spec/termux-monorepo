"""Jules/bot authorship is a mild penalty, not a HOLD by itself."""
from __future__ import annotations
from typing import Any, Mapping

def flag(pr: Mapping[str, Any]) -> bool:
    return "bot" in str(pr.get("author") or "").lower()
