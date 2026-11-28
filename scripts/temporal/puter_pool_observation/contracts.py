"""Serializable correlation contract shared by Temporal workflow and activities."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PuterPoolObservationInput:
    task_or_entry_ref: str = ""
    doe_run_id: str = ""
    workflow_run_id: str = ""
    run_attempt: int = 1
    interval_seconds: int = 300
