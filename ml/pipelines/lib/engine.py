"""engine: Sequential DAG runner with halt-on-fail."""
from __future__ import annotations

from typing import Callable, Iterable, Mapping, MutableMapping, Any

from .types import StageResult, StageStatus

StageFn = Callable[[MutableMapping[str, Any]], StageResult]


def run_dag(stages: Iterable[tuple[str, StageFn]], context: MutableMapping[str, Any]) -> list[StageResult]:
    results: list[StageResult] = []
    for stage_id, fn in stages:
        result = fn(context)
        if result.stage_id != stage_id:
            result = StageResult(stage_id=stage_id, status=result.status, artifacts=result.artifacts, notes=result.notes)
        results.append(result)
        context.setdefault("results", {})[stage_id] = result
        if result.status is StageStatus.FAILED:
            break
    return results


def all_ok(results: Iterable[StageResult]) -> bool:
    return all(item.status in {StageStatus.OK, StageStatus.SKIPPED} for item in results)


def summarize(results: Iterable[StageResult]) -> Mapping[str, str]:
    return {item.stage_id: item.status.value for item in results}
