"""Resolve the newest keep-alive session fixture. No network."""
from __future__ import annotations

from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def session_paths() -> list[Path]:
    return sorted(FIXTURES.glob("session_*.json"))


def latest_session_path() -> Path:
    paths = session_paths()
    if not paths:
        raise FileNotFoundError("no session_*.json fixtures")
    return paths[-1]
