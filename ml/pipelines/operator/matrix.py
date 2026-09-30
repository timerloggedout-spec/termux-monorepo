"""Durable operator intent projection. Source of truth remains Issue #175 body."""
from __future__ import annotations

from typing import Any

# Live recon 2026-09-26T21:15Z. Dual-gate GREEN on 8d36f149 (product tip).
# Tip SHA 40d8c35d is help-wanted observer refresh — non-promote.
PRIORITY: list[dict[str, Any]] = [
    {"p": 0, "item": "Master dual-gate (repo-gate + termux-smoke)", "status": "GREEN on 8d36f149", "lane": "CANDIDATE"},
    {"p": 0, "item": "ML keep-alive MLP-KEEP-001 / AR-23", "status": "MERGED #843; this extract upgrades v0.6.0", "lane": "CANDIDATE"},
    {"p": 0, "item": "Mega PRs #48 / #682 / #432", "status": "EXTRACT — never wholesale", "lane": "EXTRACT"},
    {"p": 0, "item": "Minesweeper Jules family #630 #680 #65 #140", "status": "EXTRACT — do not overwrite peers", "lane": "EXTRACT"},
    {"p": 1, "item": "#809 GAMUT knowledge fabric (AR-22)", "status": "NEED_EVIDENCE — stale base 1ad58943", "lane": "NEED_EVIDENCE"},
    {"p": 1, "item": "#806 evaluation lanes (AR-21)", "status": "NEED_EVIDENCE — stale base 1ad58943", "lane": "NEED_EVIDENCE"},
    {"p": 1, "item": "#184 credential inventory", "status": "names-only; never commit values", "lane": "CANDIDATE"},
    {"p": 1, "item": "Vercel hobby rate-limit", "status": "NON-GATE #772", "lane": "SUPERSEDE"},
    {"p": 2, "item": "#265 Providers RE + Manus replay", "status": "EXTRACT", "lane": "EXTRACT"},
    {"p": 2, "item": "#838 foresight evidence spine", "status": "NEED_EVIDENCE stale base", "lane": "NEED_EVIDENCE"},
    {"p": 3, "item": "Linear TER-15 #788", "status": "NEED_EVIDENCE wrong-base master-staging", "lane": "NEED_EVIDENCE"},
    {"p": 3, "item": "Linear TER-71 remainder #48", "status": "EXTRACT; core on master via #805", "lane": "EXTRACT"},
]


def by_priority(level: int) -> list[dict[str, Any]]:
    return [row for row in PRIORITY if int(row["p"]) == level]


def lanes_in_matrix() -> set[str]:
    return {str(row["lane"]) for row in PRIORITY}
