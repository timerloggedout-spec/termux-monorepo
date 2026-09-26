"""Nested trail from a card id up to entry."""
from __future__ import annotations

from ml.pipelines.icm.cards import CARDS, card_by_id


def trail(card_id: str) -> list[str]:
    out: list[str] = []
    current = card_id
    seen: set[str] = set()
    while current and current not in seen:
        seen.add(current)
        card = card_by_id(current)
        out.append(card["id"])
        current = card.get("parent")
    return list(reversed(out))


def children(card_id: str) -> list[str]:
    return [c["id"] for c in CARDS if c.get("parent") == card_id]
