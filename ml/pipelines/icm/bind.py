"""Bind CCTV projection onto an ICM card."""
from __future__ import annotations

from typing import Any

from ml.pipelines.icm.cards import card_by_id
from ml.pipelines.viz.cctv import emit_cctv


def bind_cctv(snapshot: dict[str, Any], card_id: str = "center") -> dict[str, Any]:
    card = card_by_id(card_id)
    return {"card": card, "cctv": emit_cctv(snapshot)}
