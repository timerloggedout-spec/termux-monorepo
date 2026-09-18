"""Map PR/issue authors onto the provider catalog. PAT identity is not attribution."""
from __future__ import annotations

from collections import Counter
from typing import Any

BOT_HINTS = {
    "google-labs-jules": "jules",
    "ecc-tools": "ecc",
    "github-actions": "actions",
    "dependabot": "dependabot",
    "coderabbitai": "coderabbit",
    "devin-ai-integration": "devin",
}


def attribute_author(login: str | None) -> str:
    if not login:
        return "unknown"
    lowered = login.lower()
    for hint, provider in BOT_HINTS.items():
        if hint in lowered:
            return provider
    if lowered == "timerloggedout-spec":
        return "operator-shared-login"
    return "human-or-unmapped"


def author_histogram(prs: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(attribute_author(pr.get("author")) for pr in prs))
