"""Termux smoke aliases."""
from __future__ import annotations

from ml.pipelines.actions.named_jobs import match_smoke


def is_smoke(name: str) -> bool:
    return match_smoke(name)
