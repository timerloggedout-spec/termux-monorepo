from __future__ import annotations

from ml.pipelines.keepalive_dag import DagSpec, render_mermaid, operator_dag


def dag_mermaid(spec: DagSpec | None = None) -> str:
    return render_mermaid(spec or operator_dag())
