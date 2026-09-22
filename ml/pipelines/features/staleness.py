"""stale_base is a WAIT signal when dual-gate is green, never a promote by itself."""
from __future__ import annotations
from typing import Any, Mapping

def flag(pr: Mapping[str, Any]) -> bool:
    return bool(pr.get("stale_base"))
