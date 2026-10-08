"""Frozen observations from the 2026-10-08 recon. Not a second policy file."""
from __future__ import annotations

# Issue #175 body still names this September product tip.
RECORDED_TIP = "8424a50c"
# command_center.constants — left untouched on purpose.
CODE_PRODUCT_SHA = "8d36f149214f4a147932188bc424e7c29b8de444"
CODE_OBSERVER_SHA = "40d8c35dcfffe3e1a963e88df386e65ad23fb5df"
# docs/ops/generated/lane-matrix-status.md at recon time.
LANE_BOARD_SHA = "664092d43fac8dddcd8cb8a5f2679ab843620d3c"
LANE_BOARD_AT = "2026-10-07T23:02:33Z"
# Live master when this ledger was cut. A sweep receipt, not a product promote.
LIVE_MASTER_SHA = "000c9391ebdb4decb6669cfc8bd4709f11d55e7d"
LIVE_MASTER_CLASS = "sweep-receipt"
# Last dual-gate SUCCESS observed on master before that receipt.
DUAL_GATE_SHA = "68fd8608e960ca6db384266cb7941c567aadae6d"
DUAL_GATE = {
    "repo-gate": "success",
    "repo-gate-run": "37722000150",
    "termux-smoke": "success",
    "termux-smoke-run": "37722000126",
}
CONTRACT_VERSION = "0.6.0"
HUB_ISSUE = 175
VALID_LANES = ("EXTRACT", "CANDIDATE", "NEED_EVIDENCE", "SUPERSEDE")
INVALID_PARKING = ("HOLD", "WAIT", "OBSERVE")
# Advisory CodeRabbit window from the operator matrix. Not a promote gate.
CODERABBIT_ADVISORY_MAX = 100
# Bot diffs above this are minesweeper EXTRACT (lanes/minesweeper_rules.py).
BOT_EXTRACT_THRESHOLD = 40
WHOLESALE_NO_GO = (48, 432, 549, 601, 682, 746, 787, 817)
STAGING_ONLY = (48, 788)
PROTECTED_PEERS = (
    {"number": 65, "lane": "EXTRACT", "why": "palette heartbeat — do not overwrite"},
    {"number": 140, "lane": "EXTRACT", "why": "minesweeper family"},
    {"number": 481, "lane": "EXTRACT", "why": "Jules handoff observability"},
    {"number": 630, "lane": "EXTRACT", "why": "Jules dashboard fallback — peer branch"},
    {"number": 672, "lane": "EXTRACT", "why": "help-wanted tribute minesweeper"},
    {"number": 680, "lane": "EXTRACT", "why": "Bolt live catalog — peer branch"},
    {"number": 750, "lane": "EXTRACT", "why": "Jules fallback imports"},
    {"number": 884, "lane": "EXTRACT", "why": "Jules Linguist symbol-map optimization"},
    {"number": 1151, "lane": "EXTRACT", "why": "palette UX — minesweeper-title"},
    {"number": 1169, "lane": "EXTRACT", "why": "Jules lane-consolidation audit"},
    {"number": 1171, "lane": "EXTRACT", "why": "Jules Linguist CedrLang prefilter"},
)
