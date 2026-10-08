"""Ranked next actions. Product work, not a session-stamp comment."""
from __future__ import annotations

from typing import Any

from ml.pipelines.recon.vocab import assert_lane

def next_actions() -> list[dict[str, Any]]:
    rows = [
        {
            "p": 0,
            "lane": "CANDIDATE",
            "item": "Keep repo-gate + termux-smoke green on the dual-gate SHA",
            "status": "SUCCESS on 68fd8608 (runs 37722000150 / 37722000126)",
        },
        {
            "p": 0,
            "lane": "SUPERSEDE",
            "item": "Do not promote sweep receipt 000c9391 as a product SHA",
            "status": "accountability commit only",
        },
        {
            "p": 0,
            "lane": "EXTRACT",
            "item": "Wholesale ML family and #48",
            "status": "never merge #48 #432 #549 #601 #682 #746 #787 #817 whole",
        },
        {
            "p": 0,
            "lane": "EXTRACT",
            "item": "Minesweeper peers",
            "status": "do not overwrite #630 #65 #680 #884 #1151 #1169 #1171",
        },
        {
            "p": 1,
            "lane": "CANDIDATE",
            "item": "Align ml.pipelines.__version__ with VERSION",
            "status": "0.5.0 hardcoded vs VERSION 0.6.0 — fixed by reading VERSION",
        },
        {
            "p": 1,
            "lane": "NEED_EVIDENCE",
            "item": "#806 evaluation lanes and #809 GAMUT",
            "status": "rebase as small slices; stale bases",
        },
        {
            "p": 1,
            "lane": "CANDIDATE",
            "item": "#184 credential inventory",
            "status": "names only; never commit values",
        },
        {
            "p": 2,
            "lane": "NEED_EVIDENCE",
            "item": "Edit Issue #175 body tip when intent changes",
            "status": "recorded tip 8424a50c is behind; do not pulse-comment",
        },
        {
            "p": 3,
            "lane": "NEED_EVIDENCE",
            "item": "#788 TER-15 and #48 TER-71 remainder",
            "status": "stay on master-staging; never retarget to master",
        },
    ]
    for row in rows:
        assert_lane(row["lane"])
    return rows
