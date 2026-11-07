"""Emit a command-center projection with explicit repository SSOT links."""
from __future__ import annotations

from typing import Any

from ml.pipelines.command_center.bind import bind
from ml.pipelines.command_center.board import board_from_snapshot
from ml.pipelines.command_center.constants import SSOT_PATHS, VERSION
from ml.pipelines.command_center.drift import drift_report
from ml.pipelines.command_center.extract import plan_many
from ml.pipelines.command_center.peers import active_peers
from ml.pipelines.command_center.receipt import receipt
from ml.pipelines.command_center.session import current
from ml.pipelines.operator.matrix import PRIORITY


def emit_command_center(snapshot: dict[str, Any], checks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    board = board_from_snapshot(snapshot)
    prs = snapshot.get("prs") or []
    sess = current()
    evidence = bind(str(snapshot.get("master_sha") or sess.product_sha), checks or [])
    payload = {
        "ssot": SSOT_PATHS,
        "version": VERSION,
        "session": sess.session_id,
        "board": board,
        "priority": PRIORITY,
        "drift": drift_report(prs),
        "peers": active_peers(prs),
        "extract_plan": plan_many(prs[:40]),
        "dual_gate": evidence,
    }
    return receipt("command-center", payload)
