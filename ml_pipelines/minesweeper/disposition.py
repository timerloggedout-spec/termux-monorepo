"""Human-readable disposition copy. Not a merge command."""
from __future__ import annotations

COPY = {
    "NO_GO": "Do not merge wholesale. Extract only after a dedicated item.",
    "DIRTY_HOLD": "Conflicts vs master. Reconstruct a small green PR instead of API rebase.",
    "LANE_DUPLICATE": "Same lane already has multiple open PRs. Keep newest unique slice.",
    "MERGE_CANDIDATE": "Mergeable and clean. Still requires repo-gate + termux-smoke + review.",
    "EXTRACT_CANDIDATE": "Mergeable but checks unstable. Extract the unique files only.",
    "MEGA_REVIEW": "Too large for a thin PR. Component-by-component extract only.",
    "HOLD": "No merge recommendation. Observe and wait for evidence.",
}


def explain(disposition: str) -> str:
    return COPY.get(disposition, COPY["HOLD"])
