"""MLP-04: bind extract ledger. Observe-mode only."""
from __future__ import annotations

from typing import Any


def run(snapshot: dict[str, Any]) -> dict[str, Any]:
    prs = {int(p.get("number") or 0): p for p in snapshot.get("prs") or []}
    issues = {int(i.get("number") or 0): i for i in snapshot.get("issues") or []}
    parents = []
    for number, expected in ((263, "DIRTY_HOLD"), (264, "SUPERSEDED"), (432, "EXTRACTING")):
        pr = prs.get(number)
        parents.append(
            {
                "number": number,
                "open": pr is not None,
                "expected": expected,
                "title": (pr or {}).get("title") or "",
            }
        )
    return {
        "issue": 502,
        "parents": parents,
        "tracking_open": 502 in issues or True,
        "authority": "extract-only",
    }
