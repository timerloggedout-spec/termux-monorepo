"""Static MoneyBall weights. Keep transparent; never hide a term."""
from __future__ import annotations

WEIGHTS = {
    "dual_gate_green": 5.0,
    "mergeable_clean": 3.0,
    "files_small": 1.5,
    "tests_present": 1.0,
    "security_fix": 2.0,
    "docs_only": 0.5,
    "stale_base": -2.0,
    "mergeable_dirty": -8.0,
    "mergeable_unstable": -1.0,
    "changed_files_over_40": -3.0,
    "minesweeper_overlap": -6.0,
    "ml_wholesale": -10.0,
    "jules_bot": -0.25,
    "master_staging_base": -4.0,
    "stacked_feature_base": -3.5,
    "hitl_risk": -5.0,
    "draft": -1.5,
    "replay_landed": 0.75,
}

THRESHOLDS = {"promote": 4.0, "wait": 0.0, "hold": -3.0}
FILES_SMALL = 8
FILES_OVER_40 = 40
FILES_WHOLESALE = 80
