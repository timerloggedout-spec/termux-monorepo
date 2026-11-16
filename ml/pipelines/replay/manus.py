"""Manus computer-replay is EXTRACT-only (#265 / #503). Names, not payloads."""
from __future__ import annotations

MANUS_ISSUES = (265, 503)


def is_manus_lane(number: int) -> bool:
    return int(number) in MANUS_ISSUES
