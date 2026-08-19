#!/usr/bin/env python3
"""Dependency-phase lifecycle command line interface.

Examples:
  python3 scripts/agentic/dependency_phases.py validate
  python3 scripts/agentic/dependency_phases.py render --snapshot tests/fixtures/dependency_phases/ready.json
  python3 scripts/agentic/dependency_phases.py evaluate --live --repo timerloggedout-spec/termux-monorepo
  python3 scripts/agentic/dependency_phases.py sync-project --repo timerloggedout-spec/termux-monorepo

All GitHub mutations require an explicit ``--apply`` flag. The default behavior
is a dry run that prints the exact operations it would perform.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from dependency_phase_engine import (
    PlanValidationError,
    evaluate_plan,
    load_json,
    plan_digest,
    render_markdown,
    render_mermaid,
    require_valid_plan,
    write_json,
)
from github_phase_adapter import (
    CLAIM_PREFIX,
    GitHubAdapterError,
    active_claim_records,
    add_issue_to_project,
    claim_exists,
    create_issue,
    issue_comments,
    issues,
    phase_issue_body,
    phase_issue_matches,
    phase_issue_title,
    post_issue_comment,
    project_items,
    pull_requests,
    set_project_status,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLAN = ROOT / "docs" / "agentic" / "dependency-phases.json"
DEFAULT_APPROVALS = ROOT / "docs" / "agentic" / "phase-approvals.json"
DEFAULT_REPORT = ROOT / "docs" / "agentic" / "DEPENDENCY_PHASES.md"
DEFAULT_MERMAID = ROOT / "docs" / "agentic" / "dependency-phases.mmd"


class CommandError(RuntimeError):
    """Raised for a requested operation that is not currently permitted."""


def _load_approvals(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = load_json(path)
    approvals = value.get("approvals", value)
    return approvals if isinstance(approvals, dict) else {}


def _load_snapshot(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"project_items": [], "pull_requests": [], "approvals": {}}
    snapshot = load_json(path)
    snapshot.setdefault("project_items", [])
    snapshot.setdefault("pull_requests", [])
    snapshot.setdefault("approvals", {})
    snapshot.setdefault("claims", [])
    return snapshot


def live_snapshot(plan: dict[str, Any], repo: str, approvals_path: Path) -> dict[str, Any]:
    """Read live Project, PR, approval, and canonical issue-claim evidence."""
    project = plan["project"]
    live_issues = issues(repo)
    claims: list[dict[str, Any]] = []
    for phase in plan["phases"]:
        canonical = [candidate for candidate in live_issues if phase_issue_matches(plan, phase, candidate)]
        if len(canonical) > 1:
            raise CommandError(f"multiple canonical issues found for {phase['phase_id']}")
        if canonical:
            claims.extend(active_claim_records(issue_comments(repo, int(canonical[0]["number"]))))
    return {
        "project_items": project_items(project["owner"], int(project["number"])),
        "pull_requests": pull_requests(
            repo,
            plan["base_branch"],
            phase_ids=[str(phase["phase_id"]) for phase in plan["phases"]],
        ),
        "approvals": _load_approvals(approvals_path),
        "claims": claims,
    }


def _phase_by_id(plan: dict[str, Any], phase_id: str) -> dict[str, Any]:
    for phase in plan["phases"]:
        if phase["phase_id"] == phase_id:
            return phase
    raise CommandError(f"unknown phase_id: {phase_id}")


def _project_item_for_phase(phase_id: str, items: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Resolve a Project item only from an exact canonical title marker."""
    pattern = re.compile(rf"(?<![A-Z0-9-]){re.escape(phase_id)}(?![A-Z0-9-])")
    matches: list[dict[str, Any]] = []
    for item in items:
        content = item.get("content")
        titles = [str(item.get("title", ""))]
        if isinstance(content, dict):
            titles.append(str(content.get("title", "")))
        if any(pattern.search(title) for title in titles):
            matches.append(item)
    if len(matches) > 1:
        raise CommandError(f"multiple Project items found for {phase_id}")
    return matches[0] if matches else None


def _desired_project_status(state: str) -> str:
    if state == "complete":
        return "Done"
    if state in {"running", "awaiting_review"}:
        return "In progress"
    return "Todo"


def sync_project(plan: dict[str, Any], report: dict[str, Any], repo: str, *, apply: bool) -> dict[str, Any]:
    """Build or apply a project reconciliation plan for all lifecycle phases."""
    project = plan["project"]
    operations: list[dict[str, Any]] = []
    evaluation_by_id = {entry["phase_id"]: entry for entry in report["evaluations"]}
    live_items = project_items(project["owner"], int(project["number"]))
    live_issues = issues(repo)
    digest = plan_digest(plan)

    for phase in plan["phases"]:
        phase_id = phase["phase_id"]
        evaluation = evaluation_by_id[phase_id]
        item = _project_item_for_phase(phase_id, live_items)
        desired_status = _desired_project_status(evaluation["state"])
        canonical_issues = [candidate for candidate in live_issues if phase_issue_matches(plan, phase, candidate)]
        if len(canonical_issues) > 1:
            raise CommandError(f"multiple canonical issues found for {phase_id}")
        issue = canonical_issues[0] if canonical_issues else None
        if item is None:
            if issue is None:
                issue_result = create_issue(repo, phase_issue_title(phase), phase_issue_body(plan, phase, digest), apply=apply)
                operations.append({"phase_id": phase_id, **issue_result})
                if not apply:
                    continue
                issue_url = issue_result["url"]
            else:
                issue_url = str(issue["url"])
                operations.append({
                    "phase_id": phase_id,
                    "operation": "reuse_existing_issue",
                    "issue": issue.get("number"),
                    "url": issue_url,
                })
            item_result = add_issue_to_project(project["owner"], int(project["number"]), issue_url, apply=apply)
            operations.append({"phase_id": phase_id, **item_result})
            continue
        current_status = item.get("status")
        if current_status != desired_status:
            operation = set_project_status(
                project["id"], item["id"], project["status_field_id"], project["status_options"][desired_status], apply=apply
            )
            operations.append({"phase_id": phase_id, "from": current_status, "to": desired_status, **operation})
        else:
            operations.append({"phase_id": phase_id, "operation": "no_change", "status": current_status})
    return {"apply": apply, "project_url": project["url"], "operations": operations}


def dispatch_claim(plan: dict[str, Any], report: dict[str, Any], repo: str, phase_id: str, issue_number: int, *, apply: bool) -> dict[str, Any]:
    """Create one idempotent issue-backed phase claim after evaluating readiness."""
    evaluation = next((entry for entry in report["evaluations"] if entry["phase_id"] == phase_id), None)
    if evaluation is None:
        raise CommandError(f"phase {phase_id} was not evaluated")
    if evaluation["state"] != "ready":
        raise CommandError(f"phase {phase_id} is {evaluation['state']}: {evaluation['reason']}")
    phase = _phase_by_id(plan, phase_id)
    canonical_issues = [candidate for candidate in issues(repo) if phase_issue_matches(plan, phase, candidate)]
    if len(canonical_issues) != 1:
        raise CommandError(f"expected exactly one canonical issue for {phase_id}, found {len(canonical_issues)}")
    canonical_issue = canonical_issues[0]
    canonical_number = int(canonical_issue["number"])
    if issue_number != canonical_number:
        raise CommandError(f"issue #{issue_number} is not the canonical issue for {phase_id}; expected #{canonical_number}")
    comments = issue_comments(repo, canonical_number)
    key = evaluation["idempotency_key"]
    if claim_exists(comments, key):
        return {"phase_id": phase_id, "claimed": False, "reason": "idempotency key already claimed", "idempotency_key": key}
    body = "\n".join([
        f"{CLAIM_PREFIX} {key} -->",
        f"Dependency phase `{phase_id}` is claimed against plan `{plan['plan_id']}`.",
        f"Plan hash: `{report['plan_sha256']}`.",
        "The dispatcher revalidated prerequisites, approval evidence, current PR state, and project evidence before recording this claim.",
    ])
    result = post_issue_comment(repo, canonical_number, body, apply=apply)
    return {"phase_id": phase_id, "claimed": bool(apply), "idempotency_key": key, **result}


def _parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN, help="canonical dependency-phase JSON plan")
    parser.add_argument("--snapshot", type=Path, help="offline normalized evidence snapshot JSON")
    parser.add_argument("--approvals", type=Path, default=DEFAULT_APPROVALS, help="repository approval evidence JSON")
    parser.add_argument("--repo", default="timerloggedout-spec/termux-monorepo", help="GitHub owner/repository")
    parser.add_argument("--live", action="store_true", help="read current GitHub Project and pull-request evidence")
    parser.add_argument("--apply", action="store_true", help="apply an otherwise dry-run GitHub mutation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="validate the canonical plan")
    evaluate = subparsers.add_parser("evaluate", help="evaluate phase lifecycle state")
    evaluate.add_argument("--output", type=Path, help="write JSON report")
    render = subparsers.add_parser("render", help="generate Mermaid and Markdown derived views")
    render.add_argument("--markdown-output", type=Path, default=DEFAULT_REPORT)
    render.add_argument("--mermaid-output", type=Path, default=DEFAULT_MERMAID)
    render.add_argument("--report-output", type=Path, help="write JSON report")
    subparsers.add_parser("sync-project", help="dry-run or apply GitHub Projects reconciliation")
    dispatch = subparsers.add_parser("dispatch", help="dry-run or record one idempotent phase claim")
    dispatch.add_argument("--phase-id", required=True)
    dispatch.add_argument("--issue", required=True, type=int)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    arguments = _parse_arguments(argv or sys.argv[1:])
    try:
        plan = load_json(arguments.plan)
        require_valid_plan(plan)
        snapshot = live_snapshot(plan, arguments.repo, arguments.approvals) if arguments.live else _load_snapshot(arguments.snapshot)
        if not arguments.live:
            snapshot["approvals"] = snapshot.get("approvals") or _load_approvals(arguments.approvals)
        report = evaluate_plan(plan, snapshot)

        if arguments.command == "validate":
            print(json.dumps({"valid": True, "plan_id": plan["plan_id"], "plan_sha256": report["plan_sha256"]}, indent=2))
            return 0
        if arguments.command == "evaluate":
            if arguments.output:
                write_json(report, arguments.output)
            print(json.dumps(report, indent=2))
            return 0
        if arguments.command == "render":
            arguments.markdown_output.write_text(render_markdown(plan, report), encoding="utf-8")
            arguments.mermaid_output.write_text(render_mermaid(plan, report), encoding="utf-8")
            if arguments.report_output:
                write_json(report, arguments.report_output)
            print(json.dumps({"markdown": str(arguments.markdown_output), "mermaid": str(arguments.mermaid_output), "plan_sha256": report["plan_sha256"]}, indent=2))
            return 0
        if arguments.command == "sync-project":
            if not arguments.live:
                raise CommandError("sync-project requires --live so it cannot mutate a stale snapshot")
            print(json.dumps(sync_project(plan, report, arguments.repo, apply=arguments.apply), indent=2))
            return 0
        if arguments.command == "dispatch":
            if not arguments.live:
                raise CommandError("dispatch requires --live so readiness is revalidated before claiming")
            print(json.dumps(dispatch_claim(plan, report, arguments.repo, arguments.phase_id, arguments.issue, apply=arguments.apply), indent=2))
            return 0
        raise CommandError(f"unknown command: {arguments.command}")
    except (PlanValidationError, GitHubAdapterError, CommandError, OSError, json.JSONDecodeError) as error:
        print(f"dependency phase error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
