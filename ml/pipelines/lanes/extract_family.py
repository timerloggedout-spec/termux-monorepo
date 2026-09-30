"""Known EXTRACT families. Never wholesale-merge."""
from __future__ import annotations

from ml.pipelines.command_center.constants import MEGA_NO_GO, MINESWEEPER_FAMILY, STAGING_ONLY


def family_of(number: int) -> str:
    n = int(number)
    if n in STAGING_ONLY:
        return "staging-only"
    if n in MEGA_NO_GO:
        return "ml-wholesale"
    if n in MINESWEEPER_FAMILY:
        return "minesweeper"
    return "other"


def must_extract(number: int) -> bool:
    return family_of(number) in {"ml-wholesale", "minesweeper"}
