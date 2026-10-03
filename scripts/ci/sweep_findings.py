#!/usr/bin/env python3
"""Build sweep findings JSON from checkout env and optional census files."""
import json
import os
import pathlib

def main() -> int:
    items = [
        {
            "id": "repository-head",
            "classification": "OBSERVED",
            "statement": "HEAD=" + os.environ["HEAD_SHA"],
            "evidence_refs": ["git://commit/" + os.environ["HEAD_SHA"]],
            "confidence": 1,
        },
        {
            "id": "repository-commit-count",
            "classification": "OBSERVED",
            "statement": "reachable commits=" + os.environ["COMMITS"],
            "evidence_refs": ["git://rev-list"],
            "confidence": 1,
        },
        {
            "id": "trigger-event",
            "classification": "OBSERVED",
            "statement": "sweep trigger=" + os.environ["EVENT_KIND"],
            "evidence_refs": ["github://event"],
            "confidence": 1,
        },
    ]
    census = pathlib.Path(os.environ.get("CENSUS_DIR", "docs/ops/generated/sweep-ledger/census"))
    if census.exists():
        for name in ("pulls", "issues", "workflow-runs"):
            path = census.joinpath(name + ".json")
            if not path.exists():
                continue
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                if raw and isinstance(raw, list) and isinstance(raw[0], list):
                    n = sum(len(x) for x in raw)
                elif isinstance(raw, list):
                    n = len(raw)
                else:
                    n = 0
            except Exception:
                n = -1
            items.append({
                "id": "census-" + name,
                "classification": "OBSERVED",
                "statement": name + " pages/items=" + str(n),
                "evidence_refs": ["artifact://census/" + name],
                "confidence": 1,
            })
    print(json.dumps(items, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
