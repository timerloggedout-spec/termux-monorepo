"""errors: Typed failures; never leak secrets."""
from __future__ import annotations

class PipelineError(Exception):
    """Base pipeline error."""


class GateBlocked(PipelineError):
    """Dual-gate or minesweeper rule blocked a promote."""


class SchemaError(PipelineError):
    """Payload failed schema validation."""
