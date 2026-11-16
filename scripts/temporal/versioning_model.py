#!/usr/bin/env python3
"""V3 versioned-autoscale: the model that is the variant's claim.

Worker Versioning + backlog-driven autoscaling, modeled
deterministically (K8s actuation itself is specified_not_run — no
cluster; omes receipts are the declared suite, this model is the
evidence the claim stands on):

- Routing: each workflow pins the build id current at its start; a
  routing change (new default build) NEVER moves an in-flight
  workflow (N3's actuation invariant).
- Autoscale policy: workers = clamp(ceil(backlog / target_per_worker)
  adjusted by latency pressure, min..max) — a pure function, so the
  same metrics always yield the same actuation decision.

Self-check mode asserts both properties over synthetic metrics and
prints the decision table. Exit 0 = model properties hold.
"""

from __future__ import annotations

import json
import math
import sys

MIN_WORKERS, MAX_WORKERS = 1, 32
TARGET_PER_WORKER = 25
LATENCY_PRESSURE_MS = 2000


def route(builds: list[str], default_build: str, inflight: dict[str, str],
          workflow_id: str) -> str:
    """An in-flight workflow keeps its pinned build; new starts take the default."""
    return inflight.get(workflow_id, default_build)


def autoscale(backlog: int, p95_latency_ms: int) -> int:
    base = math.ceil(backlog / TARGET_PER_WORKER) if backlog > 0 else MIN_WORKERS
    if p95_latency_ms > LATENCY_PRESSURE_MS and backlog > 0:
        base = math.ceil(base * 1.5)
    return max(MIN_WORKERS, min(MAX_WORKERS, base))


def main() -> int:
    failures = []
    builds = ["b1", "b2"]
    inflight = {"wf-old": "b1"}
    if route(builds, "b2", inflight, "wf-old") != "b1":
        failures.append("in-flight workflow moved by a routing change")
    if route(builds, "b2", inflight, "wf-new") != "b2":
        failures.append("new workflow did not take the new default build")
    table = {}
    prev = 0
    for backlog, lat in ((0, 100), (10, 100), (100, 100), (100, 5000),
                         (500, 100), (5000, 9000)):
        w = autoscale(backlog, lat)
        table[f"backlog={backlog},p95={lat}"] = w
        if backlog >= 100 and w < prev:
            failures.append(f"autoscale not monotone at backlog={backlog}")
        prev = w
    if autoscale(0, 100) != MIN_WORKERS or autoscale(10**9, 10**5) != MAX_WORKERS:
        failures.append("autoscale clamps broken")
    print(json.dumps({"verdict": "PASS" if not failures else "FAIL",
                      "decision_table": table, "failures": failures}, indent=1))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
