"""Lane rules for the 2026-10-14 probe. Vocab v2 only.

Leaves recon10 frozen. Adds two corrections:
- "live status recon" and "status refresh" titles are session pulses.
- Jules peers opened after the v0.10.0 cut stay EXTRACT and are not overwritten.
"""
from __future__ import annotations

from ml.pipelines.recon10.rules import (
    CODERABBIT_FILE_BUDGET,
    INVALID_PARKING,
    JULES_LOGINS,
    VALID_LANES,
    classify_open_pr as classify_v10,
)

EXTRA_MINESWEEPER = frozenset({1221, 1224, 1225})
PULSE_MARKERS = ("live status recon", "status refresh")


def classify_open_pr(*, number: int, base: str, login: str, title: str, draft: bool = False) -> tuple[str, tuple[str, ...], str]:
    """Return lane, reasons, action. Never emit HOLD/WAIT/OBSERVE."""
    lowered = title.lower()
    if any(marker in lowered for marker in PULSE_MARKERS):
        reasons: list[str] = []
        if draft:
            reasons.append("draft")
        reasons.append("session-pulse")
        return "SUPERSEDE", tuple(reasons), "supersede-generated-board-is-ssot"
    if number in EXTRA_MINESWEEPER or login in JULES_LOGINS:
        reasons = ["minesweeper-peer"]
        if draft:
            reasons.insert(0, "draft")
        return "EXTRACT", tuple(reasons), "do-not-overwrite-peer"
    return classify_v10(number=number, base=base, login=login, title=title, draft=draft)


__all__ = [
    "CODERABBIT_FILE_BUDGET",
    "EXTRA_MINESWEEPER",
    "INVALID_PARKING",
    "VALID_LANES",
    "classify_open_pr",
]
