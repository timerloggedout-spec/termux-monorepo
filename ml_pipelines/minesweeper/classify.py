"""Classify one PR into a minesweeper disposition."""
from __future__ import annotations

import re
from typing import Any

from .lanes import LANE_PATTERNS

NO_GO_TITLES = (
    "vibe dispatch",
    "NO-GO wholesale",
    "wholesale merge",
)


def classify_pr(pr: dict[str, Any], lane_size: int = 1) -> dict[str, Any]:
    title = str(pr.get("title") or "")
    hay = f"{title} {pr.get('headRefName') or ''}"
    lane = "unclassified"
    for name, _label, pattern in LANE_PATTERNS:
        if re.search(pattern, hay):
            lane = name
            break
    mergeable = pr.get("mergeable")
    state = pr.get("mergeStateStatus")
    files = int(pr.get("changedFiles") or 0)
    if any(token.lower() in title.lower() for token in NO_GO_TITLES):
        disposition = "NO_GO"
    elif mergeable == "CONFLICTING" or state == "DIRTY":
        disposition = "DIRTY_HOLD"
    elif lane != "unclassified" and lane_size >= 3 and files <= 12:
        disposition = "LANE_DUPLICATE"
    elif mergeable == "MERGEABLE" and state == "CLEAN" and files <= 20:
        disposition = "MERGE_CANDIDATE"
    elif mergeable == "MERGEABLE" and files <= 12:
        disposition = "EXTRACT_CANDIDATE"
    elif files >= 80:
        disposition = "MEGA_REVIEW"
    else:
        disposition = "HOLD"
    return {
        "number": pr.get("number"),
        "lane": lane,
        "disposition": disposition,
        "mergeable": mergeable,
        "state": state,
        "changed_files": files,
        "title": title,
        "author": pr.get("author"),
        "url": pr.get("url"),
    }
