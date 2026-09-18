"""Quota/skip interpretation. Skip is not a gate failure."""
from __future__ import annotations

from typing import Any


def classify_run(run: dict[str, Any]) -> str:
    title = f"{run.get('name') or ''} {run.get('title') or ''}".lower()
    conclusion = (run.get("conclusion") or "").lower()
    if conclusion == "skipped":
        return "quota_or_path_skip"
    if conclusion == "cancelled":
        return "superseded_or_cancel"
    if "ledger" in title and conclusion == "failure":
        return "ledger_failure"
    if conclusion == "failure":
        return "workflow_failure"
    if conclusion == "success":
        return "success"
    return "unknown"
