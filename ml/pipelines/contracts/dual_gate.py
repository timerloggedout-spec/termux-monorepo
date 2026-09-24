"""Named dual-gate checks. Both must be SUCCESS."""
from __future__ import annotations

from typing import Mapping

HYGIENE = "hygiene + portability gate"
SMOKE = "agentic termux smoke"


def dual_gate_green(checks: Mapping[str, str]) -> bool:
    return checks.get(HYGIENE) == "success" and checks.get(SMOKE) == "success"
