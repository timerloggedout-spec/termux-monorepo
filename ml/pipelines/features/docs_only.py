"""docs_only pulses stay WAIT/SUPERSEDE; they do not replace keep-alive extracts."""
from __future__ import annotations
from typing import Any, Mapping

def flag(pr: Mapping[str, Any]) -> bool:
    return bool(pr.get("docs_only"))
