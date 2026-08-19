#!/usr/bin/env python3
"""GitHub CLI adapter for the dependency-phase lifecycle system.

All mutating operations require ``apply=True``. The default mode only computes
an auditable reconciliation plan from live GitHub data.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from typing import Any

ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
CLAIM_PREFIX = "<!-- dependency-phase-claim:"
CLAIM_MARKER = re.compile(r"<!--\s*dependency-phase-claim:\s*([A-Z][A-Z0-9-]{2,63}:[0-9a-f]{64})\s*-->")
LIVE_READ_ATTEMPTS = 3
TRANSIENT_GH_FAILURES = (
    "http 502",
    "http 503",
    "http 504",
    "gateway timeout",
    "secondary rate limit",
    "rate limit exceeded",
    "connection reset",
    "temporarily unavailable",
)


class GitHubAdapterError(RuntimeError):
    """Raised for a failed GitHub CLI operation."""


@dataclass(frozen=True)
class CommandResult:
    stdout: str
    stderr: str


def _clean(value: str) -> str:
    return ANSI.sub("", value)


def _is_transient_failure(stdout: str, stderr: str) -> bool:
    diagnostic = f"{stdout}\n{stderr}".lower()
    return any(marker in diagnostic for marker in TRANSIENT_GH_FAILURES)


def run_gh(
    arguments: list[str],
    *,
    input_text: str | None = None,
    attempts: int = 1,
    retry_backoff_seconds: float = 1.0,
) -> CommandResult:
    """Run gh in no-color mode, retrying only explicitly opted-in transient reads."""
    if attempts < 1:
        raise ValueError("attempts must be at least one")
    environment = os.environ.copy()
    environment["NO_COLOR"] = "1"
    environment["CLICOLOR"] = "0"
    for attempt in range(1, attempts + 1):
        process = subprocess.run(
            ["gh", *arguments],
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )
        stdout = _clean(process.stdout)
        stderr = _clean(process.stderr)
        if process.returncode == 0:
            return CommandResult(stdout=stdout, stderr=stderr)
        if attempt < attempts and _is_transient_failure(stdout, stderr):
            time.sleep(retry_backoff_seconds * (2 ** (attempt - 1)))
            continue
        raise GitHubAdapterError(f"gh {' '.join(arguments)} failed: {stderr.strip() or stdout.strip()}")
    raise AssertionError("unreachable")


def json_gh(arguments: list[str], *, attempts: int = 1) -> dict[str, Any]:
    result = run_gh(arguments, attempts=attempts)
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise GitHubAdapterError(f"gh did not return JSON: {error}") from error
    if not isinstance(value, dict):
        raise GitHubAdapterError("gh JSON response must be an object")
    return value


def list_gh(arguments: list[str], *, attempts: int = 1) -> list[dict[str, Any]]:
    """Return a JSON array from a read-only gh command."""
    result = run_gh(arguments, attempts=attempts)
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise GitHubAdapterError(f"gh did not return JSON: {error}") from error
    if not isinstance(value, list):
        raise GitHubAdapterError("gh JSON response must be an array")
    return [item for item in value if isinstance(item, dict)]


def project_items(owner: str, number: int, limit: int = 500) -> list[dict[str, Any]]:
    response = json_gh(
        ["project", "item-list", str(number), "--owner", owner, "--limit", str(limit), "--format", "json"],
        attempts=LIVE_READ_ATTEMPTS,
    )
    items = response.get("items", [])
    if not isinstance(items, list):
        raise GitHubAdapterError("project item list did not contain an items array")
    return [item for item in items if isinstance(item, dict)]


def _normalise_checks(raw_checks: Any) -> dict[str, str]:
    checks: dict[str, str] = {}
    if not isinstance(raw_checks, list):
        return checks
    for check in raw_checks:
        if not isinstance(check, dict):
            continue
        name = check.get("name") or check.get("context")
        state = check.get("conclusion") or check.get("state") or check.get("status")
        if isinstance(name, str) and state is not None:
            checks[name] = str(state)
    return checks


def _rest_commit_checks(repo: str, ref: str) -> dict[str, str]:
    """Collect check-run and legacy status evidence for one pull-request head."""
    check_runs = json_gh(
        ["api", "-X", "GET", f"repos/{repo}/commits/{ref}/check-runs?per_page=100"],
        attempts=LIVE_READ_ATTEMPTS,
    )
    combined_status = json_gh(
        ["api", "-X", "GET", f"repos/{repo}/commits/{ref}/status?per_page=100"],
        attempts=LIVE_READ_ATTEMPTS,
    )
    checks = _normalise_checks(check_runs.get("check_runs"))
    checks.update(_normalise_checks(combined_status.get("statuses")))
    return checks


def _phase_evidence_matches(row: dict[str, Any], phase_ids: set[str]) -> bool:
    text = f"{row.get('title', '')}\n{row.get('body', '')}"
    return any(phase_id in text for phase_id in phase_ids)


def pull_requests(
    repo: str,
    base_branch: str,
    limit: int = 200,
    phase_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Read PR metadata from REST and checks only for canonical phase evidence.

    ``gh pr list`` obtains GraphQL's expensive ``statusCheckRollup`` aggregate,
    which can time out on large repositories. These REST resources preserve the
    lifecycle evidence contract while avoiding that aggregate query.
    """
    page_size = min(100, max(1, limit))
    rows: list[dict[str, Any]] = []
    for page in range(1, (limit + page_size - 1) // page_size + 1):
        page_rows = list_gh(
            [
                "api", "-X", "GET",
                f"repos/{repo}/pulls?state=all&base={base_branch}&per_page={page_size}&page={page}",
            ],
            attempts=LIVE_READ_ATTEMPTS,
        )
        rows.extend(page_rows)
        if len(page_rows) < page_size:
            break

    linked_phase_ids = {phase_id for phase_id in (phase_ids or []) if isinstance(phase_id, str)}
    normalized: list[dict[str, Any]] = []
    for row in rows[:limit]:
        head = row.get("head")
        ref = head.get("sha") if isinstance(head, dict) else None
        checks: dict[str, str] = {}
        if isinstance(ref, str) and _phase_evidence_matches(row, linked_phase_ids):
            checks = _rest_commit_checks(repo, ref)
        normalized.append({
            "number": row.get("number"),
            "title": row.get("title", ""),
            "body": row.get("body", ""),
            "state": str(row.get("state", "")).lower(),
            "merged": bool(row.get("merged_at")),
            "url": row.get("html_url"),
            "checks": checks,
        })
    return normalized


def issues(repo: str, limit: int = 300) -> list[dict[str, Any]]:
    """Return repository issues in a normalized shape for phase reconciliation."""
    response = run_gh([
        "issue", "list", "--repo", repo, "--state", "all", "--limit", str(limit),
        "--json", "number,title,body,state,url",
    ], attempts=LIVE_READ_ATTEMPTS)
    try:
        rows = json.loads(response.stdout)
    except json.JSONDecodeError as error:
        raise GitHubAdapterError(f"unable to parse issue inventory: {error}") from error
    if not isinstance(rows, list):
        raise GitHubAdapterError("issue response must be an array")
    return [row for row in rows if isinstance(row, dict)]


def issue_comments(repo: str, issue_number: int) -> list[dict[str, Any]]:
    response = run_gh(
        ["api", f"repos/{repo}/issues/{issue_number}/comments", "--paginate"],
        attempts=LIVE_READ_ATTEMPTS,
    )
    try:
        value = json.loads(response.stdout)
    except json.JSONDecodeError as error:
        raise GitHubAdapterError(f"unable to parse issue comments: {error}") from error
    if not isinstance(value, list):
        raise GitHubAdapterError("issue comments response must be an array")
    return [item for item in value if isinstance(item, dict)]


def create_issue(repo: str, title: str, body: str, *, apply: bool) -> dict[str, Any]:
    if not apply:
        return {"planned": True, "operation": "create_issue", "title": title}
    response = run_gh(["issue", "create", "--repo", repo, "--title", title, "--body", body])
    url = response.stdout.strip()
    match = re.search(r"/(?:issues|pull)/(\d+)$", url)
    if not match:
        raise GitHubAdapterError(f"unable to identify issue number from gh output: {url}")
    return {"planned": False, "operation": "create_issue", "number": int(match.group(1)), "url": url}


def add_issue_to_project(owner: str, number: int, issue_url: str, *, apply: bool) -> dict[str, Any]:
    if not apply:
        return {"planned": True, "operation": "add_project_item", "url": issue_url}
    # Do not request formatted mutation output here. For user-owned Projects, gh
    # can complete addProjectV2ItemById and then fail its follow-up formatting
    # query for lack of read scope, incorrectly reporting a failed mutation.
    run_gh(["project", "item-add", str(number), "--owner", owner, "--url", issue_url])
    return {"planned": False, "operation": "add_project_item", "url": issue_url}


def set_project_status(project_id: str, item_id: str, status_field_id: str, option_id: str, *, apply: bool) -> dict[str, Any]:
    if not apply:
        return {"planned": True, "operation": "set_project_status", "item_id": item_id, "option_id": option_id}
    run_gh([
        "project", "item-edit", "--project-id", project_id, "--id", item_id,
        "--field-id", status_field_id, "--single-select-option-id", option_id,
    ])
    return {"planned": False, "operation": "set_project_status", "item_id": item_id, "option_id": option_id}


def post_issue_comment(repo: str, issue_number: int, body: str, *, apply: bool) -> dict[str, Any]:
    if not apply:
        return {"planned": True, "operation": "post_issue_comment", "issue": issue_number}
    response = run_gh(["issue", "comment", str(issue_number), "--repo", repo, "--body", body])
    return {"planned": False, "operation": "post_issue_comment", "url": response.stdout.strip()}


def active_claim_records(comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize durable active claim markers from GitHub issue comments."""
    records: dict[str, dict[str, Any]] = {}
    for comment in comments:
        if not isinstance(comment, dict):
            continue
        body = str(comment.get("body", ""))
        for match in CLAIM_MARKER.finditer(body):
            key = match.group(1)
            records[key] = {
                "idempotency_key": key,
                "active": True,
                "comment_id": comment.get("id"),
                "issue_url": comment.get("issue_url"),
            }
    return [records[key] for key in sorted(records)]


def claim_exists(comments: list[dict[str, Any]], idempotency_key: str) -> bool:
    return any(record["idempotency_key"] == idempotency_key for record in active_claim_records(comments))


def phase_issue_title(phase: dict[str, Any]) -> str:
    return f"[{phase['phase_id']}] {phase['title']}"


def phase_issue_matches(plan: dict[str, Any], phase: dict[str, Any], candidate: dict[str, Any]) -> bool:
    """Require the exact generated title and durable plan/phase markers for a phase issue."""
    title = str(candidate.get("title", "")).strip()
    body = str(candidate.get("body", ""))
    return (
        title == phase_issue_title(phase)
        and f"**Plan:** `{plan['plan_id']}`" in body
        and f"**Phase:** `{phase['phase_id']}`" in body
    )


def phase_issue_body(plan: dict[str, Any], phase: dict[str, Any], plan_sha256: str) -> str:
    prerequisites = ", ".join(phase.get("depends_on", [])) or "None"
    checks = ", ".join(phase["completion"]["required_checks"])
    return "\n".join([
        "## Dependency phase",
        "",
        f"**Plan:** `{plan['plan_id']}`",
        f"**Phase:** `{phase['phase_id']}`",
        f"**Plan hash:** `{plan_sha256}`",
        f"**Prerequisites:** {prerequisites}",
        f"**Required checks:** {checks}",
        f"**Approval required:** {'yes' if phase.get('approval_required') else 'no'}",
        "",
        "This issue is managed by the repository dependency-phase system. Its GitHub Project status is a derived coordination view; lifecycle eligibility remains determined by the versioned plan and objective evidence.",
        "",
        f"Implements: {phase['phase_id']}",
    ])
