"""Peer / agent drift detector. Concurrent agents are not idle parking."""
from __future__ import annotations

from typing import Any

from ml.pipelines.command_center.constants import MINESWEEPER_FAMILY
from ml.pipelines.lanes.minesweeper_rules import is_bot_author, minesweeper_title


def overlapping(a: dict[str, Any], b: dict[str, Any]) -> bool:
    if int(a.get("number") or 0) == int(b.get("number") or 0):
        return False
    files_a = set(a.get("files") or [])
    files_b = set(b.get("files") or [])
    if files_a and files_b and files_a & files_b:
        return True
    prefix_a = str(a.get("head_ref") or a.get("head") or "")[:24]
    prefix_b = str(b.get("head_ref") or b.get("head") or "")[:24]
    return bool(prefix_a and prefix_a == prefix_b)


def drift_report(prs: list[dict[str, Any]]) -> dict[str, Any]:
    mines = []
    bots = []
    for pr in prs:
        n = int(pr.get("number") or 0)
        if n in MINESWEEPER_FAMILY or minesweeper_title(pr) or is_bot_author(pr):
            mines.append(n)
        if is_bot_author(pr):
            bots.append(n)
    collisions = []
    for i, a in enumerate(prs):
        for b in prs[i + 1 :]:
            if overlapping(a, b):
                collisions.append((int(a["number"]), int(b["number"])))
    return {
        "minesweeper": mines,
        "bots": bots,
        "collisions": collisions,
        "rule": "Do not overwrite peer branches. EXTRACT, never force-push.",
    }
