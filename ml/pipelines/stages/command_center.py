"""DAG stage: project command-center hub into context."""
from __future__ import annotations

from typing import Any

from ml.pipelines.command_center.hub import emit_hub


def stage_command_center(context: dict[str, Any]) -> None:
    snapshot = context.get("snapshot") or {}
    context["hub"] = emit_hub(snapshot, context.get("checks") or [])
