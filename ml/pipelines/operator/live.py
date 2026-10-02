"""Live 2026-09-26 product SHA facts. Observer tip is not promote."""
from __future__ import annotations

PRODUCT_SHA = "8d36f149214f4a147932188bc424e7c29b8de444"
OBSERVER_TIP = "40d8c35dcfffe3e1a963e88df386e65ad23fb5df"
DUAL_GATE = {
    "repo_gate_run": "36268169372",
    "termux_smoke_run": "36268169447",
    "conclusion": "success",
}


def is_product_sha(sha: str) -> bool:
    return str(sha or "").startswith(PRODUCT_SHA[:12])


def is_observer_tip(sha: str) -> bool:
    return str(sha or "").startswith(OBSERVER_TIP[:12])
