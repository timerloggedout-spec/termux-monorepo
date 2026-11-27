"""Deterministic, read-only retrieval for optimizer-side SIM history.

Retrieval uses explicit domain/component and source/target compatibility metadata.
It preserves negative outcomes and exposes compatibility labels to callers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

from scripts.ci.validate_sim_memory import parse_timestamp, validate_records


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
    problem_id: str
    problem_summary: str
    root_cause: str
    component: str | None
    attempt_id: str
    ordinal: int
    sample_id: str
    outcome: str
    accepted: bool
    change_summary: str
    files: tuple[str, ...]
    rationale: str
    predicted_task_ids: tuple[str, ...]
    fixed_task_ids: tuple[str, ...]
    missed_task_ids: tuple[str, ...]
    unresolved_task_ids: tuple[str, ...]
    passed: int
    total: int
    evidence_refs: tuple[str, ...]
    compatibility: dict[str, str]
    retrieval_score: int
    recorded_at: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


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
    validate_records(path)
    problems: dict[str, dict[str, Any]] = {}
    lessons: list[RetrievedLesson] = []

    with path.open(encoding="utf-8") as stream:
        for raw in stream:
            if not raw.strip():
                continue
            record = json.loads(raw)
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
            context = attempt["context"]
            compatibility, score = _compatibility(query, problem, attempt)
            observation = attempt["observation"]
            prediction = attempt["prediction"]
            change = attempt["change"]
            lessons.append(RetrievedLesson(
                problem_id=problem_id,
                problem_summary=problem["summary"],
                root_cause=problem["root_cause"],
                component=problem.get("component"),
                attempt_id=attempt["attempt_id"],
                ordinal=attempt["ordinal"],
                sample_id=attempt["sample_id"],
                outcome=observation["outcome"],
                accepted=attempt["accepted"],
                change_summary=change["summary"],
                files=tuple(change["files"]),
                rationale=attempt["rationale"],
                predicted_task_ids=tuple(prediction["predicted_task_ids"]),
                fixed_task_ids=tuple(observation["fixed_task_ids"]),
                missed_task_ids=tuple(observation["missed_task_ids"]),
                unresolved_task_ids=tuple(observation.get("unresolved_task_ids", [])),
                passed=observation["passed"],
                total=observation["total"],
                evidence_refs=tuple(observation["evidence_refs"]),
                compatibility=compatibility,
                retrieval_score=score,
                recorded_at=record["recorded_at"],
            ))

    lessons.sort(
        key=lambda item: (
            -item.retrieval_score,
            -parse_timestamp(item.recorded_at).timestamp(),
            item.problem_id,
            item.ordinal,
        )
    )
    return lessons[:query.limit]
