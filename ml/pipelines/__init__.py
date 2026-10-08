"""ml.pipelines: Keep-alive ML DAG for operator ranking.

Implements: MLP-KEEP-001
``__version__`` tracks ``ml/pipelines/VERSION`` so the package cannot drift
from the v0.6.0 contract (it previously hardcoded 0.5.0).
"""
from __future__ import annotations

from pathlib import Path

def _version() -> str:
    path = Path(__file__).resolve().parent / "VERSION"
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise RuntimeError("ml/pipelines/VERSION is empty")
    return text

__version__ = _version()
