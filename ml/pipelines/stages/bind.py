"""DAG stage: bind dual-gate named jobs to the snapshot SHA."""
from __future__ import annotations

from typing import Any

from ml.pipelines.command_center.bind import bind


def stage_bind(context: dict[str, Any]) -> None:
    snapshot = context.get("snapshot") or {}
    context["bind"] = bind(str(snapshot.get("master_sha") or ""), context.get("checks") or [])
