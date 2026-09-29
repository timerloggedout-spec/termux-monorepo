"""Minesweeper: concurrent agents open overlapping PRs. Do not overwrite WAIT peers."""
from __future__ import annotations

from typing import Any

BOT_LOGINS = frozenset(
    {
        "google-labs-jules[bot]",
        "github-actions[bot]",
        "coderabbitai[bot]",
        "devin-ai-integration[bot]",
        "cursor[bot]",
        "copilot-swe-agent[bot]",
    }
)

MINESWEEPER_TOKENS = (
    "palette:",
    "sentinel:",
    "bolt:",
    "linguist:",
    "minesweeper",
)


def is_bot_author(pr: dict[str, Any]) -> bool:
    user = pr.get("user") or {}
    login = user.get("login") if isinstance(user, dict) else pr.get("author")
    return str(login or "") in BOT_LOGINS or str(login or "").endswith("[bot]")


def minesweeper_title(pr: dict[str, Any]) -> bool:
    title = str(pr.get("title") or "").lower()
    return any(token in title for token in MINESWEEPER_TOKENS)


def files_over_extract_threshold(pr: dict[str, Any], threshold: int = 40) -> bool:
    return int(pr.get("changed_files") or 0) > threshold


def minesweeper_extract(pr: dict[str, Any]) -> bool:
    return (is_bot_author(pr) and files_over_extract_threshold(pr)) or minesweeper_title(pr)
