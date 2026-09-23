"""types: Canonical records for the keep-alive DAG."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class Lane(str, Enum):
    PROMOTE = "promote"
    WAIT = "wait"
    HOLD = "hold"
    EXTRACT = "extract"
    OBSERVE = "observe"
    SUPERSEDE = "supersede"


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    OK = "ok"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class StageResult:
    stage_id: str
    status: StageStatus
    artifacts: Mapping[str, Any] = field(default_factory=dict)
    notes: tuple[str, ...] = ()
