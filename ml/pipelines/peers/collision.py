"""File-set collisions between open PRs."""
from __future__ import annotations

from typing import Any


def collisions_among(prs: list[dict[str, Any]]) -> list[tuple[int, int, list[str]]]:
    out: list[tuple[int, int, list[str]]] = []
    for i, a in enumerate(prs):
        fa = set(a.get("files") or [])
        if not fa:
            continue
        for b in prs[i + 1 :]:
            fb = set(b.get("files") or [])
            overlap = sorted(fa & fb)
            if overlap:
                out.append((int(a["number"]), int(b["number"]), overlap))
    return out
