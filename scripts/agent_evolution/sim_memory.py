"""Deterministic, read-only retrieval for optimizer-side SIM history.

Retrieval uses explicit domain/component and source/target compatibility metadata.
It preserves negative outcomes and exposes compatibility labels to callers.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from scripts.ci.validate_sim_memory import _loads_strict, parse_timestamp, validate_records


@dataclass(frozen=True)
class RetrievalQuery:
    domain: str
    component: str | None = None
    target_provider: str | None = None
    target_model: str | None = None
    target_benchmark_id: str | None = None
    target_benchmark_version: str | None = None
    target_environment_fingerprint: str | None = None
    task_ids: tuple[str, ...] = ()
    limit: int = 8

    def __post_init__(self) -> None:
        if not self.domain.strip():
            raise ValueError("domain is required")
        if not 1 <= self.limit <= 32:
            raise ValueError("limit must be between 1 and 32")
        if len(set(self.task_ids)) != len(self.task_ids):
            raise ValueError("task_ids must be unique")


@dataclass(frozen=True)
class RetrievedLesson:
    record: dict[str, Any]
    compatibility: dict[str, str]
    retrieval_score: int

    @property
    def problem_id(self) -> str:
        return self.record["problem_id"]

    @property
    def outcome(self) -> str:
        return self.record["attempt"]["observation"]["outcome"]

    @property
    def missed_task_ids(self) -> tuple[str, ...]:
        return tuple(self.record["attempt"]["observation"]["missed_task_ids"])

    @property
    def recorded_at(self) -> str:
        return self.record["recorded_at"]

    def as_dict(self) -> dict[str, Any]:
        return {
            "record": self.record,
            "compatibility": self.compatibility,
            "retrieval_score": self.retrieval_score,
        }


def _policy_match(query: RetrievalQuery, policy: dict[str, Any]) -> bool:
    requested = {
        "provider": query.target_provider,
        "model": query.target_model,
    }
    active = {key: value for key, value in requested.items() if value}
    return bool(active) and all(policy.get(key) == value for key, value in active.items())


def _compatibility(query: RetrievalQuery, problem: dict[str, Any], attempt: dict[str, Any]) -> tuple[dict[str, str], int]:
    context = attempt["context"]
    labels: dict[str, str] = {}
    score = 100  # Exact domain is a required admission condition.

    component = problem.get("component")
    if query.component:
        if component == query.component:
            labels["component"] = "exact"
            score += 6
        elif component is None:
            labels["component"] = "unscoped"
            score += 1
        else:
            labels["component"] = "different"
    else:
        labels["component"] = "not-requested"

    target_policy = context["target_policy"]
    source_policy = context["source_policy"]
    if _policy_match(query, target_policy):
        labels["policy"] = "target-exact"
        score += 5
    elif _policy_match(query, source_policy):
        labels["policy"] = "source-exact"
        score += 2
    elif query.target_provider or query.target_model:
        known = any(
            policy.get("provider") or policy.get("model")
            for policy in (source_policy, target_policy)
        )
        labels["policy"] = "cross-model" if known else "unknown"
        score -= 1 if known else 0
    else:
        labels["policy"] = "not-requested"

    target_benchmark = context["target_benchmark"]
    source_benchmark = context["source_benchmark"]
    benchmark_requested = query.target_benchmark_id or query.target_benchmark_version
    if benchmark_requested and all(
        not requested or target_benchmark.get(key) == requested
        for key, requested in (
            ("id", query.target_benchmark_id),
            ("version", query.target_benchmark_version),
        )
    ):
        labels["benchmark"] = "target-exact"
        score += 5
    elif benchmark_requested and all(
        not requested or source_benchmark.get(key) == requested
        for key, requested in (
            ("id", query.target_benchmark_id),
            ("version", query.target_benchmark_version),
        )
    ):
        labels["benchmark"] = "source-exact"
        score += 2
    elif benchmark_requested:
        labels["benchmark"] = "cross-benchmark"
        score -= 1
    else:
        labels["benchmark"] = "not-requested"

    target_environment = context["target_environment_fingerprint"]
    source_environment = context["source_environment_fingerprint"]
    if query.target_environment_fingerprint == target_environment and query.target_environment_fingerprint:
        labels["environment"] = "target-exact"
        score += 3
    elif query.target_environment_fingerprint == source_environment and query.target_environment_fingerprint:
        labels["environment"] = "source-exact"
        score += 1
    elif query.target_environment_fingerprint:
        labels["environment"] = "different"
        score -= 1
    else:
        labels["environment"] = "not-requested"

    predicted = set(attempt["prediction"]["predicted_task_ids"])
    overlap = predicted.intersection(query.task_ids)
    if overlap:
        labels["task_overlap"] = "exact-overlap"
        score += 2
    elif query.task_ids:
        labels["task_overlap"] = "no-overlap"
    else:
        labels["task_overlap"] = "not-requested"

    outcome = attempt["observation"]["outcome"]
    if outcome == "improved":
        score += 1
    elif outcome in {"regressed", "unresolved"}:
        score -= 1
    return labels, score


def retrieve_sim_memory(path: Path, query: RetrievalQuery) -> list[RetrievedLesson]:
    """Return the highest-compatibility lessons; preserve all outcome classes."""
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    validate_records(path, raw_lines=raw_lines)
    problems: dict[str, dict[str, Any]] = {}
    lessons: list[RetrievedLesson] = []

    for raw in raw_lines:
        if not raw.strip():
            continue
        record = _loads_strict(raw)
        problem_id = record["problem_id"]
        if record["record_type"] == "problem_opened":
            problems[problem_id] = record["problem"]
            continue

        problem = problems[problem_id]
        if problem["domain"] != query.domain:
            continue
        if query.component and problem.get("component") not in (None, query.component):
            continue

        attempt = record["attempt"]
        compatibility, score = _compatibility(query, problem, attempt)
        lessons.append(RetrievedLesson(
            record=record,
            compatibility=compatibility,
            retrieval_score=score,
        ))

    lessons.sort(
        key=lambda item: (
            -item.retrieval_score,
            -parse_timestamp(item.recorded_at)[0],
            -parse_timestamp(item.recorded_at)[1],
            item.problem_id,
            item.record["attempt"]["ordinal"],
        )
    )
    return lessons[:query.limit]
