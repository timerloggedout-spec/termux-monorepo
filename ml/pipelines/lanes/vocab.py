"""Lane vocabulary v2 (#836). HOLD/WAIT/OBSERVE are invalid parking."""
from __future__ import annotations

from enum import Enum


class Lane(str, Enum):
    EXTRACT = "EXTRACT"
    CANDIDATE = "CANDIDATE"
    NEED_EVIDENCE = "NEED_EVIDENCE"
    SUPERSEDE = "SUPERSEDE"


VALID_LANES = frozenset(item.value for item in Lane)
INVALID_PARKING = frozenset({"HOLD", "WAIT", "OBSERVE"})


def coerce(raw: str) -> Lane:
    if raw in INVALID_PARKING:
        raise ValueError(f"invalid parking lane: {raw}")
    return Lane(raw)
