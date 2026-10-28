#!/usr/bin/env python3
"""N4 — Gantt-as-workflow compiler (Temporal pass addendum, 2026-10-27).

Compiles a Gantt plan in the fleet's filing format — one phase per
line, "phase | start | end | depends-on" (the delphi-rfp form's
format, also used for candidate plans in Oracle Method passes) —
into a workflow-shaped DAG: stages in topological order, dependency
edges, and the query answers a workflow runtime would need
(critical path by stage count, dependency closure per phase).

Deterministic, offline, stdlib only. A plan that references an
unknown phase or contains a dependency cycle fails compilation with
the violations aggregated — the same discipline as the evidence
envelope validators (V4).

Usage: gantt_compile.py PLAN.txt [PLAN2.txt ...]  (JSON to stdout)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def parse_gantt(text: str) -> list[dict]:
    phases = []
    for line in text.splitlines():
        line = line.strip().strip("-* ")
        if "|" not in line or line.lower().startswith("phase |"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 4 or not parts[0]:
            continue
        depends = [] if parts[3] in ("-", "") else [d.strip() for d in parts[3].split(",") if d.strip()]
        phases.append({"phase": parts[0], "start": parts[1], "end": parts[2], "depends_on": depends})
    return phases


def compile_plan(phases: list[dict]) -> dict:
    names = [p["phase"] for p in phases]
    violations = []
    if len(names) != len(set(names)):
        violations.append("duplicate phase names")
    known = set(names)
    for p in phases:
        for d in p["depends_on"]:
            if d not in known:
                violations.append(f"{p['phase']}: unknown dependency '{d}'")
    order, placed, remaining = [], set(), list(phases)
    while remaining:
        ready = [p for p in remaining if all(d in placed for d in p["depends_on"])]
        if not ready:
            stuck = [p["phase"] for p in remaining
                     if all(d in known for d in p["depends_on"])]
            if stuck:
                violations.append("dependency cycle among: " + ", ".join(stuck))
            break
        for p in sorted(ready, key=lambda x: x["phase"]):
            order.append(p["phase"])
            placed.add(p["phase"])
            remaining.remove(p)
    depth = {}
    by_name = {p["phase"]: p for p in phases}
    for name in order:
        depth[name] = 1 + max((depth[d] for d in by_name[name]["depends_on"]), default=0)
    critical = max(depth.values(), default=0)
    closure = {}
    for name in order:
        seen, stack = set(), list(by_name[name]["depends_on"])
        while stack:
            d = stack.pop()
            if d not in seen:
                seen.add(d)
                stack.extend(by_name[d]["depends_on"])
        closure[name] = sorted(seen)
    return {"valid": not violations, "violations": violations,
            "stages": order, "critical_path_stages": critical,
            "depth": depth, "dependency_closure": closure}


def compile_text(text: str) -> dict:
    phases = parse_gantt(text)
    if not phases:
        return {"valid": False, "violations": ["no Gantt phases parsed"], "stages": []}
    return compile_plan(phases)


def main() -> int:
    out = {}
    for arg in sys.argv[1:]:
        out[arg] = compile_text(Path(arg).read_text())
    print(json.dumps(out, indent=1))
    return 0 if all(v["valid"] for v in out.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
