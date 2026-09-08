#!/usr/bin/env python3
"""Bounded, deterministic Issue Observatory matcher.

Consumes JSON objects with `number`, `title`, `body`, `labels`, and optional
`changed_paths`; emits candidate relations with explainable evidence.
No network access and no writes: the workflow owns collection and policy.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import PurePosixPath

STOP = {"the", "and", "for", "with", "this", "that", "from", "into", "are", "was", "have", "has", "will", "not"}
REF = re.compile(r"(?:#|issues/|pull/)(\d+)", re.I)
TOKEN = re.compile(r"[a-z0-9][a-z0-9_./-]{1,}")


def tokens(text: str) -> set[str]:
    return {x for x in TOKEN.findall((text or "").lower()) if x not in STOP}


def refs(text: str) -> set[str]:
    return set(REF.findall(text or ""))


def jaccard(a: set[str], b: set[str]) -> float:
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def path_similarity(a: list[str], b: list[str]) -> float:
    aa = {str(PurePosixPath(x)) for x in a}
    bb = {str(PurePosixPath(x)) for x in b}
    return jaccard(aa, bb)


def candidate(a: dict, b: dict) -> dict | None:
    ta, tb = tokens(a.get("title", "") + " " + a.get("body", "")), tokens(b.get("title", "") + " " + b.get("body", ""))
    title = jaccard(tokens(a.get("title", "")), tokens(b.get("title", "")))
    body = jaccard(ta, tb)
    paths = path_similarity(a.get("changed_paths", []), b.get("changed_paths", []))
    shared_refs = refs(a.get("body", "")) & refs(b.get("body", ""))
    labels = set(a.get("labels", [])) & set(b.get("labels", []))
    score = min(1.0, 0.45 * title + 0.25 * body + 0.20 * paths + 0.05 * bool(shared_refs) + 0.05 * bool(labels))
    if score < 0.35:
        return None
    relation = "near_duplicate" if score >= 0.78 else "resembles"
    evidence = []
    if title: evidence.append({"kind": "title_similarity", "value": round(title, 4)})
    if body: evidence.append({"kind": "text_similarity", "value": round(body, 4)})
    if paths: evidence.append({"kind": "shared_paths", "value": round(paths, 4)})
    if shared_refs: evidence.append({"kind": "shared_references", "value": sorted(shared_refs)})
    if labels: evidence.append({"kind": "shared_labels", "value": sorted(labels)})
    return {"a": a.get("number"), "b": b.get("number"), "relation": relation, "score": round(score, 4), "confidence": "high" if score >= 0.78 else "candidate", "evidence": evidence}


def main() -> int:
    data = json.load(sys.stdin)
    if not isinstance(data, list):
        raise SystemExit("expected a JSON array")
    out = []
    for i, a in enumerate(data):
        for b in data[i + 1:]:
            if a.get("number") == b.get("number"):
                continue
            hit = candidate(a, b)
            if hit:
                out.append(hit)
    out.sort(key=lambda x: (-x["score"], str(x["a"]), str(x["b"])))
    json.dump({"schema": "issue-observatory/matcher-v1", "count": len(out), "candidates": out}, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
