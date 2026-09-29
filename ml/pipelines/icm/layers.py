"""ICM layers: orientation → routing → evidence → product."""
from __future__ import annotations

LAYERS = ("orientation", "routing", "evidence", "product")


def layer_of(card_id: str) -> str:
    mapping = {
        "entry": "orientation",
        "icm": "routing",
        "skills": "routing",
        "gate": "evidence",
        "lane": "evidence",
        "board": "evidence",
        "hub": "evidence",
        "ml": "product",
        "center": "product",
        "ml-skill": "routing",
        "cctv-skill": "routing",
    }
    return mapping.get(card_id, "routing")
