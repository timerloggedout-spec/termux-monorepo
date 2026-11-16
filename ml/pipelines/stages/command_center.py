"""DAG stage: project repository command-center state into context."""
from __future__ import annotations

from typing import Any

from ml.pipelines.command_center.hub import emit_command_center


def stage_command_center(context: dict[str, Any]) -> None:
    snapshot = context.get("snapshot") or {}
    context["command_center"] = emit_command_center(snapshot, context.get("checks") or [])
