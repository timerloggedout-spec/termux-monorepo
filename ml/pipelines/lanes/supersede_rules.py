"""Session pulses and stale keep-alive parents are SUPERSEDE, not WAIT."""
from __future__ import annotations
from typing import Any, Mapping

def should_supersede(pr: Mapping[str, Any]) -> bool:
    if pr.get("supersede"):
        return True
    title = str(pr.get("title") or "").lower()
    if "session pulse" in title or "lane-matrix" in title and "session" in title:
        return True
    if pr.get("keep_alive_parent") and pr.get("stale_base"):
        return True
    return False
