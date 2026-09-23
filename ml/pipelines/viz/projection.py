"""JSON projection consumed by operator dashboards. No secrets."""
from __future__ import annotations
from typing import Any, Mapping
from .cctv import cctv
from .matrix_view import matrix_rows

def project(snapshot: Mapping[str, Any], lanes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "master_sha": snapshot.get("master_sha"),
        "issue": snapshot.get("issue", 175),
        "captured_at": snapshot.get("captured_at"),
        "cctv": cctv(lanes),
        "rows": matrix_rows(lanes),
    }
