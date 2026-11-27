"""Context integration: bounded working set with durable evidence references."""
from __future__ import annotations
from typing import Any, Iterable, Mapping
from .signals import normalize_signals

def build_context(signals: Iterable[Mapping[str, Any]], episodes: Iterable[Mapping[str, Any]] = (),
                  max_items: int = 64, prioritized_ids: Iterable[str] = ()) -> dict[str, Any]:
    """Build a bounded signal context while retaining unique episode evidence refs."""
    if isinstance(max_items, bool) or not isinstance(max_items, int) or max_items < 1:
        raise ValueError("max_items must be a positive integer")
    normalized = normalize_signals(signals)
    by_id = {item["signal_id"]: item for item in normalized}
    focused_ids = []
    for raw_id in prioritized_ids:
        signal_id = str(raw_id).strip()
        if not signal_id:
            raise ValueError("prioritized signal IDs must be non-empty")
        if signal_id not in by_id:
            raise ValueError(f"prioritized signal is absent from context input: {signal_id}")
        if signal_id not in focused_ids:
            focused_ids.append(signal_id)
    focused_ids = focused_ids[:max_items]
    focused = [by_id[signal_id] for signal_id in focused_ids]
    focused_set = set(focused_ids)
    remaining = [item for item in normalized if item["signal_id"] not in focused_set]
    recent_slots = max_items - len(focused)
    selected = focused + (remaining[-recent_slots:] if recent_slots else [])
    selected.sort(key=lambda item: (item["sequence"], item["signal_id"]))
    episode_list = [dict(item) for item in episodes]
    evidence_refs: list[str] = []
    for episode in episode_list:
        for ref in episode.get("evidence_refs", []):
            value = str(ref).strip()
            if value and value not in evidence_refs:
                evidence_refs.append(value)
    return {
        "schema_version": "brain.context.v1",
        "signals": selected,
        "episode_ids": [str(item.get("episode_id", "")).strip() for item in episode_list if str(item.get("episode_id", "")).strip()],
        "evidence_refs": evidence_refs,
        "truncated_signal_count": max(0, len(normalized) - len(selected)),
    }
