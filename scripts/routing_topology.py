#!/usr/bin/env python3
"""Bounded executors for optimized routing topologies.

This module is deliberately provider-neutral. It executes already-admitted
participants and emits evidence describing what was actually executed.
Admission, credentials, policy, and candidate selection remain upstream.

Supported modes:
single, series, dynamic, parallel, nested, co-working, volley.

The executor never treats a declared topology as evidence of execution.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Iterable


MODES = {"single", "series", "dynamic", "parallel", "nested", "co-working", "volley"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class Participant:
    name: str
    run: Callable[[Any], Any]
    owner: str | None = None


@dataclass
class Evidence:
    topology: str
    declared_participants: list[str]
    executed_participants: list[str] = field(default_factory=list)
    outputs: list[Any] = field(default_factory=list)
    rounds: int = 0
    execution_status: str = "NOT_EXECUTED"
    observed_at: str = field(default_factory=utc_now)
    errors: list[dict[str, str]] = field(default_factory=list)

    def envelope(self) -> dict[str, Any]:
        return {
            "schema": "routing-execution/v1",
            "topology": self.topology,
            "declared_participants": self.declared_participants,
            "executed_participants": self.executed_participants,
            "outputs": self.outputs,
            "rounds": self.rounds,
            "execution_status": self.execution_status,
            "observed_at": self.observed_at,
            "errors": self.errors,
        }


def _participants(items: Iterable[Participant]) -> list[Participant]:
    rows = list(items)
    if not rows:
        raise ValueError("at least one admitted participant is required")
    names = [p.name for p in rows]
    if any(not n for n in names) or len(names) != len(set(names)):
        raise ValueError("participant names must be non-empty and unique")
    return rows


def execute_route(
    mode: str,
    participants: Iterable[Participant],
    context: Any = None,
    *,
    selector: Callable[[list[Participant], Any], Participant] | None = None,
    max_workers: int | None = None,
    max_rounds: int = 3,
    stop: Callable[[Any, int], bool] | None = None,
) -> dict[str, Any]:
    """Execute one bounded route and return an auditable evidence envelope."""
    mode = mode.strip().lower()
    if mode not in MODES:
        raise ValueError(f"unsupported routing mode: {mode}")
    if max_rounds < 1:
        raise ValueError("max_rounds must be positive")

    rows = _participants(participants)
    evidence = Evidence(mode, [p.name for p in rows])

    def call(p: Participant, value: Any):
        try:
            result = p.run(value)
            evidence.executed_participants.append(p.name)
            return result
        except Exception as exc:
            evidence.executed_participants.append(p.name)
            evidence.errors.append({"participant": p.name, "error_class": type(exc).__name__})
            raise

    try:
        if mode == "single":
            selected = selector(rows, context) if selector else rows[0]
            evidence.outputs.append(call(selected, context))
            evidence.rounds = 1

        elif mode == "series":
            value = context
            for p in rows:
                value = call(p, value)
                evidence.outputs.append(value)
                evidence.rounds += 1

        elif mode == "parallel":
            workers = max_workers or len(rows)
            with ThreadPoolExecutor(max_workers=min(workers, len(rows))) as pool:
                futures = {pool.submit(call, p, context): p for p in rows}
                for future in as_completed(futures):
                    evidence.outputs.append(future.result())
            evidence.rounds = 1

        elif mode == "dynamic":
            selected = selector(rows, context) if selector else rows[0]
            evidence.outputs.append(call(selected, context))
            evidence.rounds = 1

        elif mode == "nested":
            selected = selector(rows, context) if selector else rows[0]
            nested = selected.run(context)
            if not isinstance(nested, dict) or "participants" not in nested:
                raise ValueError("nested participant must return a route specification")
            nested_rows = _participants(nested["participants"])
            nested_mode = nested.get("mode", "single")
            nested_context = nested.get("context", context)
            nested_evidence = execute_route(
                nested_mode, nested_rows, nested_context,
                max_workers=max_workers, max_rounds=max_rounds, stop=stop,
            )
            evidence.executed_participants.append(selected.name)
            evidence.outputs.append(nested_evidence)
            evidence.rounds = 1 + nested_evidence["rounds"]

        elif mode == "co-working":
            shared = {"context": context, "outputs": []}
            for p in rows:
                value = call(p, shared)
                shared["outputs"].append({"participant": p.name, "value": value})
                evidence.outputs.append(value)
                evidence.rounds += 1

        elif mode == "volley":
            value = context
            for round_no in range(max_rounds):
                p = rows[round_no % len(rows)]
                value = call(p, value)
                evidence.outputs.append(value)
                evidence.rounds += 1
                if stop and stop(value, round_no + 1):
                    break

        evidence.execution_status = "EXECUTED"
    except Exception:
        evidence.execution_status = "PARTIAL" if evidence.executed_participants else "FAILED"

    return evidence.envelope()
