from __future__ import annotations

from typing import Any


def adapt_pr(raw: dict[str, Any]) -> dict[str, Any]:
    base = raw.get("base")
    if isinstance(base, str):
        raw = {**raw, "base": {"ref": base}}
    return raw
