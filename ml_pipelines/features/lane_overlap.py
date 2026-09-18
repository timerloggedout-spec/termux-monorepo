"""Detect overlapping Jules/agent lanes from titles and head refs."""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from ml_pipelines.minesweeper.lanes import LANE_PATTERNS


def cluster(prs: list[dict[str, Any]]) -> dict[str, list[int]]:
    buckets: dict[str, list[int]] = defaultdict(list)
    for pr in prs:
        hay = f"{pr.get('title') or ''} {pr.get('headRefName') or ''}"
        matched = False
        for name, _label, pattern in LANE_PATTERNS:
            if re.search(pattern, hay):
                buckets[name].append(int(pr["number"]))
                matched = True
        if not matched:
            buckets["unclassified"].append(int(pr["number"]))
    return {key: sorted(set(vals)) for key, vals in buckets.items()}
