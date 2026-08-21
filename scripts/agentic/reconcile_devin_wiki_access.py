#!/usr/bin/env python3
"""Reconcile supported Devin GitHub App access for accessible repositories.

The workflow supplies the established job-scoped operator-token lane. Scheduled
runs may add repositories to an already installed Devin GitHub App only through
GitHub's documented ``PUT /user/installations/{installation_id}/repositories/{repository_id}``
endpoint. The controller does not use browser automation, provider-private
endpoints, or an undocumented DeepWiki trigger.

Granting GitHub App access makes a repository eligible for provider-managed
Devin Wiki indexing. It does not prove that a public DeepWiki page has indexed
or refreshed; the report records that boundary explicitly.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from reconcile_repository_surface import (
    GhClient,
    LIVE_READ_ATTEMPTS,
    ReconcilerError,
    SAFE_REPOSITORY,
    _require_mapping,
)

DEVIN_APP_SLUG = "devin-ai-integration"


@dataclass(frozen=True)
class Repository:
    repository_id: int
    full_name: str
    default_branch: str
    archived: bool


@dataclass(frozen=True)
class Installation:
    installation_id: int
    account_login: str
    repository_selection: str


@dataclass
class Finding:
    repository: str
    state: str
    operation: str
    detail: str
    installation_id: int | None = None


def _validate_repository(full_name: str) -> str:
    if not SAFE_REPOSITORY.fullmatch(full_name):
        raise ReconcilerError(f"unsafe repository name returned by GitHub: {full_name!r}")
    return full_name


def _owner(full_name: str) -> str:
    return full_name.split("/", 1)[0].lower()


def _require_integer(value: Any, operation: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ReconcilerError(f"{operation} did not return a positive integer")
    return value


def list_accessible_repositories(client: GhClient) -> list[Repository]:
    """Return the existing operator token's complete credential-scoped inventory."""
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
                    repository_id=_require_integer(row.get("id"), "repository list"),
                    full_name=_validate_repository(full_name),
                    default_branch=default_branch,
                    archived=bool(row.get("archived")),
                )
            )
        if len(rows) < 100:
            break
        page += 1
    return sorted(repositories, key=lambda record: record.full_name.lower())


def list_devin_installations(client: GhClient) -> list[Installation]:
    """Find Devin App installations visible to the existing user token."""
    payload = _require_mapping(
        client.request("GET", "user/installations?per_page=100", attempts=LIVE_READ_ATTEMPTS),
        "Devin installation lookup",
    )
    rows = payload.get("installations")
    if not isinstance(rows, list):
        raise ReconcilerError("Devin installation lookup did not return an installation array")
    installations: list[Installation] = []
    for row in rows:
        if not isinstance(row, dict) or row.get("app_slug") != DEVIN_APP_SLUG:
            continue
        account = row.get("account")
        if not isinstance(account, dict) or not isinstance(account.get("login"), str):
            raise ReconcilerError("Devin installation did not include its target account")
        selection = row.get("repository_selection")
        if selection not in {"all", "selected"}:
            raise ReconcilerError("Devin installation did not include a supported repository selection")
        installations.append(
            Installation(
                installation_id=_require_integer(row.get("id"), "Devin installation lookup"),
                account_login=str(account["login"]),
                repository_selection=str(selection),
            )
        )
    return installations


def list_installation_repository_ids(client: GhClient, installation_id: int) -> set[int]:
    """List repositories currently assigned to one selected-repository installation."""
    repository_ids: set[int] = set()
    page = 1
    while True:
        payload = _require_mapping(
            client.request(
                "GET",
                f"user/installations/{installation_id}/repositories?per_page=100&page={page}",
                attempts=LIVE_READ_ATTEMPTS,
            ),
            "Devin installation repository lookup",
        )
        rows = payload.get("repositories")
        if not isinstance(rows, list):
            raise ReconcilerError("Devin installation repository lookup did not return a repository array")
        for row in rows:
            if isinstance(row, dict):
                repository_ids.add(_require_integer(row.get("id"), "Devin installation repository lookup"))
        if len(rows) < 100:
            break
        page += 1
    return repository_ids


def _installations_by_owner(installations: list[Installation]) -> dict[str, Installation]:
    by_owner: dict[str, Installation] = {}
    for installation in installations:
        key = installation.account_login.lower()
        if key in by_owner:
            raise ReconcilerError(f"multiple visible Devin installations target {installation.account_login!r}")
        by_owner[key] = installation
    return by_owner


def reconcile(client: GhClient, *, source_repository: str, apply: bool) -> list[Finding]:
    """Classify access readiness and optionally grant Devin App repository access.

    An access grant is an external provider-configuration write, but not a
    repository-content write. It is deliberately limited to the documented
    GitHub App endpoint and never changes a default branch, workflow, issue,
    pull request, secret, or provider setting.
    """
    _validate_repository(source_repository)
    repositories = list_accessible_repositories(client)
    try:
        installations = _installations_by_owner(list_devin_installations(client))
    except ReconcilerError as error:
        detail = f"Devin installation discovery is unavailable: {error}"
        return [Finding(repo.full_name, "blocked", "none", detail) for repo in repositories]

    assigned_by_installation: dict[int, set[int]] = {}
    findings: list[Finding] = []
    for repository in repositories:
        if repository.archived:
            findings.append(Finding(repository.full_name, "excluded", "none", "Archived repository."))
            continue
        installation = installations.get(_owner(repository.full_name))
        if installation is None:
            findings.append(
                Finding(
                    repository.full_name,
                    "not_configured",
                    "none",
                    "No visible Devin GitHub App installation targets this repository owner.",
                )
            )
            continue
        if installation.repository_selection == "all":
            findings.append(
                Finding(
                    repository.full_name,
                    "current",
                    "none",
                    "Devin GitHub App access covers all repositories for this owner; provider-managed indexing is eligible.",
                    installation.installation_id,
                )
            )
            continue

        try:
            assigned = assigned_by_installation.get(installation.installation_id)
            if assigned is None:
                assigned = list_installation_repository_ids(client, installation.installation_id)
                assigned_by_installation[installation.installation_id] = assigned
        except ReconcilerError as error:
            findings.append(
                Finding(
                    repository.full_name,
                    "blocked",
                    "none",
                    f"Could not inspect selected Devin App repository access: {error}",
                    installation.installation_id,
                )
            )
            continue
        if repository.repository_id in assigned:
            findings.append(
                Finding(
                    repository.full_name,
                    "current",
                    "none",
                    "Repository already has selected Devin GitHub App access; provider-managed indexing is eligible.",
                    installation.installation_id,
                )
            )
            continue

        finding = Finding(
            repository.full_name,
            "missing",
            "report",
            "Repository is not assigned to the selected Devin GitHub App installation.",
            installation.installation_id,
        )
        if apply:
            try:
                client.request(
                    "PUT",
                    f"user/installations/{installation.installation_id}/repositories/{repository.repository_id}",
                )
                assigned.add(repository.repository_id)
                finding.operation = "app_access_granted"
                finding.detail = "Granted selected Devin GitHub App access through the documented GitHub endpoint."
            except ReconcilerError as error:
                finding.state = "blocked"
                finding.operation = "none"
                finding.detail = f"Could not grant selected Devin GitHub App access: {error}"
        findings.append(finding)
    return findings


def _report(findings: list[Finding], *, source_repository: str, apply: bool) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.state] = counts.get(finding.state, 0) + 1
    return {
        "schema_version": 1,
        "source_repository": source_repository,
        "credential_lane": "operator-token",
        "provider": "Devin GitHub App",
        "provider_app_slug": DEVIN_APP_SLUG,
        "public_deepwiki": "provider-managed; no documented indexing-write endpoint is invoked",
        "mode": "apply" if apply else "dry_run",
        "counts": counts,
        "findings": [asdict(finding) for finding in findings],
    }


def _summary_report(report: dict[str, Any]) -> dict[str, Any]:
    """Return an artifact-safe projection with no repository IDs or diagnostics."""
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
        "provider": report.get("provider"),
        "provider_app_slug": report.get("provider_app_slug"),
        "public_deepwiki": report.get("public_deepwiki"),
        "mode": report.get("mode"),
        "counts": report.get("counts", {}),
        "operations": operations,
        "repository_count": len(findings) if isinstance(findings, list) else 0,
        "redaction": "Repository names, IDs, installation IDs, and diagnostic details are intentionally omitted.",
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", required=True, help="Control-plane repository, OWNER/REPO.")
    parser.add_argument("--report", required=True, help="Path for the detailed local JSON reconciliation report.")
    parser.add_argument("--summary-report", help="Optional artifact-safe aggregate report without repository identifiers.")
    parser.add_argument("--apply", action="store_true", help="Grant supported Devin App repository access; never modify repository content.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or [])
    if not os.environ.get("GH_TOKEN"):
        raise ReconcilerError("GH_TOKEN is required; supply the workflow's existing operator-token precedence")
    findings = reconcile(GhClient(), source_repository=args.source_repo, apply=bool(args.apply))
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
        raise SystemExit(main(__import__("sys").argv[1:]))
    except ReconcilerError as error:
        print(f"reconciliation error: {error}", file=__import__("sys").stderr)
        raise SystemExit(2)
