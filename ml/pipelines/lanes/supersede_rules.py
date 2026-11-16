"""SUPERSEDE classifiers: session pulses, stamps, ancient no-auto."""
from __future__ import annotations

from typing import Any

PULSE_TOKENS = (
    "ops(session)",
    "ops(skills): stamp",
    "lane-matrix",
    "pulse",
    "live status refresh",
)


def is_session_pulse(pr: dict[str, Any]) -> bool:
    title = str(pr.get("title") or "").lower()
    return any(token in title for token in PULSE_TOKENS)


def is_ancient(pr: dict[str, Any], days: float = 40.0) -> bool:
    return float(pr.get("age_days") or 0) >= days


def should_supersede(pr: dict[str, Any]) -> bool:
    return is_session_pulse(pr) or (is_ancient(pr) and not pr.get("product"))
