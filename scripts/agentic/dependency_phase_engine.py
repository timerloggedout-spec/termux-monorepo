#!/usr/bin/env python3
"""Deterministic evaluation and rendering for the repository dependency-phase plan.

The engine is deliberately offline and side-effect free. It accepts a canonical
plan plus a JSON evidence snapshot, reports lifecycle state, and generates
Mermaid/Markdown views. GitHub reads and writes live in separate adapters.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TERMINAL = {"complete"}
PROJECT_DONE = "Done"
SUCCESS_STATES = {"success", "successful", "completed", "neutral", "skipped"}


class PlanValidationError(ValueError):
    """Raised when a plan cannot be evaluated safely."""


@dataclass(frozen=True)
class Evaluation:
    phase_id: str
    state: str
    reason: str
    project_item_id: str | None
    project_status: str | None
    pull_requests: tuple[int, ...]
    idempotency_key: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "phase_id": self.phase_id,
            "state": self.state,
            "reason": self.reason,
            "project_item_id": self.project_item_id,
            "project_status": self.project_status,
            "pull_requests": list(self.pull_requests),
            "idempotency_key": self.idempotency_key,
        }


def load_json(path: str | Path) -> dict[str, Any]:
    """Load one JSON document and require an object top level."""
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PlanValidationError(f"{path}: expected a JSON object")
    return value


def plan_digest(plan: dict[str, Any]) -> str:
    """Return a stable SHA-256 digest used for idempotency and provenance."""
    payload = json.dumps(plan, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def topological_order(phases: Iterable[dict[str, Any]]) -> list[str]:
    """Return a stable topological ordering or raise with cycle details."""
    phase_list = list(phases)
    identifiers = [str(phase.get("phase_id", "")) for phase in phase_list]
    by_id = {phase["phase_id"]: phase for phase in phase_list}
    incoming = {phase_id: set(by_id[phase_id].get("depends_on", [])) for phase_id in identifiers}
    outgoing: dict[str, set[str]] = defaultdict(set)
    for phase_id, dependencies in incoming.items():
        for dependency in dependencies:
            outgoing[dependency].add(phase_id)

    ready = deque(sorted(phase_id for phase_id, dependencies in incoming.items() if not dependencies))
    result: list[str] = []
    while ready:
        phase_id = ready.popleft()
        result.append(phase_id)
        for dependent in sorted(outgoing.get(phase_id, set())):
            incoming[dependent].discard(phase_id)
            if not incoming[dependent]:
                ready.append(dependent)

    if len(result) != len(identifiers):
        cyclic = sorted(phase_id for phase_id, dependencies in incoming.items() if dependencies)
        raise PlanValidationError("dependency cycle detected: " + ", ".join(cyclic))
    return result


def validate_plan(plan: dict[str, Any]) -> list[str]:
    """Validate schema-level and graph-level invariants without modifying input."""
    errors: list[str] = []
    _require(plan.get("schema_version") == 1, "schema_version must equal 1", errors)
    _require(isinstance(plan.get("plan_id"), str) and plan["plan_id"], "plan_id is required", errors)
    _require(plan.get("base_branch") == "master-staging", "base_branch must be master-staging", errors)
    phases = plan.get("phases")
    _require(isinstance(phases, list) and phases, "phases must be a non-empty list", errors)
    if errors:
        return errors

    policy = plan.get("policy", {})
    approved_agents = set(policy.get("dispatch_agents", []))
    seen: set[str] = set()
    phase_ids: set[str] = set()
    for index, phase in enumerate(phases):
        prefix = f"phases[{index}]"
        if not isinstance(phase, dict):
            errors.append(f"{prefix} must be an object")
            continue
        phase_id = phase.get("phase_id")
        _require(isinstance(phase_id, str) and re.fullmatch(r"[A-Z][A-Z0-9-]{2,63}", phase_id or "") is not None,
                 f"{prefix}.phase_id must be an uppercase stable identifier", errors)
        if isinstance(phase_id, str):
            if phase_id in seen:
                errors.append(f"duplicate phase_id: {phase_id}")
            seen.add(phase_id)
            phase_ids.add(phase_id)
        _require(isinstance(phase.get("title"), str) and len(phase["title"].strip()) >= 3,
                 f"{prefix}.title is required", errors)
        dependencies = phase.get("depends_on")
        _require(isinstance(dependencies, list), f"{prefix}.depends_on must be a list", errors)
        if isinstance(dependencies, list):
            if len(set(dependencies)) != len(dependencies):
                errors.append(f"{prefix}.depends_on contains duplicates")
            if phase_id in dependencies:
                errors.append(f"{prefix} cannot depend on itself")
        checks = phase.get("completion", {}).get("required_checks") if isinstance(phase.get("completion"), dict) else None
        _require(isinstance(checks, list) and checks, f"{prefix}.completion.required_checks must be non-empty", errors)
        execution = phase.get("execution")
        _require(isinstance(execution, dict), f"{prefix}.execution must be an object", errors)
        if isinstance(execution, dict):
            _require(execution.get("mode") in {"agent", "human", "agent_or_human"},
                     f"{prefix}.execution.mode is invalid", errors)
            preferred = execution.get("preferred_agent")
            if execution.get("mode") == "agent":
                _require(preferred in approved_agents, f"{prefix}.preferred_agent is not approved", errors)

    for phase in phases:
        if not isinstance(phase, dict):
            continue
        for dependency in phase.get("depends_on", []):
            if dependency not in phase_ids:
                errors.append(f"{phase.get('phase_id', '<unknown>')} depends on unknown phase {dependency}")
    if not errors:
        try:
            topological_order(phases)
        except PlanValidationError as error:
            errors.append(str(error))
    return errors


def require_valid_plan(plan: dict[str, Any]) -> None:
    errors = validate_plan(plan)
    if errors:
        raise PlanValidationError("plan validation failed:\n- " + "\n- ".join(errors))


def _phase_text_matches(phase_id: str, candidate: dict[str, Any]) -> bool:
    text_parts = [str(candidate.get("title", "")), str(candidate.get("body", ""))]
    content = candidate.get("content")
    if isinstance(content, dict):
        text_parts.extend([str(content.get("title", "")), str(content.get("body", ""))])
    return re.search(rf"(?<![A-Z0-9-]){re.escape(phase_id)}(?![A-Z0-9-])", "\n".join(text_parts)) is not None


def _project_item_for_phase(phase_id: str, items: list[dict[str, Any]]) -> dict[str, Any] | None:
    matches = [item for item in items if _phase_text_matches(phase_id, item)]
    if not matches:
        return None
    return sorted(matches, key=lambda item: str(item.get("id", "")))[0]


def _pull_requests_for_phase(phase_id: str, pull_requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted((pr for pr in pull_requests if _phase_text_matches(phase_id, pr)), key=lambda pr: int(pr.get("number", 0)))


def _checks_passed(pull_requests: list[dict[str, Any]], required_checks: list[str]) -> bool:
    if not pull_requests:
        return False
    for pull_request in pull_requests:
        checks = pull_request.get("checks", {})
        if not isinstance(checks, dict):
            return False
        for required in required_checks:
            if str(checks.get(required, "")).lower() not in SUCCESS_STATES:
                return False
    return True


def _is_approved(phase_id: str, snapshot: dict[str, Any]) -> bool:
    approvals = snapshot.get("approvals", {})
    if isinstance(approvals, dict):
        value = approvals.get(phase_id, False)
        if isinstance(value, dict):
            return bool(value.get("approved"))
        return bool(value)
    if isinstance(approvals, list):
        return phase_id in approvals
    return False


def _has_active_claim(phase_id: str, digest: str, snapshot: dict[str, Any]) -> bool:
    claims = snapshot.get("claims", [])
    if not isinstance(claims, list):
        return False
    key = f"{phase_id}:{digest}"
    return any(isinstance(claim, dict) and claim.get("idempotency_key") == key and claim.get("active", False) for claim in claims)


def evaluate_plan(plan: dict[str, Any], snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    """Evaluate phase readiness against a normalized evidence snapshot."""
    require_valid_plan(plan)
    snapshot = snapshot or {}
    digest = plan_digest(plan)
    items = snapshot.get("project_items", [])
    pull_requests = snapshot.get("pull_requests", [])
    if not isinstance(items, list) or not isinstance(pull_requests, list):
        raise PlanValidationError("snapshot project_items and pull_requests must be lists")

    by_id = {phase["phase_id"]: phase for phase in plan["phases"]}
    outcomes: dict[str, Evaluation] = {}
    for phase_id in topological_order(plan["phases"]):
        phase = by_id[phase_id]
        dependencies = phase.get("depends_on", [])
        item = _project_item_for_phase(phase_id, items)
        project_status = item.get("status") if item else None
        matching_prs = _pull_requests_for_phase(phase_id, pull_requests)
        pr_numbers = tuple(int(pr.get("number", 0)) for pr in matching_prs if pr.get("number") is not None)
        key = f"{phase_id}:{digest}"

        incomplete_dependencies = [dependency for dependency in dependencies if outcomes[dependency].state != "complete"]
        if incomplete_dependencies:
            outcomes[phase_id] = Evaluation(phase_id, "waiting", "waiting on " + ", ".join(incomplete_dependencies),
                                            item.get("id") if item else None, project_status, pr_numbers, key)
            continue
        if phase.get("approval_required") and not _is_approved(phase_id, snapshot):
            outcomes[phase_id] = Evaluation(phase_id, "blocked", "human approval evidence is required",
                                            item.get("id") if item else None, project_status, pr_numbers, key)
            continue
        if _has_active_claim(phase_id, digest, snapshot):
            outcomes[phase_id] = Evaluation(phase_id, "running", "active idempotent claim exists",
                                            item.get("id") if item else None, project_status, pr_numbers, key)
            continue

        open_prs = [pr for pr in matching_prs if not bool(pr.get("merged")) and str(pr.get("state", "open")).lower() == "open"]
        if open_prs:
            required = phase["completion"]["required_checks"]
            state = "awaiting_review" if _checks_passed(open_prs, required) else "running"
            reason = "linked pull request is awaiting review" if state == "awaiting_review" else "linked pull request is active"
            outcomes[phase_id] = Evaluation(phase_id, state, reason, item.get("id") if item else None,
                                            project_status, pr_numbers, key)
            continue

        merged_prs = [pr for pr in matching_prs if bool(pr.get("merged"))]
        required_checks = phase["completion"]["required_checks"]
        if merged_prs and _checks_passed(merged_prs, required_checks) and project_status == PROJECT_DONE:
            outcomes[phase_id] = Evaluation(phase_id, "complete", "merged PR, required checks, and project status agree",
                                            item.get("id") if item else None, project_status, pr_numbers, key)
            continue
        if project_status == PROJECT_DONE and not merged_prs:
            outcomes[phase_id] = Evaluation(phase_id, "blocked", "project item is Done without linked merged phase PR",
                                            item.get("id") if item else None, project_status, pr_numbers, key)
            continue
        outcomes[phase_id] = Evaluation(phase_id, "ready", "all prerequisites and current evidence permit a claim",
                                        item.get("id") if item else None, project_status, pr_numbers, key)

    return {
        "plan_id": plan["plan_id"],
        "plan_sha256": digest,
        "base_branch": plan["base_branch"],
        "valid": True,
        "topological_order": topological_order(plan["phases"]),
        "evaluations": [outcomes[phase_id].as_dict() for phase_id in topological_order(plan["phases"])],
    }


def _mermaid_label(phase: dict[str, Any], evaluation: dict[str, Any]) -> str:
    title = str(phase["title"]).replace('"', "'")
    return f'{phase["phase_id"]}<br/>{title}<br/>{evaluation["state"]}'


def render_mermaid(plan: dict[str, Any], report: dict[str, Any]) -> str:
    """Render a deterministic Mermaid dependency graph from an evaluation report."""
    evaluation_by_id = {evaluation["phase_id"]: evaluation for evaluation in report["evaluations"]}
    lines = ["flowchart LR"]
    for phase in plan["phases"]:
        evaluation = evaluation_by_id[phase["phase_id"]]
        lines.append(f'  {phase["phase_id"].replace("-", "_")}["{_mermaid_label(phase, evaluation)}"]')
    for phase in plan["phases"]:
        target = phase["phase_id"].replace("-", "_")
        for dependency in phase.get("depends_on", []):
            lines.append(f'  {dependency.replace("-", "_")} --> {target}')
    classes = {
        "complete": "fill:#0f766e,color:#ffffff,stroke:#115e59",
        "ready": "fill:#166534,color:#ffffff,stroke:#14532d",
        "running": "fill:#1d4ed8,color:#ffffff,stroke:#1e3a8a",
        "awaiting_review": "fill:#a16207,color:#ffffff,stroke:#713f12",
        "waiting": "fill:#64748b,color:#ffffff,stroke:#475569",
        "blocked": "fill:#b91c1c,color:#ffffff,stroke:#7f1d1d",
    }
    for state, styling in classes.items():
        members = [phase_id.replace("-", "_") for phase_id, evaluation in evaluation_by_id.items() if evaluation["state"] == state]
        if members:
            lines.append(f"  class {','.join(sorted(members))} {state}")
            lines.append(f"  classDef {state} {styling}")
    return "\n".join(lines) + "\n"


def render_markdown(plan: dict[str, Any], report: dict[str, Any]) -> str:
    """Render a reviewable Markdown status report that embeds the Mermaid graph."""
    evaluation_by_id = {evaluation["phase_id"]: evaluation for evaluation in report["evaluations"]}
    lines = [
        "# Dependency Phase Status",
        "",
        "This file is generated from `docs/agentic/dependency-phases.json` and a normalized evidence snapshot.",
        "Do not edit it as an authority source.",
        "",
        f"**Plan hash:** `{report['plan_sha256']}`",
        "",
        "```mermaid",
        render_mermaid(plan, report).rstrip(),
        "```",
        "",
        "| Phase | State | GitHub Project status | Linked PRs | Reason |",
        "|---|---|---|---|---|",
    ]
    for phase_id in report["topological_order"]:
        evaluation = evaluation_by_id[phase_id]
        prs = ", ".join(f"#{number}" for number in evaluation["pull_requests"]) or "—"
        project_status = evaluation["project_status"] or "unmapped"
        lines.append(f"| `{phase_id}` | **{evaluation['state']}** | {project_status} | {prs} | {evaluation['reason']} |")
    lines.extend([
        "",
        "## Safety boundary",
        "",
        "The chart and report are derived views. Phase completion requires a matching merged PR, the configured checks, and a GitHub Project item in `Done`; agent comments, rendered diagrams, and inferred approvals do not satisfy those conditions.",
        "",
    ])
    return "\n".join(lines)


def write_json(value: dict[str, Any], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
