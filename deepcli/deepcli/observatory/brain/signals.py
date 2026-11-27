"""Afferent signal intake: normalize, validate, deduplicate, and order observations."""
from __future__ import annotations
from typing import Any, Iterable, Mapping

_REQUIRED = {"signal_id", "source", "kind", "sequence", "confidence"}

def normalize_signals(signals: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Return unique signals in sequence order; conflicting identities are rejected."""
    by_id: dict[str, dict[str, Any]] = {}
    for raw in signals:
        missing = _REQUIRED - raw.keys()
        if missing:
            raise ValueError(f"signal missing fields: {sorted(missing)}")
        item = dict(raw)
        for key in ("signal_id", "source", "kind"):
            item[key] = str(item[key]).strip()
            if not item[key]:
                raise ValueError(f"signal {key} must be non-empty")
        if isinstance(item["sequence"], bool) or not isinstance(item["sequence"], int) or item["sequence"] < 0:
            raise ValueError("signal sequence must be a non-negative integer")
        confidence = float(item["confidence"])
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("signal confidence must be between 0 and 1")
        item["confidence"] = confidence
        previous = by_id.get(item["signal_id"])
        if previous is not None and previous != item:
            raise ValueError(f"conflicting duplicate signal identity: {item['signal_id']}")
        by_id[item["signal_id"]] = item
    return sorted(by_id.values(), key=lambda item: (item["sequence"], item["signal_id"]))
