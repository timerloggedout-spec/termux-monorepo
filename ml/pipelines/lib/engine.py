"""Tiny DAG runner. Stages are callables(context) -> None."""
from __future__ import annotations

from typing import Any, Callable

Stage = Callable[[dict[str, Any]], None]


def run_dag(stages: list[tuple[str, Stage]], context: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for name, fn in stages:
        fn(context)
        results.append({"stage": name, "ok": True})
    return results


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {"stages": len(results), "ok": all(r.get("ok") for r in results)}
