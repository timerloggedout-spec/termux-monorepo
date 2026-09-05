"""Eval envelope contract. Digest required."""
from __future__ import annotations

from typing import Any

from ml_pipelines.contracts import CONTRACT, PipelineError, digest


def wrap(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    if kind not in {"leaderboard", "minesweeper", "matrix", "health"}:
        raise PipelineError(f"unknown eval kind: {kind}")
    envelope = {"contract": CONTRACT, "kind": kind, "payload": payload}
    envelope["digest"] = digest(envelope)
    return envelope
