"""SHA roles for the 2026-10-12 cut. Observer tip is not a promote."""
from __future__ import annotations

VERSION = "0.10.0"
PRODUCT_SHA = "8d36f149214f4a147932188bc424e7c29b8de444"
OBSERVER_TIP = "458ff77882e48075815c68aa29a0661be8aa383d"
OPEN_PRS_OBSERVED = 210
BOARD_LANES = {
    "CANDIDATE": 0,
    "EXTRACT": 79,
    "NEED_EVIDENCE": 130,
    "SUPERSEDE": 1,
}
PREDECESSOR_VERSION = "0.9.0"
AGENT = "Grok (Administrator)"
PRODUCT_NOTE = "last recorded dual-gate in command-center constants; do not restamp from this cut"
OBSERVER_NOTE = "context relationship index reconcile on master; not a product promote"
CATALOG_NOTE = "priority subset of the 210-PR board, not the lane-matrix writer"
