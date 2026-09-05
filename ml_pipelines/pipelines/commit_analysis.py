"""Issue #213 first value-add: local commit-analysis features.

Inspired by github-commit-analysis_fork but implemented stdlib-only
against the redacted snapshot. History files stay untouched.
"""
from __future__ import annotations

from collections import Counter
from typing import Any


def run(snapshot: dict[str, Any]) -> dict[str, Any]:
    commits = list(snapshot.get("commits") or [])
    authors = Counter(str(c.get("author") or "unknown") for c in commits)
    prefixes = Counter()
    for commit in commits:
        msg = str(commit.get("message") or "")
        prefix = msg.split(":")[0].split("(")[0].strip()[:24] or "unknown"
        prefixes[prefix] += 1
    return {
        "commit_count": len(commits),
        "authors": dict(authors),
        "message_prefixes": dict(prefixes),
        "head": commits[0] if commits else None,
    }
