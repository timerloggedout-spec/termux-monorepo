"""Concurrent-agent overlap. Classify, do not overwrite WAIT peers."""
from __future__ import annotations
from typing import Any, Mapping

BOT_AUTHORS = (
    "google-labs-jules[bot]",
    "devin-ai-integration[bot]",
    "coderabbitai[bot]",
    "github-actions[bot]",
)

def is_minesweeper(pr: Mapping[str, Any]) -> bool:
    if pr.get("minesweeper"):
        return True
    author = str(pr.get("author") or "")
    files = int(pr.get("changed_files") or 0)
    if author in BOT_AUTHORS and files > 40:
        return True
    return False
