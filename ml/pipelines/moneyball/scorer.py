from __future__ import annotations

from typing import Any

from ml.pipelines.lanes.minesweeper_rules import minesweeper_extract
from ml.pipelines.moneyball.normalize import clamp
from ml.pipelines.moneyball.weights import STALE_CAP, WEIGHTS


def score(pr: dict[str, Any]) -> float:
    points = 0.0
    base = (pr.get("base") or {}).get("ref") if isinstance(pr.get("base"), dict) else pr.get("base")
    gates = pr.get("gates") or {}
    if gates.get("repo-gate") == "success" and gates.get("termux-smoke") == "success":
        points += WEIGHTS["dual_gate_green"]
    if base == "master":
        points += WEIGHTS["on_master_base"]
    if int(pr.get("changed_files") or 0) <= 100:
        points += WEIGHTS["files_under_100"]
    if pr.get("has_tests"):
        points += WEIGHTS["has_tests"]
    if float(pr.get("age_days") or 0) < 2:
        points += WEIGHTS["fresh"]
    if pr.get("draft"):
        points += WEIGHTS["draft"]
    if pr.get("mergeable_state") == "dirty":
        points += WEIGHTS["dirty"]
    if base and base != "master":
        points += WEIGHTS["wrong_base"]
    if minesweeper_extract(pr):
        points += WEIGHTS["minesweeper"]
    if pr.get("wholesale"):
        points += WEIGHTS["wholesale"]
    stale = int(float(pr.get("age_days") or 0))
    points += max(STALE_CAP, stale * WEIGHTS["stale_day"])
    return clamp(points)
