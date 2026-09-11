"""Load a redacted ops snapshot. Comment bodies are never stored."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ml_pipelines.contracts import PipelineError, assert_safe, redacted
from ml_pipelines.io import load_json

REQUIRED = {"captured_at", "repo", "prs", "issues", "runs", "commits"}


@dataclass(frozen=True)
class Snapshot:
    captured_at: str
    repo: str
    master_sha: str
    prs: list[dict[str, Any]]
    issues: list[dict[str, Any]]
    runs: list[dict[str, Any]]
    commits: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "captured_at": self.captured_at,
            "repo": self.repo,
            "master_sha": self.master_sha,
            "prs": self.prs,
            "issues": self.issues,
            "runs": self.runs,
            "commits": self.commits,
        }


def load_snapshot(path: Path) -> Snapshot:
    raw = redacted(load_json(path))
    missing = REQUIRED - set(raw)
    if missing:
        raise PipelineError(f"snapshot missing {sorted(missing)}")
    assert_safe(raw)
    return Snapshot(
        captured_at=str(raw["captured_at"]),
        repo=str(raw["repo"]),
        master_sha=str(raw.get("master_sha") or ""),
        prs=list(raw["prs"]),
        issues=list(raw["issues"]),
        runs=list(raw["runs"]),
        commits=list(raw["commits"]),
    )
