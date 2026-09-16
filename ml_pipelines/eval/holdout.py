"""Deterministic holdout split by PR number. No shuffle seed surprises."""
from __future__ import annotations

from typing import Any


def split(rows: list[dict[str, Any]], mod: int = 5) -> dict[str, list[dict[str, Any]]]:
    train = [row for row in rows if int(row.get("number") or 0) % mod]
    hold = [row for row in rows if int(row.get("number") or 0) % mod == 0]
    return {"train": train, "holdout": hold}
