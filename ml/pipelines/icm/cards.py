"""One verified component card before loading deeper source (docs/icm/CLAUDE.md)."""
from __future__ import annotations

from typing import Any

CARDS: list[dict[str, Any]] = [
    {"id": "entry", "title": "CLAUDE.md", "path": "CLAUDE.md", "parent": None},
    {"id": "icm", "title": "ICM routing", "path": "docs/icm/CLAUDE.md", "parent": "entry"},
    {"id": "gate", "title": "Dual gates", "path": "docs/ARCHW1Z-GATE.md", "parent": "entry"},
    {"id": "lane", "title": "Lane matrix policy", "path": "docs/ops/LANE-MATRIX.md", "parent": "entry"},
    {"id": "board", "title": "Generated board", "path": "docs/ops/generated/lane-matrix-status.md", "parent": "lane"},
    {"id": "ml", "title": "ML keep-alive", "path": "ml/pipelines/README.md", "parent": "entry"},
    {"id": "center", "title": "Command center", "path": "docs/ml/COMMAND-CENTER.md", "parent": "ml"},
    {"id": "skills", "title": "Skills inventory", "path": "docs/ops/SKILLS-INVENTORY.md", "parent": "entry"},
    {"id": "ml-skill", "title": "ml-pipeline-ops", "path": ".agents/skills/ml-pipeline-ops/SKILL.md", "parent": "skills"},
    {"id": "cctv-skill", "title": "icm-cctv-ops", "path": ".agents/skills/icm-cctv-ops/SKILL.md", "parent": "skills"},
    {"id": "hub", "title": "Issue #175 hub", "path": "https://github.com/timerloggedout-spec/termux-monorepo/issues/175", "parent": "entry"},
]


def card_by_id(card_id: str) -> dict[str, Any]:
    for card in CARDS:
        if card["id"] == card_id:
            return card
    raise KeyError(card_id)
