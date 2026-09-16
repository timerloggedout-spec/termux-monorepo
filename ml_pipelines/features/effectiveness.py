"""PR change-effectiveness features. Large dirty PRs score low."""
from __future__ import annotations

from typing import Any


def effectiveness(pr: dict[str, Any]) -> dict[str, Any]:
    files = int(pr.get("changedFiles") or 0)
    additions = int(pr.get("additions") or 0)
    deletions = int(pr.get("deletions") or 0)
    churn = additions + deletions
    density = round(churn / files, 2) if files else 0.0
    return {
        "number": pr.get("number"),
        "files": files,
        "churn": churn,
        "density": density,
        "conflicted": pr.get("mergeable") == "CONFLICTING",
    }
