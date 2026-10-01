"""Parse operator intent from Issue #175 body markers. No pulse comments."""
from __future__ import annotations

import re
from typing import Any

LANE_RE = re.compile(r"\b(EXTRACT|CANDIDATE|NEED_EVIDENCE|SUPERSEDE)\b")
INVALID_RE = re.compile(r"\b(HOLD|WAIT|OBSERVE)\b")


def extract_lanes(body: str) -> list[str]:
    return LANE_RE.findall(body or "")


def invalid_parking(body: str) -> list[str]:
    return INVALID_RE.findall(body or "")


def next_actions(body: str) -> list[str]:
    lines = []
    grab = False
    for raw in (body or "").splitlines():
        if "Next OPERATOR actions" in raw:
            grab = True
            continue
        if grab:
            if raw.startswith("#"):
                break
            text = raw.strip(" -*	")
            if text:
                lines.append(text)
    return lines


def summarize_intent(body: str) -> dict[str, Any]:
    return {
        "lanes_mentioned": sorted(set(extract_lanes(body))),
        "invalid_parking": sorted(set(invalid_parking(body))),
        "next": next_actions(body)[:8],
        "pulse_comments_allowed": False,
    }
