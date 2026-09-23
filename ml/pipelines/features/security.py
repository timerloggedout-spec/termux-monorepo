"""security_fix adds score; still requires dual-gate + clean mergeable."""
from __future__ import annotations
from typing import Any, Mapping

def flag(pr: Mapping[str, Any]) -> bool:
    return bool(pr.get("security"))
