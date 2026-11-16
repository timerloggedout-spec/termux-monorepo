"""GitHub Projects (ProjectV2) snapshot via GraphQL — optional network.

Uses `gh api graphql`. Pure normalize helpers work offline on saved payloads.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECTS_QUERY = """
query($owner: String!, $repo: String!, $n: Int!) {
  repository(owner: $owner, name: $repo) {
    projectsV2(first: $n) {
      nodes {
        id
        title
        number
        url
        closed
        items(first: 20) {
          totalCount
          nodes {
            id
            type
            content {
              __typename
              ... on Issue { number title state url }
              ... on PullRequest { number title state url }
              ... on DraftIssue { title }
            }
          }
        }
      }
    }
  }
}
"""


def normalize_projects_payload(data: MappingLike) -> dict[str, Any]:
    """Pure: GraphQL response → compact project summary."""
    root = data
    if isinstance(data, dict) and "data" in data:
        # wrapper from our collector or gh
        inner = data.get("data") or data
        if isinstance(inner, dict) and "repository" in inner:
            root = inner
        elif isinstance(inner, dict) and "data" in inner:
            root = inner.get("data") or inner
    repo = {}
    if isinstance(root, dict):
        repo = (root.get("repository") or root) if isinstance(root, dict) else {}
    nodes = []
    if isinstance(repo, dict):
        pv = repo.get("projectsV2") or {}
        nodes = list(pv.get("nodes") or []) if isinstance(pv, dict) else []
    projects: list[dict[str, Any]] = []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        items = n.get("items") or {}
        item_nodes = list(items.get("nodes") or []) if isinstance(items, dict) else []
        projects.append(
            {
                "id": n.get("id"),
                "title": n.get("title"),
                "number": n.get("number"),
                "url": n.get("url"),
                "closed": n.get("closed"),
                "item_count": items.get("totalCount") if isinstance(items, dict) else len(item_nodes),
                "sample_items": [
                    {
                        "type": it.get("type"),
                        "content": it.get("content"),
                    }
                    for it in item_nodes[:10]
                    if isinstance(it, dict)
                ],
            }
        )
    return {
        "project_count": len(projects),
        "projects": projects,
        "label": "locally_reconstructed",
        "source": "graphql:projectsV2",
    }


# typing alias without importing Mapping at runtime cost
MappingLike = Any


def collect_projects(owner: str, repo: str, *, out: Path, max_projects: int = 10) -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    cmd = [
        "gh",
        "api",
        "graphql",
        "-f",
        f"query={PROJECTS_QUERY}",
        "-F",
        f"owner={owner}",
        "-F",
        f"repo={repo}",
        "-F",
        f"n={max_projects}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy(), check=False)
    if r.returncode != 0:
        print(f"projects collect failed: {r.stderr[:500]}", file=sys.stderr)
        return 2
    try:
        raw = json.loads(r.stdout)
    except json.JSONDecodeError as e:
        print(f"projects JSON error: {e}", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)
    raw_path = out / f"projects-raw-{stamp}.json"
    raw_path.write_text(json.dumps({"collected_at": datetime.now(timezone.utc).isoformat(), "data": raw}, indent=2) + "\n")
    summary = normalize_projects_payload(raw)
    summary["collected_at"] = datetime.now(timezone.utc).isoformat()
    sum_path = out / f"projects-summary-{stamp}.json"
    sum_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"wrote {raw_path} and {sum_path}")
    return 0
