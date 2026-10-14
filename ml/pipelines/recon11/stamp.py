"""Read-only recon11 probe stamp."""
from __future__ import annotations

from collections import Counter

from ml.pipelines.recon11.catalog import all_observations
from ml.pipelines.recon11.connectors import connector_report
from ml.pipelines.recon11.locks import LOCKS
from ml.pipelines.recon11.roles import (
    AGENT,
    BOARD_LANES,
    BOARD_NOTE,
    CATALOG_NOTE,
    OBSERVER_NOTE,
    OBSERVER_TIP,
    OPEN_PRS_OBSERVED,
    PREDECESSOR_VERSION,
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
        "secrets": False,
        "product_sha": PRODUCT_SHA,
        "product_note": PRODUCT_NOTE,
        "observer_tip": OBSERVER_TIP,
        "observer_note": OBSERVER_NOTE,
        "observer_tip_promotable": False,
        "open_prs_observed": OPEN_PRS_OBSERVED,
        "board_lanes": dict(BOARD_LANES),
        "board_note": BOARD_NOTE,
        "catalog_rows": len(rows),
        "catalog_is_full_board": False,
        "catalog_note": CATALOG_NOTE,
        "predecessor_version": PREDECESSOR_VERSION,
        "lane_counts": dict(sorted(counts.items())),
        "locks": LOCKS,
        "connectors": connector_report(),
        "keep_pipelines": True,
        "command": "probe",
    }
