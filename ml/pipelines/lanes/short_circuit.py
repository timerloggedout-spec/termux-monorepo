"""Lane short-circuit before PROMOTE. EXTRACT never auto-promotes."""
from __future__ import annotations

from ml.pipelines.lanes.vocab import Lane


def may_promote(lane: Lane) -> bool:
    return lane is Lane.CANDIDATE
