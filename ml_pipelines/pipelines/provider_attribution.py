"""Provider attribution histogram. Shared PAT login is not an agent id."""
from __future__ import annotations

from typing import Any

from ml_pipelines.features.agent_attribution import author_histogram


def run(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "pr_authors": author_histogram(list(snapshot.get("prs") or [])),
        "note": "timerloggedout-spec is a shared operator login, not a single agent.",
    }
