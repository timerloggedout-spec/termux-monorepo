"""Actions skip-reason catalog. Quota is a comment, not silent skip."""
from __future__ import annotations

REASONS = {
    "quota": "Actions quota exhausted — leave skip-reason comment",
    "vercel_hobby": "Vercel hobby rate-limit is non-gate (#772)",
    "dirty": "mergeable_state=dirty blocks promote until rebase",
    "wrong_base": "wrong-base (master-staging / vibe) — never retarget to master",
    "wholesale": "ml-wholesale-no-go — extract slim slice only",
    "minesweeper": "peer/bot overlap — EXTRACT, do not overwrite",
    "observer": "help-wanted / lane-matrix sweep is observer, not promote",
    "combined_status": "combined commit status is not dual-gate",
}


def reason(key: str) -> str:
    if key not in REASONS:
        raise KeyError(key)
    return REASONS[key]


def is_non_gate_skip(key: str) -> bool:
    return key in {"quota", "vercel_hobby", "combined_status", "observer"}
