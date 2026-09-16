#!/usr/bin/env python3
"""Reconcile the managed GitHub Wiki publisher across accessible repositories.

The workflow supplies a job-scoped ``GH_TOKEN`` using the repository's existing
operator-token precedence. The default mode is read-only. ``--apply`` may only
create or update a dedicated branch and reviewable pull request; it never
pushes to a default branch, merges a pull request, overwrites an unmanaged
workflow, or interprets repository discussion content as instructions.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

MANAGED_MARKER = "# managed-by: timerloggedout-spec/repository-surface-reconciler"
MANAGED_WORKFLOW_PATH = ".github/workflows/publish-wiki.yml"
BOT_BRANCH = "automation/wiki-publisher"
BOT_PR_TITLE = "chore(wiki): install managed GitHub Wiki publisher"
SAFE_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
LIVE_READ_ATTEMPTS = 3
ANSI_ESCAPE = re.compile(r"\x1B(?:\[[0-?]*[ -/]*[@-~]|[@-_])")
TRANSIENT_FAILURES = (
    "http 502",
    "http 503",
    "http 504",
    "gateway timeout",
    "secondary rate limit",
    "rate limit exceeded",
    "connection reset",
    "temporarily unavailable",
)


class ReconcilerError(RuntimeError):
    """Raised for a malformed GitHub response or a failed guarded operation."""


class GitHubClient(Protocol):
    def request(
        self,
        method: str,
        endpoint: str,
        *,
        fields: dict[str, str] | None = None,
        attempts: int = 1,
    ) -> Any:
        """Call a GitHub REST endpoint and return parsed JSON."""


class GhClient:
    """A no-colour GitHub CLI client that inherits the job's scoped token."""

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        fields: dict[str, str] | None = None,
        attempts: int = 1,
    ) -> Any:
        if attempts < 1:
            raise ValueError("attempts must be at least one")
        arguments = ["api", "-X", method, endpoint]
        for key, value in (fields or {}).items():
            arguments.extend(["-f", f"{key}={value}"])
        environment = os.environ.copy()
        environment["NO_COLOR"] = "1"
        environment["CLICOLOR"] = "0"
        environment.pop("CLICOLOR_FORCE", None)
        environment.pop("GH_FORCE_TTY", None)
        environment["GH_PAGER"] = "cat"
        for attempt in range(1, attempts + 1):
            result = subprocess.run(
                ["gh", *arguments],
                text=True,
                capture_output=True,
                check=False,
                env=environment,
            )
            if result.returncode == 0:
                try:
                    return json.loads(ANSI_ESCAPE.sub("", result.stdout))
                except json.JSONDecodeError as error:
                    raise ReconcilerError(f"GitHub returned non-JSON for {endpoint}: {error}") from error
            diagnostic = f"{result.stdout}\n{result.stderr}".lower()
            if attempt < attempts and any(item in diagnostic for item in TRANSIENT_FAILURES):
                time.sleep(2 ** (attempt - 1))
                continue
            raise ReconcilerError(
                f"GitHub request {method} {endpoint} failed: {result.stderr.strip() or result.stdout.strip()}"
            )
        raise AssertionError("unreachable")


@dataclass(frozen=True)
class Repository:
    full_name: str
    default_branch: str
    archived: bool
    fork: bool
    visibility: str


@dataclass
class Finding:
    repository: str
    default_branch: str
    state: str
    operation: str
    detail: str
    pull_request: str | None = None


def _require_mapping(value: Any, operation: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReconcilerError(f"{operation} did not return an object")
    return value


def _validate_repository(full_name: str) -> str:
    if not SAFE_REPOSITORY.fullmatch(full_name):
        raise ReconcilerError(f"unsafe repository name returned by GitHub: {full_name!r}")
    return full_name


def list_accessible_repositories(client: GitHubClient) -> list[Repository]:
    """List all repositories visible to the job's existing operator token.

    The endpoint includes user-owned repositories and repositories available
    through organization membership or collaboration. It is intentionally a
    credential-scoped inventory rather than an assumed enterprise-wide list.
    """
    repositories: list[Repository] = []
    page = 1
    while True:
        rows = client.request(
            "GET",
            f"user/repos?affiliation=owner,organization_member,collaborator&sort=full_name&per_page=100&page={page}",
            attempts=LIVE_READ_ATTEMPTS,
        )
        if not isinstance(rows, list):
            raise ReconcilerError("accessible repository list did not return an array")
        for row in rows:
            if not isinstance(row, dict):
                continue
            full_name = row.get("full_name")
            default_branch = row.get("default_branch")
            if not isinstance(full_name, str) or not isinstance(default_branch, str):
                continue
            repositories.append(
                Repository(
                    full_name=_validate_repository(full_name),
                    default_branch=default_branch,
                    archived=bool(row.get("archived")),
                    fork=bool(row.get("fork")),
                    visibility=str(row.get("visibility", "unknown")),
                )
            )
        if len(rows) < 100:
            break
        page += 1
    return sorted(repositories, key=lambda record: record.full_name.lower())


def _decode_content(payload: dict[str, Any]) -> str:
    encoding = payload.get("encoding")
    content = payload.get("content")
    if encoding != "base64" or not isinstance(content, str):
        raise ReconcilerError("workflow content response was not base64")
    try:
        normalized = re.sub(r"\s+", "", content)
        return base64.b64decode(normalized, validate=True).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as error:
        raise ReconcilerError("workflow content response could not be decoded") from error


def _content(client: GitHubClient, repository: str, branch: str) -> tuple[str, str] | None:
    try:
        payload = _require_mapping(
            client.request(
                "GET",
                f"repos/{repository}/contents/{MANAGED_WORKFLOW_PATH}?ref={branch}",
                attempts=LIVE_READ_ATTEMPTS,
            ),
            "workflow content lookup",
        )
    except ReconcilerError as error:
        if "http 404" in str(error).lower() or "not found" in str(error).lower():
            return None
        raise
    sha = payload.get("sha")
    if not isinstance(sha, str) or not sha:
        raise ReconcilerError("workflow content response did not contain a blob SHA")
    return _decode_content(payload), sha


def _workflow_state(current: tuple[str, str] | None, expected: str) -> tuple[str, str]:
    if current is None:
        return "missing", "The managed publisher workflow is absent."
    content, _ = current
    if content == expected:
        return "current", "The managed publisher workflow exactly matches the canonical source."
    if MANAGED_MARKER not in content:
        return "unmanaged", "A publisher workflow exists but is not managed by this reconciler; it will not be overwritten."
    return "drifted", "A managed publisher workflow differs from the canonical source."


def _branch_ref(client: GitHubClient, repository: str, branch: str) -> str | None:
    try:
        payload = _require_mapping(
            client.request("GET", f"repos/{repository}/git/ref/heads/{branch}", attempts=LIVE_READ_ATTEMPTS),
            "branch lookup",
        )
    except ReconcilerError as error:
        if "http 404" in str(error).lower() or "not found" in str(error).lower():
            return None
        raise
    object_value = payload.get("object")
    if not isinstance(object_value, dict) or not isinstance(object_value.get("sha"), str):
        raise ReconcilerError("branch lookup did not return a commit SHA")
    return str(object_value["sha"])


def _open_pr(client: GitHubClient, repository: str, owner: str) -> dict[str, Any] | None:
    payload = client.request(
        "GET",
        f"repos/{repository}/pulls?state=open&head={owner}:{BOT_BRANCH}&per_page=10",
        attempts=LIVE_READ_ATTEMPTS,
    )
    if not isinstance(payload, list):
        raise ReconcilerError("pull request lookup did not return an array")
    for row in payload:
        if isinstance(row, dict) and row.get("title") == BOT_PR_TITLE:
            return row
    return None


def _create_branch_if_needed(client: GitHubClient, repository: Repository) -> None:
    if _branch_ref(client, repository.full_name, BOT_BRANCH) is not None:
        return
    base_sha = _branch_ref(client, repository.full_name, repository.default_branch)
    if base_sha is None:
        raise ReconcilerError(f"default branch {repository.default_branch!r} was not found")
    try:
        client.request(
            "POST",
            f"repos/{repository.full_name}/git/refs",
            fields={"ref": f"refs/heads/{BOT_BRANCH}", "sha": base_sha},
        )
    except ReconcilerError as error:
        if "reference already exists" not in str(error).lower() and "http 422" not in str(error).lower():
            raise


def _write_and_open_pr(
    client: GitHubClient,
    repository: Repository,
    canonical_workflow: str,
) -> str:
    owner = repository.full_name.split("/", 1)[0]
    existing_pr = _open_pr(client, repository.full_name, owner)
    branch_exists = _branch_ref(client, repository.full_name, BOT_BRANCH) is not None
    branch_content = _content(client, repository.full_name, BOT_BRANCH) if branch_exists else None
    if branch_exists:
        if branch_content is not None and MANAGED_MARKER not in branch_content[0]:
            raise ReconcilerError("the reserved automation branch contains an unmanaged workflow")
        if branch_content is None and existing_pr is not None:
            raise ReconcilerError("the reserved automation branch lost its managed workflow")
    else:
        _create_branch_if_needed(client, repository)

    fields = {
        "message": "chore(wiki): reconcile managed publisher workflow",
        "content": base64.b64encode(canonical_workflow.encode("utf-8")).decode("ascii"),
        "branch": BOT_BRANCH,
    }
    if branch_content is not None:
        fields["sha"] = branch_content[1]
    client.request("PUT", f"repos/{repository.full_name}/contents/{MANAGED_WORKFLOW_PATH}", fields=fields)

    if existing_pr is not None:
        url = existing_pr.get("html_url")
        if isinstance(url, str) and url:
            return url
        raise ReconcilerError("existing pull request did not return a URL")

    response = _require_mapping(
        client.request(
            "POST",
            f"repos/{repository.full_name}/pulls",
            fields={
                "title": BOT_PR_TITLE,
                "head": BOT_BRANCH,
                "base": repository.default_branch,
                "body": (
                    "This pull request is generated by the repository-surface reconciler.\n\n"
                    "It installs or updates only the managed GitHub Wiki publisher. "
                    "It never merges automatically.\n\n"
                    "Implements: AR-09"
                ),
            },
        ),
        "pull request creation",
    )
    url = response.get("html_url")
    if not isinstance(url, str) or not url:
        raise ReconcilerError("pull request creation did not return a URL")
    return url


def reconcile(
    client: GitHubClient,
    *,
    source_repository: str,
    canonical_workflow: str,
    apply: bool,
) -> list[Finding]:
    """Classify each accessible repository and optionally open reviewable PRs."""
    _validate_repository(source_repository)
    if MANAGED_MARKER not in canonical_workflow:
        raise ReconcilerError(f"canonical workflow must contain {MANAGED_MARKER!r}")
    findings: list[Finding] = []
    for repository in list_accessible_repositories(client):
        if repository.full_name == source_repository:
            findings.append(Finding(repository.full_name, repository.default_branch, "excluded", "none", "Control-plane repository."))
            continue
        if repository.archived:
            findings.append(Finding(repository.full_name, repository.default_branch, "excluded", "none", "Archived repository."))
            continue
        current = _content(client, repository.full_name, repository.default_branch)
        state, detail = _workflow_state(current, canonical_workflow)
        finding = Finding(repository.full_name, repository.default_branch, state, "report", detail)
        if state in {"missing", "drifted"} and apply:
            try:
                finding.pull_request = _write_and_open_pr(client, repository, canonical_workflow)
                finding.operation = "pull_request"
                finding.detail = "Opened or updated the dedicated reviewable automation pull request."
            except ReconcilerError as error:
                finding.state = "blocked"
                finding.operation = "none"
                finding.detail = str(error)
        findings.append(finding)
    return findings


def _report(findings: list[Finding], *, source_repository: str, apply: bool) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.state] = counts.get(finding.state, 0) + 1
    return {
        "schema_version": 2,
        "source_repository": source_repository,
        "credential_lane": "operator-token",
        "managed_workflow_path": MANAGED_WORKFLOW_PATH,
        "mode": "apply" if apply else "dry_run",
        "counts": counts,
        "findings": [asdict(finding) for finding in findings],
    }


def _summary_report(report: dict[str, Any]) -> dict[str, Any]:
    """Return an artifact-safe projection with no repository identifiers or details."""
    findings = report.get("findings", [])
    operations: dict[str, int] = {}
    if isinstance(findings, list):
        for finding in findings:
            if isinstance(finding, dict):
                operation = str(finding.get("operation", "unknown"))
                operations[operation] = operations.get(operation, 0) + 1
    return {
        "schema_version": report.get("schema_version"),
        "credential_lane": report.get("credential_lane"),
        "mode": report.get("mode"),
        "counts": report.get("counts", {}),
        "operations": operations,
        "repository_count": len(findings) if isinstance(findings, list) else 0,
        "redaction": "Repository names, branches, PR URLs, and diagnostic details are intentionally omitted.",
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", required=True, help="Canonical control-plane repository, OWNER/REPO.")
    parser.add_argument(
        "--source-workflow",
        default=MANAGED_WORKFLOW_PATH,
        help="Canonical workflow path relative to the repository root.",
    )
    parser.add_argument("--report", required=True, help="Path for the detailed local JSON reconciliation report.")
    parser.add_argument("--summary-report", help="Optional path for an artifact-safe aggregate report without repository identifiers.")
    parser.add_argument("--apply", action="store_true", help="Create or update reviewable pull requests; never merge.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    workflow_path = Path(args.source_workflow)
    if workflow_path.is_absolute() or ".." in workflow_path.parts:
        raise ReconcilerError("source workflow must be a repository-relative path")
    if not os.environ.get("GH_TOKEN"):
        raise ReconcilerError("GH_TOKEN is required; supply the workflow's existing operator-token precedence")
    canonical_workflow = workflow_path.read_text(encoding="utf-8")
    findings = reconcile(
        GhClient(),
        source_repository=args.source_repo,
        canonical_workflow=canonical_workflow,
        apply=bool(args.apply),
    )
    report = _report(findings, source_repository=args.source_repo, apply=bool(args.apply))
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.summary_report:
        summary_path = Path(args.summary_report)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(_summary_report(report), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mode": report["mode"], "counts": report["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReconcilerError as error:
        print(f"reconciliation error: {error}", file=sys.stderr)
        raise SystemExit(2)
