"""Slim keep-alive ML pipeline package (AR-23 / MLP-KEEP-001)."""

from .keepalive_dag import DagSpec, default_dag, render_mermaid, validate_dag

__all__ = ["DagSpec", "default_dag", "render_mermaid", "validate_dag"]
