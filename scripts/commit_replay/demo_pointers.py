#!/usr/bin/env python3
"""Pointer-created demo - assembled by compose() from this recipe.

Fragments git/iso/parse_commit are imported via gpointers from
scripts/commit_replay/extract.py (blob 80f468513959) instead of being
written again. Recipe: ops/commit-replay/recipes/demo-commit-parse.json
Regenerate: compose.py --recipe <this file> ; verify: --check
"""
import subprocess
from datetime import datetime, timezone


def git(root, *args):
    out = subprocess.run(["git", "-C", root, *args],
                         capture_output=True, text=True, check=True)
    return out.stdout


def iso(ts, tz):
    try:
        dt = datetime.fromtimestamp(int(ts), timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None


def parse_commit(root, oid):
    raw = git(root, "cat-file", "commit", oid)
    tree, parents, author, ts = None, [], None, None
    for line in raw.splitlines():
        if line.startswith("tree "):
            tree = line[5:].strip()
        elif line.startswith("parent "):
            parents.append(line[7:].strip())
        elif line.startswith("author "):
            # author Name <email> ts tz
            body = line[7:]
            lt, gt = body.rfind("<"), body.rfind(">")
            author = body[:lt].strip() if 0 <= lt < gt else body
            parts = body[gt + 1:].split() if gt >= 0 else []
            ts = iso(parts[0], parts[1] if len(parts) > 1 else "+0000") \
                if parts else None
        elif line == "":
            break
    return {"kind": "commit", "oid": oid, "tree": tree,
            "parents": parents, "author": author, "ts": ts, "refs": []}

if __name__ == "__main__":
    import json, sys
    print(json.dumps(parse_commit(sys.argv[1], sys.argv[2]),
                     indent=1, sort_keys=True))
