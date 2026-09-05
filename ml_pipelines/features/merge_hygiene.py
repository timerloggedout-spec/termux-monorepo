"""Score PR merge hygiene without claiming merge authority."""
from __future__ import annotations

from typing import Any


def merge_hygiene_score(pr: dict[str, Any]) -> dict[str, Any]:
    mergeable = pr.get("mergeable")
    state = pr.get("mergeStateStatus")
    files = int(pr.get("changedFiles") or 0)
    dirty = mergeable == "CONFLICTING" or state == "DIRTY"
    clean = mergeable == "MERGEABLE" and state in {"CLEAN", "UNSTABLE", "HAS_HOOKS"}
    score = 0.0
    if clean:
        score += 0.7
    if state == "CLEAN":
        score += 0.2
    if files and files <= 12:
        score += 0.1
    if dirty:
        score = min(score, 0.15)
    if files >= 80:
        score = min(score, 0.35)
    return {
        "number": pr.get("number"),
        "score": round(score, 3),
        "dirty": dirty,
        "clean": clean,
        "changed_files": files,
    }
