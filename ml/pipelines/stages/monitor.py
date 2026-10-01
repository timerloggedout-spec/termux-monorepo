from __future__ import annotations

from typing import Any

from ml.pipelines.viz.projection import project


def stage_monitor(context: dict[str, Any]) -> None:
    context["cctv"] = project(context.get("snapshot") or {}, context.get("lanes") or [])
