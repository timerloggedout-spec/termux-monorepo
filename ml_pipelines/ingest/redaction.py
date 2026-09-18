"""Snapshot field allowlists. Anything else is dropped."""
from __future__ import annotations

from typing import Any

PR_FIELDS = (
    "number", "title", "url", "mergeable", "mergeStateStatus", "isDraft",
    "updatedAt", "createdAt", "headRefName", "baseRefName", "author",
    "changedFiles", "additions", "deletions", "labels",
)
ISSUE_FIELDS = (
    "number", "title", "url", "updatedAt", "createdAt", "author",
    "labels", "comment_count",
)
RUN_FIELDS = (
    "id", "name", "title", "conclusion", "status", "branch", "event",
    "createdAt", "url",
)


def project(row: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {key: row.get(key) for key in fields}
