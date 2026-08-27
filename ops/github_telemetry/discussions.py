"""GitHub Discussions list via GraphQL — optional network + pure normalize."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DISCUSSIONS_QUERY = """
query($owner: String!, $repo: String!, $n: Int!) {
  repository(owner: $owner, name: $repo) {
    discussions(first: $n, orderBy: {field: UPDATED_AT, direction: DESC}) {
      totalCount
      nodes {
        number
        title
        url
        createdAt
        updatedAt
        answerChosenAt
        category { name slug }
        author { login }
        comments { totalCount }
      }
    }
  }
}
"""


def normalize_discussions_payload(data: Any) -> dict[str, Any]:
    root = data
    if isinstance(data, dict) and "data" in data:
        inner = data.get("data") or data
        if isinstance(inner, dict) and "repository" in inner:
            root = inner
        elif isinstance(inner, dict) and "data" in inner:
            root = inner.get("data") or inner
    repo = root.get("repository") if isinstance(root, dict) else {}
    disc = (repo or {}).get("discussions") if isinstance(repo, dict) else {}
    nodes = list((disc or {}).get("nodes") or []) if isinstance(disc, dict) else []
    items: list[dict[str, Any]] = []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        cat = n.get("category") or {}
        author = n.get("author") or {}
        comments = n.get("comments") or {}
        items.append(
            {
                "number": n.get("number"),
                "title": n.get("title"),
                "url": n.get("url"),
                "created_at": n.get("createdAt"),
                "updated_at": n.get("updatedAt"),
                "answered": bool(n.get("answerChosenAt")),
                "category": cat.get("name") if isinstance(cat, dict) else None,
                "author": author.get("login") if isinstance(author, dict) else None,
                "comment_count": comments.get("totalCount") if isinstance(comments, dict) else None,
            }
        )
    return {
        "discussion_count": len(items),
        "total_count": disc.get("totalCount") if isinstance(disc, dict) else len(items),
        "discussions": items,
        "label": "locally_reconstructed",
        "source": "graphql:discussions",
    }


def collect_discussions(owner: str, repo: str, *, out: Path, max_items: int = 30) -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    cmd = [
        "gh",
        "api",
        "graphql",
        "-f",
        f"query={DISCUSSIONS_QUERY}",
        "-F",
        f"owner={owner}",
        "-F",
        f"repo={repo}",
        "-F",
        f"n={max_items}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy(), check=False)
    if r.returncode != 0:
        print(f"discussions collect failed: {r.stderr[:500]}", file=sys.stderr)
        return 2
    try:
        raw = json.loads(r.stdout)
    except json.JSONDecodeError as e:
        print(f"discussions JSON error: {e}", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)
    raw_path = out / f"discussions-raw-{stamp}.json"
    raw_path.write_text(
        json.dumps({"collected_at": datetime.now(timezone.utc).isoformat(), "data": raw}, indent=2) + "\n"
    )
    summary = normalize_discussions_payload(raw)
    summary["collected_at"] = datetime.now(timezone.utc).isoformat()
    sum_path = out / f"discussions-summary-{stamp}.json"
    sum_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"wrote {raw_path} and {sum_path}")
    return 0
