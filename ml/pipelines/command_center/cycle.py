"""RECON → IMPLEMENT → WAIT → VALIDATE → REPEAT. Adaptive wait is concurrent work."""
from __future__ import annotations

STAGES = ("RECON", "IMPLEMENT", "WAIT", "VALIDATE", "REPEAT")


def next_stage(current: str) -> str:
    current = current.upper()
    if current not in STAGES:
        raise ValueError(current)
    if current == "REPEAT":
        return "RECON"
    return STAGES[STAGES.index(current) + 1]


def wait_is_idle(current: str) -> bool:
    """WAIT is a stage, not idle parking. Concurrent non-conflicting work continues."""
    return False if current == "WAIT" else False
