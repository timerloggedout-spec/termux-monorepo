#!/usr/bin/env python3
"""Validation and resolution for declared ATES sequential baseline cohorts.

This module is deliberately pure and network-free. A baseline is evidence only
when task identity, task contract, environment, and positive measured
repetitions are explicit. It never estimates a missing baseline from parallel
execution.
"""
from __future__ import annotations

import hashlib
import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


_HEX64 = set("0123456789abcdef")


def _hex64(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in _HEX64 for c in value):
        raise ValueError(f"{field} must be a lowercase SHA-256 hex digest")
    return value


def _positive_seconds(values: Any, field: str) -> list[float]:
    if not isinstance(values, list) or not values:
        raise ValueError(f"{field} must contain at least one measurement")
    result: list[float] = []
    for value in values:
        if isinstance(value, bool):
            raise ValueError(f"{field} contains a non-numeric measurement")
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field} contains a non-numeric measurement") from exc
        if number <= 0:
            raise ValueError(f"{field} measurements must be > 0")
        result.append(number)
    return result


@dataclass(frozen=True)
class BaselineTask:
    task_id: str
    task_fingerprint: str
    repetitions_sec: tuple[float, ...]
    median_sec: float

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BaselineTask":
        task_id = value.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("task_id is required")
        fingerprint = _hex64(value.get("task_fingerprint"), "task_fingerprint")
        repetitions = _positive_seconds(value.get("repetitions_sec"), f"{task_id}.repetitions_sec")
        expected = statistics.median(repetitions)
        supplied = value.get("median_sec")
        if supplied is not None and abs(float(supplied) - expected) > 1e-9:
            raise ValueError(f"{task_id}.median_sec does not match the measured median")
        return cls(task_id, fingerprint, tuple(repetitions), expected)


@dataclass(frozen=True)
class BaselineCohort:
    cohort_id: str
    task_contract_hash: str
    environment_fingerprint: str
    tasks: tuple[BaselineTask, ...]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BaselineCohort":
        if value.get("schema_version") != "ates.baseline.v1":
            raise ValueError("unsupported baseline schema_version")
        cohort_id = value.get("cohort_id")
        if not isinstance(cohort_id, str) or not cohort_id:
            raise ValueError("cohort_id is required")
        contract = _hex64(value.get("task_contract_hash"), "task_contract_hash")
        environment = _hex64(value.get("environment_fingerprint"), "environment_fingerprint")
        raw_tasks = value.get("tasks")
        if not isinstance(raw_tasks, list) or not raw_tasks:
            raise ValueError("tasks must contain at least one task")
        tasks = tuple(BaselineTask.from_mapping(task) for task in raw_tasks)
        ids = [task.task_id for task in tasks]
        fingerprints = [task.task_fingerprint for task in tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("task_id values must be unique")
        if len(fingerprints) != len(set(fingerprints)):
            raise ValueError("task_fingerprint values must be unique")
        return cls(cohort_id, contract, environment, tasks)

    @classmethod
    def from_path(cls, path: str | Path) -> "BaselineCohort":
        return cls.from_mapping(json.loads(Path(path).read_text(encoding="utf-8")))

    def sequential_seconds(self, task_fingerprints: Sequence[str]) -> float:
        """Return the declared serial cohort duration for an exact task set.

        Matching is by immutable task fingerprint, not display name. Unknown or
        duplicate tasks fail closed so ATES cannot compare incomparable work.
        """
        requested = list(task_fingerprints)
        if not requested or len(requested) != len(set(requested)):
            raise ValueError("task_fingerprints must be a non-empty unique sequence")
        by_fingerprint = {task.task_fingerprint: task for task in self.tasks}
        if any(fingerprint not in by_fingerprint for fingerprint in requested):
            raise KeyError("baseline cohort does not contain every requested task")
        return sum(by_fingerprint[fingerprint].median_sec for fingerprint in requested)


def fingerprint_task(task_contract: Mapping[str, Any]) -> str:
    """Create the canonical SHA-256 fingerprint for a task contract mapping."""
    encoded = json.dumps(task_contract, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
