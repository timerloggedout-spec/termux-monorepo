"""Lane vocab v2. HOLD / WAIT / OBSERVE are invalid parking."""
from __future__ import annotations

from ml.pipelines.recon.catalog import INVALID_PARKING, VALID_LANES

def assert_lane(lane: str) -> str:
    if lane in INVALID_PARKING:
        raise ValueError(f"invalid parking: {lane}")
    if lane not in VALID_LANES:
        raise ValueError(f"unknown lane: {lane}")
    return lane
