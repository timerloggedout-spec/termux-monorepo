"""Review-coverage proxy from labels/files. Does not scrape review bodies."""
from __future__ import annotations

from typing import Any


def coverage_proxy(pr: dict[str, Any]) -> dict[str, Any]:
    labels = {str(x).lower() for x in (pr.get("labels") or [])}
    return {
        "number": pr.get("number"),
        "has_security_label": "security" in labels,
        "has_priority_label": any(x in labels for x in ("p0", "priority", "high-priority")),
        "changed_files": int(pr.get("changedFiles") or 0),
        "proxy": "labels+size",
    }
