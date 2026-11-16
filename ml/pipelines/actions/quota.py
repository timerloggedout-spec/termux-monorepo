"""Quota handling. Skip is a documented reason, never silent."""
from __future__ import annotations

from ml.pipelines.command_center.skip import reason


def skip_comment(kind: str = "quota") -> str:
    return f"skip-reason: {reason(kind)}"
