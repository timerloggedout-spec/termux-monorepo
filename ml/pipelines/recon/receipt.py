"""Compose the MLP-KEEP-006 receipt. Pure data in, JSON-ready dict out."""
from __future__ import annotations

from typing import Any

from ml.pipelines.recon.actions import next_actions
from ml.pipelines.recon.catalog import (
    CODE_OBSERVER_SHA,
    CODE_PRODUCT_SHA,
    CONTRACT_VERSION,
    DUAL_GATE,
    DUAL_GATE_SHA,
    HUB_ISSUE,
    LANE_BOARD_AT,
    LANE_BOARD_SHA,
    LIVE_MASTER_CLASS,
    LIVE_MASTER_SHA,
    RECORDED_TIP,
)
from ml.pipelines.recon.peers import protected_numbers
from ml.pipelines.recon.sha import same_commit, tip_relation
from ml.pipelines.recon.version_audit import mismatch

def build_receipt(*, init_version: str, file_version: str = CONTRACT_VERSION) -> dict[str, Any]:
    relation = tip_relation(RECORDED_TIP, LIVE_MASTER_SHA)
    return {
        "kind": "mlp-keep-006-recon",
        "issue": HUB_ISSUE,
        "contract_version": file_version,
        "init_version": init_version,
        "version_mismatch": mismatch(init_version, file_version),
        "recorded_tip": RECORDED_TIP,
        "code_product_sha": CODE_PRODUCT_SHA,
        "code_observer_sha": CODE_OBSERVER_SHA,
        "lane_board_sha": LANE_BOARD_SHA,
        "lane_board_at": LANE_BOARD_AT,
        "live_master_sha": LIVE_MASTER_SHA,
        "live_master_class": LIVE_MASTER_CLASS,
        "dual_gate_sha": DUAL_GATE_SHA,
        "dual_gate": dict(DUAL_GATE),
        "tip_relation": relation,
        "recorded_matches_live": same_commit(RECORDED_TIP, LIVE_MASTER_SHA),
        "recorded_matches_product": same_commit(RECORDED_TIP, CODE_PRODUCT_SHA),
        "live_matches_dual_gate": same_commit(LIVE_MASTER_SHA, DUAL_GATE_SHA),
        "protected_peers": list(protected_numbers()),
        "next_actions": next_actions(),
        "coderabbit_advisory_max_files": 100,
        "coderabbit_non_gate": True,
        "secrets": "names-only",
    }
