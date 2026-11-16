"""Pick the newest session fixture. Stdlib only."""
from __future__ import annotations

from pathlib import Path

FIX = Path(__file__).resolve().parents[1] / "fixtures"


def latest_session_path() -> Path:
    sessions = sorted(FIX.glob("session_*.json"))
    if not sessions:
        raise FileNotFoundError("no session_*.json fixtures")
    return sessions[-1]
