#!/usr/bin/env python3
"""Pure ATES adapter for deterministic orchestrator benchmark results."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Iterable, Mapping
from she.metrics.agent_throughput import ThroughputMetrics, reduce_events

@dataclass(frozen=True)
class OrchestratorBenchmarkMetrics:
    cases: int
    deterministic_pass_rate: float | None
    boundary_failure_rate: float | None
    omission_failure_rate: float | None
    deterministic_execution_failure_rate: float | None
    mean_net_score: float | None
    throughput: ThroughputMetrics | None
    def to_dict(self) -> dict[str, Any]: return asdict(self)

def reduce_benchmark_results(results: Iterable[Mapping[str, Any]], *, throughput_events: Iterable[Mapping[str, Any]] | None = None, sequential_baseline_sec: float | None = None) -> OrchestratorBenchmarkMetrics:
    rows=[dict(row) for row in results]
    if not rows:
        return OrchestratorBenchmarkMetrics(0,None,None,None,None,None,None)
    total=len(rows)
    passes=sum(row.get("outcome")=="PASS" for row in rows)
    boundary=sum(any("distractor_leak" in str(f) for f in row.get("failures",[])) for row in rows)
    omissions=sum(any("required_fragment_mismatch" in str(f) for f in row.get("failures",[])) for row in rows)
    execution=sum(any("exit_code_mismatch" in str(f) or "missing_assertion" in str(f) or "state_change_mismatch" in str(f) for f in row.get("failures",[])) for row in rows)
    scores=[float(row["net_score"]) for row in rows if isinstance(row.get("net_score"),(int,float))]
    throughput=None
    if throughput_events is not None:
        throughput=reduce_events(throughput_events,sequential_baseline_sec=sequential_baseline_sec)
    return OrchestratorBenchmarkMetrics(total,round(passes/total,6),round(boundary/total,6),round(omissions/total,6),round(execution/total,6),round(sum(scores)/len(scores),6) if scores else None,throughput)