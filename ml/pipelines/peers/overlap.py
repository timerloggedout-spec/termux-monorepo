"""Title-token overlap heuristic for minesweeper titles."""
from __future__ import annotations

TOKENS = ("palette", "bolt", "linguist", "sentinel", "minesweeper")


def title_overlap(title: str) -> bool:
    blob = (title or "").lower()
    return any(tok in blob for tok in TOKENS)
