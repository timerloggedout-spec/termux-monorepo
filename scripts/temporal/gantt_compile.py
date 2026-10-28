#!/usr/bin/env python3
"""N4 — Gantt-as-workflow compiler (Temporal pass; addendum 2026-10-27).

Compiles a Gantt plan in the fleet's filing format — one phase per
line, "phase | start | end | depends-on" (the delphi-rfp form's
format) — into a workflow-shaped DAG: stages in topological order,
dependency waves, critical path, and per-phase dependency closure.

The Kahn core is NOT re-implemented here: ordering, frontiers and
cycle residuals come from the canonical Kahn surface
(`she/orchestration/dag.py`, algorithm `kahn-reference-v2`). This
module owns only the filing-format parsing and the aggregated
violation reporting (unknown dependencies are collected, not raised
one at a time — the envelope-validator discipline).

Usage: gantt_compile.py PLAN.txt [PLAN2.txt ...]  (JSON to stdout)
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_kahn():
    root = Path(__file__).resolve().parents[2]
    path = root / "she" / "orchestration" / "dag.py"
    spec = importlib.util.spec_from_file_location("she_kahn_dag", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


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
    by_name = {p["phase"]: p for p in phases}
    closure = {}
    for p in phases:
        seen, stack = set(), list(p["depends_on"])
        while stack:
            d = stack.pop()
            if d in by_name and d not in seen:
                seen.add(d)
                stack.extend(by_name[d]["depends_on"])
        closure[p["phase"]] = sorted(seen)
    if violations:
        return {"valid": False, "violations": violations, "stages": [],
                "dependency_closure": closure}
    kahn = _load_kahn()
    edges = [(d, p["phase"]) for p in phases for d in p["depends_on"]]
    plan = kahn.plan_dag(names, edges)
    if not plan.is_acyclic:
        return {"valid": False,
                "violations": ["dependency cycle among: " + ", ".join(plan.cycle_or_blocked_nodes)],
                "stages": [], "dependency_closure": closure,
                "algorithm": plan.algorithm_version, "graph_sha256": plan.graph_sha256}
    depth = {}
    for level, frontier in enumerate(plan.ready_frontiers):
        for node in frontier:
            depth[node] = level + 1
    return {"valid": True, "violations": [],
            "stages": list(plan.topological_order),
            "waves": [list(f) for f in plan.ready_frontiers],
            "critical_path_stages": len(plan.ready_frontiers),
            "depth": depth, "dependency_closure": closure,
            "algorithm": plan.algorithm_version, "graph_sha256": plan.graph_sha256}


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
