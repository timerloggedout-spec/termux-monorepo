"""Read-only recon stamp."""
from __future__ import annotations

from collections import Counter

from ml.pipelines.recon08.catalog import all_observations
from ml.pipelines.recon08.locks import LOCKS
from ml.pipelines.recon08.roles import (
    AGENT,
    OBSERVER_NOTE,
    OBSERVER_TIP,
    OPEN_PRS_OBSERVED,
    PREDECESSOR_PR,
    PRODUCT_NOTE,
    PRODUCT_SHA,
    VERSION,
)


def stamp_report() -> dict[str, object]:
    rows = all_observations()
    counts = Counter(row.lane for row in rows)
    return {
        "version": VERSION,
        "issue": 175,
        "agent": AGENT,
        "writes": False,
        "product_sha": PRODUCT_SHA,
        "product_note": PRODUCT_NOTE,
        "observer_tip": OBSERVER_TIP,
        "observer_note": OBSERVER_NOTE,
        "observer_tip_promotable": False,
        "open_prs_observed": OPEN_PRS_OBSERVED,
        "catalog_rows": len(rows),
        "catalog_is_full_board": False,
        "predecessor_pr": PREDECESSOR_PR,
        "lane_counts": dict(sorted(counts.items())),
        "locks": LOCKS,
    }
