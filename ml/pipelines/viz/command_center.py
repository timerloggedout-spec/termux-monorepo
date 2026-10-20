"""Mermaid + JSON projection of the operator hub."""
from __future__ import annotations

from typing import Any

from ml.pipelines.command_center.hub import emit_hub
from ml.pipelines.keepalive_dag import operator_dag, render_mermaid


def emit_center(snapshot: dict[str, Any]) -> dict[str, Any]:
    hub = emit_hub(snapshot)
    hub["mermaid"] = render_mermaid(operator_dag())
    return hub
