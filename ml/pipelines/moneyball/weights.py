"""Transparent MoneyBall weights. Not a black box."""
from __future__ import annotations

WEIGHTS = {
    "dual_gate_green": 40,
    "on_master_base": 20,
    "files_under_100": 15,
    "has_tests": 10,
    "fresh": 10,
    "draft": -25,
    "dirty": -40,
    "wrong_base": -40,
    "minesweeper": -30,
    "wholesale": -50,
    "stale_day": -1,
}

STALE_CAP = -20
