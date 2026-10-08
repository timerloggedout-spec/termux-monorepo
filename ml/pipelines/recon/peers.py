"""Peers this extract must not check out or overwrite."""
from __future__ import annotations

from ml.pipelines.recon.catalog import PROTECTED_PEERS, STAGING_ONLY, WHOLESALE_NO_GO

def protected_numbers() -> tuple[int, ...]:
    return tuple(int(row["number"]) for row in PROTECTED_PEERS)

def is_protected(number: int) -> bool:
    return int(number) in set(protected_numbers())

def is_wholesale(number: int) -> bool:
    return int(number) in WHOLESALE_NO_GO

def is_staging_only(number: int) -> bool:
    return int(number) in STAGING_ONLY

def retarget_allowed(number: int, base: str) -> bool:
    """master-staging PRs stay on master-staging."""
    if is_staging_only(number) and base == "master":
        return False
    return True
