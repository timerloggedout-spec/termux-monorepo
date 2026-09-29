"""Resolve the newest session fixture without restamping LANE-MATRIX."""
from __future__ import annotations

from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def latest_session_path() -> Path:
    sessions = sorted(FIXTURE_DIR.glob("session_*.json"))
    if not sessions:
        raise FileNotFoundError("no session_*.json fixtures")
    return sessions[-1]
