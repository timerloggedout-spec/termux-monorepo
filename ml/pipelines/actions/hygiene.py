"""Hygiene + portability gate aliases."""
from __future__ import annotations

from ml.pipelines.actions.named_jobs import match_repo_gate


def is_hygiene(name: str) -> bool:
    return match_repo_gate(name) or "portability" in (name or "").lower()
