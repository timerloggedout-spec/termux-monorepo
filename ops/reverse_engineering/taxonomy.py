#!/usr/bin/env python3
"""Reverse Engineering taxonomy — validator + query CLI.

The fleet's RE polyhierarchy (taxonomy.json, schema re-taxonomy/v1):
categories and tools placed exactly once, overlap expressed as extra
parents + axis tags, toolchains as stage handoffs. Sibling of the
Foundry's web-only sub-registry (ops/web_adapter_foundry/taxonomy.json).

  taxonomy.py validate            # structural validation (CI-able)
  taxonomy.py node <id>           # one node + its children
  taxonomy.py toolchain <cat-id>  # stage chain for a category
  taxonomy.py overlap             # work-family x method matrix

Stdlib only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_taxonomy(path: str | Path | None = None) -> dict:
    p = Path(path) if path else HERE / "taxonomy.json"
    return json.loads(p.read_text(encoding="utf-8"))


def validate(tax: dict) -> list[str]:
    errs: list[str] = []
    if tax.get("schema") != "re-taxonomy/v1":
        errs.append(f"schema must be re-taxonomy/v1, got {tax.get('schema')!r}")
    nodes = tax.get("nodes") or []
    by_id: dict[str, dict] = {}
    for n in nodes:
        if n["id"] in by_id:
            errs.append(f"duplicate node id {n['id']!r}")
        by_id[n["id"]] = n
        if n.get("kind") not in ("category", "tool"):
            errs.append(f"{n['id']}: kind must be category|tool")
    axes = tax.get("axes") or {}
    for n in nodes:
        for parent in n.get("parents", []):
            if parent not in by_id:
                errs.append(f"{n['id']}: unknown parent {parent!r}")
        for axis, values in (n.get("tags") or {}).items():
            if axis not in axes:
                errs.append(f"{n['id']}: unknown axis {axis!r}")
                continue
            for v in values:
                if v not in axes[axis]:
                    errs.append(f"{n['id']}: tag {axis}:{v} not in axis vocabulary")
        if n.get("kind") == "tool" and not (n.get("tags") or {}).get("tool_role"):
            errs.append(f"{n['id']}: tool nodes need tool_role tags")
    # acyclicity + root reachability
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {i: WHITE for i in by_id}

    def visit(i: str, trail: list[str]) -> None:
        color[i] = GRAY
        for p in by_id[i].get("parents", []):
            if p not in by_id:
                continue
            if color[p] == GRAY:
                errs.append(f"parent cycle: {' -> '.join(trail + [i, p])}")
            elif color[p] == WHITE:
                visit(p, trail + [i])
        color[i] = BLACK
    for i in by_id:
        if color[i] == WHITE:
            visit(i, [])
    if "reverse-engineering" not in by_id:
        errs.append("root node 'reverse-engineering' missing")
    else:
        def ancestors(i: str, seen: set) -> set:
            for p in by_id[i].get("parents", []):
                if p in by_id and p not in seen:
                    seen.add(p)
                    ancestors(p, seen)
            return seen
        for i in by_id:
            if i != "reverse-engineering" and \
                    "reverse-engineering" not in ancestors(i, set()):
                errs.append(f"{i}: does not descend from reverse-engineering")
    stages = set(tax.get("workflow_stages") or [])
    for chain in tax.get("toolchains") or []:
        if chain["category"] not in by_id:
            errs.append(f"toolchain: unknown category {chain['category']!r}")
        last = -1
        for step in chain["stages"]:
            if step["stage"] not in stages:
                errs.append(f"toolchain {chain['category']}: unknown stage "
                            f"{step['stage']!r}")
                continue
            idx = tax["workflow_stages"].index(step["stage"])
            if idx < last:
                errs.append(f"toolchain {chain['category']}: stages out of order")
            last = idx
            for t in step["tools"]:
                if t not in by_id or by_id[t].get("kind") != "tool":
                    errs.append(f"toolchain {chain['category']}: {t!r} "
                                f"is not a tool node")
    om = tax.get("overlap_matrix") or {}
    for row_id, row in (om.get("rows") or {}).items():
        if row_id not in by_id:
            errs.append(f"overlap row {row_id!r} is not a node")
        for method, value in row.items():
            if method not in (om.get("methods") or []):
                errs.append(f"overlap {row_id}: unknown method {method!r}")
            if value not in (om.get("values") or []):
                errs.append(f"overlap {row_id}: bad value {value!r}")
    rec = tax.get("example_record") or {}
    for p in rec.get("parents", []):
        if p not in by_id:
            errs.append(f"example_record: unknown parent {p!r}")
    for tool_id in (rec.get("toolchain") or {}).values():
        if tool_id not in by_id:
            errs.append(f"example_record: unknown tool {tool_id!r}")
    return errs


def node(tax: dict, node_id: str) -> dict | None:
    for n in tax["nodes"]:
        if n["id"] == node_id:
            kids = [c["id"] for c in tax["nodes"]
                    if node_id in c.get("parents", [])]
            return {**n, "children": kids}
    return None


def toolchain(tax: dict, category: str) -> dict | None:
    for chain in tax.get("toolchains", []):
        if chain["category"] == category:
            return chain
    return None


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    tax = load_taxonomy()
    cmd = args[0] if args else "validate"
    if cmd == "validate":
        errs = validate(tax)
        print("\n".join(errs) if errs else "re-taxonomy/v1: valid "
              f"({len(tax['nodes'])} nodes, {len(tax['toolchains'])} toolchains)")
        return 1 if errs else 0
    if cmd == "node" and len(args) == 2:
        print(json.dumps(node(tax, args[1]), indent=1, sort_keys=True))
        return 0
    if cmd == "toolchain" and len(args) == 2:
        print(json.dumps(toolchain(tax, args[1]), indent=1, sort_keys=True))
        return 0
    if cmd == "overlap":
        print(json.dumps(tax["overlap_matrix"], indent=1, sort_keys=True))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
