#!/usr/bin/env python3
"""Proposals index feed collector — schema proposals-feed/v1.

Reads the proposal registry of record (docs/proposals/registry.yaml)
and the Oracle Method pass records (docs/proposals/passes/*/pass.json)
and emits the feed the dashboard's proposals page renders: every
registered proposal pack with its status, priority, author and related
issues/PRs, linked to its tree on GitHub, plus the pass records.

Honesty rules (contract: docs/ops/PROPOSALS-FEED.md): registry values
are carried verbatim — statuses, priorities and author strings are
never normalized, merged or inferred; a field the registry omits
renders as an empty list, never a guessed one; a pass record whose
pass.json cannot be read is named in `gaps`, never silently dropped.

Usage: proposals_feed.py --registry docs/proposals/registry.yaml \
         --proposals-root docs/proposals --out FEED.json

The registry is YAML. PyYAML is used when importable; otherwise a
subset parser for this registry's regular shape runs instead (scalar
fields, inline or block integer lists for the related fields). The
two parsers are differential-tested against each other.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "proposals-feed/v1"
TREE = "https://github.com/timerloggedout-spec/termux-monorepo/tree/master/docs/proposals/"
ITEM_KEYS = ("id", "title", "author", "status", "priority", "path")
INT_LIST_KEYS = ("related_issues", "related_prs")


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return json.loads(value)
    if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def _int_list(value: str) -> list[int]:
    value = value.strip()
    if value in ("", "[]"):
        return []
    assert value.startswith("[") and value.endswith("]"), f"not a flow list: {value!r}"
    return [int(x.strip()) for x in value[1:-1].split(",") if x.strip()]


def parse_registry_subset(text: str) -> dict:
    """Parse the registry without PyYAML (its regular shape only)."""
    registry: dict = {"proposals": []}
    current: dict | None = None
    pending_list_key: str | None = None
    in_proposals = False
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 0:
            in_proposals = line.startswith("proposals:")
            if not in_proposals and ":" in line:
                key, _, value = line.partition(":")
                registry[key.strip()] = _unquote(value)
            current = None
            pending_list_key = None
            continue
        if not in_proposals:
            continue
        if indent == 2 and line.startswith("- "):
            current = {}
            registry["proposals"].append(current)
            pending_list_key = None
            line = line[2:]
            indent = 4
            if not line:
                continue
        if current is None:
            continue
        if indent == 4 and ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            pending_list_key = None
            if key in ITEM_KEYS:
                current[key] = _unquote(value)
            elif key in INT_LIST_KEYS:
                if value:
                    current[key] = _int_list(value)
                else:
                    current[key] = []
                    pending_list_key = key
            continue
        if indent == 6 and line.startswith("- ") and pending_list_key:
            current[pending_list_key].append(int(line[2:].strip()))
            continue
        # anything deeper belongs to a skipped nested block (reviewers,
        # related_branches, gates_required, ...) — not feed fields.
    return registry


def load_registry(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return parse_registry_subset(text)


def build_feed(registry: dict, proposals_root: Path, now: str) -> dict:
    proposals = []
    for entry in registry.get("proposals", []):
        path = str(entry.get("path", "")).strip()
        proposals.append({
            "id": entry.get("id"),
            "title": entry.get("title"),
            "author": entry.get("author"),
            "status": entry.get("status"),
            "priority": entry.get("priority"),
            "path": path,
            "url": TREE + path.lstrip("/"),
            "issues": [int(x) for x in entry.get("related_issues") or []],
            "prs": [int(x) for x in entry.get("related_prs") or []],
        })

    gaps: list[str] = []
    passes = []
    passes_dir = proposals_root / "passes"
    if passes_dir.is_dir():
        for pass_dir in sorted(p for p in passes_dir.iterdir() if p.is_dir()):
            record = {"id": pass_dir.name, "pass_id": None, "schema": None,
                      "status": None, "candidates": None,
                      "path": f"passes/{pass_dir.name}/",
                      "url": TREE + f"passes/{pass_dir.name}"}
            try:
                data = json.loads((pass_dir / "pass.json").read_text(encoding="utf-8"))
                record["pass_id"] = data.get("pass_id")
                record["schema"] = data.get("schema")
                # the pass's own status, verbatim from its record —
                # never inferred from the registry or the pass's age
                record["status"] = data.get("status")
                if record["status"] is None:
                    gaps.append(f"pass {pass_dir.name}: no status field in pass.json (not inferred)")
                if isinstance(data.get("candidates"), list):
                    record["candidates"] = len(data["candidates"])
            except Exception as exc:  # named, never silently dropped
                gaps.append(f"pass {pass_dir.name}: pass.json unreadable ({type(exc).__name__})")
            passes.append(record)
    else:
        gaps.append("docs/proposals/passes/ not found")

    def tally(key: str) -> dict:
        counts: dict[str, int] = {}
        for p in proposals:
            counts[p[key]] = counts.get(p[key], 0) + 1
        return counts

    return {
        "schema": SCHEMA,
        "generated_at": now,
        "source": "docs/proposals/registry.yaml",
        "registry_updated_at": registry.get("updated_at"),
        "registry_updated_by": registry.get("updated_by"),
        "counts": {
            "total": len(proposals),
            "by_status": tally("status"),
            "by_priority": tally("priority"),
            "by_author": tally("author"),
            "passes": len(passes),
        },
        "proposals": proposals,
        "passes": passes,
        "gaps": gaps,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="docs/proposals/registry.yaml")
    ap.add_argument("--proposals-root", default="docs/proposals")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    registry = load_registry(Path(args.registry))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    feed = build_feed(registry, Path(args.proposals_root), now)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(feed, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out}: {feed['counts']['total']} proposals, "
          f"{feed['counts']['passes']} passes, {len(feed['gaps'])} gaps")


if __name__ == "__main__":
    main()
