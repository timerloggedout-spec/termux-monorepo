"""SHA roles for the 2026-10-19 probe. Observer tip is not a promote."""
from __future__ import annotations

VERSION = "0.11.0"
PRODUCT_SHA = "8d36f149214f4a147932188bc424e7c29b8de444"
OBSERVER_TIP = "fd8c30ace52de915cf50fc3f18a070abf462cc89"
OPEN_PRS_OBSERVED = 173
BOARD_LANES = {
    "CANDIDATE": 0,
    "EXTRACT": 52,
    "NEED_EVIDENCE": 120,
    "SUPERSEDE": 1,
}
PREDECESSOR_VERSION = "0.10.0"
AGENT = "Grok (Administrator)"
PRODUCT_NOTE = "command-center constant stays 8d36f149; do not restamp from this cut"
OBSERVER_NOTE = "docs index refresh on master; not a product promote. Recent push repo-gate and termux-smoke succeeded on daa6be60 before this tip"
CATALOG_NOTE = "priority subset of the live open board, not the lane-matrix writer. Closed wholesale ML PRs stay in locks, not in this catalog"
