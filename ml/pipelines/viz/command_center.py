"""Mermaid + JSON projection of the repository command center."""
from __future__ import annotations

from typing import Any

from ml.pipelines.command_center.hub import emit_command_center
from ml.pipelines.keepalive_dag import operator_dag, render_mermaid


def emit_center(snapshot: dict[str, Any]) -> dict[str, Any]:
    center = emit_command_center(snapshot)
    center["mermaid"] = render_mermaid(operator_dag())
    return center
