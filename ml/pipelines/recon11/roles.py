"""SHA roles for the 2026-10-14 probe. Observer tip is not a promote."""
from __future__ import annotations

VERSION = "0.11.0"
PRODUCT_SHA = "8d36f149214f4a147932188bc424e7c29b8de444"
OBSERVER_TIP = "3e64bc65028a6d174059fa9a5c26693f4c58dd4e"
OPEN_PRS_OBSERVED = 219
BOARD_LANES = {
    "CANDIDATE": 61,
    "EXTRACT": 10,
    "NEED_EVIDENCE": 65,
    "SUPERSEDE": 83,
}
PREDECESSOR_VERSION = "0.10.0"
AGENT = "Grok (Administrator)"
PRODUCT_NOTE = "last recorded dual-gate in command-center constants; do not restamp from this probe"
OBSERVER_NOTE = "CRG-10 context backfill already on master; not a product promote"
CATALOG_NOTE = "priority subset only; lane-matrix writer remains the board SSOT"
BOARD_NOTE = "generated board 2026-10-14T17:06:24Z counted 219 open PRs; tip moved after that sweep"
