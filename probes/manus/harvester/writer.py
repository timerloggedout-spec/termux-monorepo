"""Append-only JSONL writer. Paths stay under captures/ (gitignored)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .normalize import normalize_event


def append_event(path: Path, raw: dict[str, Any]) -> None:
    event = normalize_event(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
