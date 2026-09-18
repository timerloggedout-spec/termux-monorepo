"""Stdlib-only GitHub ML pipelines for termux-monorepo.

Observe-mode only. No network, no secrets, no issue-body-to-shell.
Implements: MLP-01 (Issue #213), MLP-02 (Issue #175), MLP-03 (minesweeper).
"""
from .contracts import CONTRACT, PipelineError, redacted
from .registry import PipelineRegistry

__all__ = ["CONTRACT", "PipelineError", "PipelineRegistry", "redacted"]
__version__ = "0.1.0"
