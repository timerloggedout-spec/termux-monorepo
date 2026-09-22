"""Project replay evidence into corpus experiments (#741)."""
from __future__ import annotations
from typing import Any, Iterable, Mapping
from .lineage import lineage_fields

def project(events: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for event in events:
        fields = lineage_fields(event)
        rows.append({**fields, "corpus": "evolutionary-replay"})
    return rows
