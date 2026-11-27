"""Context integration: bounded working set with durable evidence references."""
from __future__ import annotations
from typing import Any, Iterable, Mapping
from .signals import normalize_signals

def build_context(signals: Iterable[Mapping[str, Any]], episodes: Iterable[Mapping[str, Any]] = (),
                  max_items: int = 64) -> dict[str, Any]:
    """Build a bounded signal context while retaining unique episode evidence refs."""
    if isinstance(max_items, bool) or not isinstance(max_items, int) or max_items < 1:
        raise ValueError("max_items must be a positive integer")
    normalized = normalize_signals(signals)
    episode_list = [dict(item) for item in episodes]
    evidence_refs: list[str] = []
    for episode in episode_list:
        for ref in episode.get("evidence_refs", []):
            value = str(ref).strip()
            if value and value not in evidence_refs:
                evidence_refs.append(value)
    return {
        "schema_version": "brain.context.v1",
        "signals": normalized[-max_items:],
        "episode_ids": [str(item.get("episode_id", "")).strip() for item in episode_list if str(item.get("episode_id", "")).strip()],
        "evidence_refs": evidence_refs,
        "truncated_signal_count": max(0, len(normalized) - max_items),
    }
