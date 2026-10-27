#!/usr/bin/env python3
"""Index this repository's branches in the Devin organization's Wiki/Ask Devin.

Companion to ``reconcile_devin_wiki_access.py`` (GitHub App access). This
controller invokes Devin's documented v3 indexing endpoint:

    PUT https://api.devin.ai/v3/organizations/{org_id}/repositories/{repository_path}/indexing
    body: {"branch_names": [...]}  (idempotent; omitted = default branch only)

The response carries ``indexing_status.latest_indexes`` with the latest index
job (status, commit, job_id) per branch; those values are recorded in the
detail report so a run proves what Devin accepted, per branch.

Credential contract (names only; values never enter the repository, the
reports, or the logs):

  DEVIN_INDEXING_API_KEY  Actions secret. A Devin service-user or personal
                          token with the org-level ``IndexOrgRepositories``
                          permission, or the narrower combination of org
                          ``Read`` plus ``repo.use_read`` and ``repo.index``
                          grants on the repository. This is a Devin API
                          token, NOT a GitHub PAT; no GitHub credential is
                          created or used for the Devin call.
  DEVIN_ORG_ID            Actions variable. The ``org-...`` identifier copied
                          from Devin Settings -> General or Settings ->
                          Devin API (one-click copy). The org slug/name is
                          not accepted by the API as this value.
  DEVIN_WIKI_EFFORT       Actions variable recording the org's DeepWiki
                          effort level as seen on the wiki page:
                          ``low`` | ``medium`` | ``high``. Per Devin's docs,
                          wiki generation is free at low, ~5-10 ACUs per wiki
                          at medium, and ~20-40 ACUs per wiki at high.
                          Indexing refuses to run until this is recorded, and
                          the bulk ``all`` scope additionally requires low
                          effort or an explicit per-run approval.
  GH_TOKEN                The workflow's existing operator-token precedence,
                          used only to list this repository's branches and
                          open pull requests through the GitHub API.

Refresh model: Devin's docs do not state that indexed branch contents are
refreshed automatically on later pushes, and the indexing response pins each
job to a commit. Freshness is therefore maintained by re-invoking this
idempotent endpoint: the workflow's daily run re-indexes the active set
(default branch + open PR head branches), a branch-created job indexes each
new branch once, and a manual dispatch can run the full additive backfill.
Indexing is additive only; this controller never removes a branch index.

Account scope (--all-repos): the target set is the access reconciler's
credential-scoped inventory — every repository the operator token can reach
(owner, organization-member, collaborator), archived repositories skipped.
The owner's policy is full use of Devin's free offerings: at the low effort
level wiki generation is free, so account-wide runs proceed at low with no
approval; at medium/high the counted cost gate refuses account-wide runs
without the per-run approval, exactly as for a single-repo bulk backfill.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

from reconcile_devin_wiki_access import list_accessible_repositories
from reconcile_repository_surface import GhClient, LIVE_READ_ATTEMPTS, ReconcilerError, SAFE_REPOSITORY

DEVIN_API_BASE = "https://api.devin.ai/v3"
CHUNK_SIZE = 50
EFFORT_ACU_PER_WIKI: dict[str, tuple[int, int]] = {
    "low": (0, 0),
    "medium": (5, 10),
    "high": (20, 40),
}
SAFE_BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
ORG_ID_PATTERN = re.compile(r"^org-[A-Za-z0-9][A-Za-z0-9_-]*$")


class IndexingError(RuntimeError):
    """A Devin API call failed in a way the run must surface (exit 2)."""


class GateRefusal(RuntimeError):
    """A provisioning or cost gate refused the run before any Devin call."""

    def __init__(self, state: str, detail: str) -> None:
        super().__init__(detail)
        self.state = state
        self.detail = detail


@dataclass
class BranchIndex:
    branch: str
    status: str
    commit: str | None = None
    job_id: str | None = None


class GitHubBranches(Protocol):
    def request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """Call a GitHub REST endpoint and return parsed JSON."""


class DevinClient:
    """Minimal Devin v3 client. The token is held in memory only."""

    def __init__(self, token: str, *, base: str = DEVIN_API_BASE, timeout: int = 60) -> None:
        if not token:
            raise IndexingError("DEVIN_INDEXING_API_KEY is empty")
        self._token = token
        self._base = base.rstrip("/")
        self._timeout = timeout

    def index_repository(self, org_id: str, repository: str, branch_names: list[str]) -> dict[str, Any]:
        """PUT the indexing endpoint; retry once with a %2F-encoded path on 404.

        The documented path parameter spans ``owner/repo``; if a deployment
        routes it as a single segment instead, the encoded form is the same
        resource. Only a 404 triggers the second form.
        """
        body = json.dumps({"branch_names": branch_names}).encode()
        variants = [
            f"/organizations/{org_id}/repositories/{repository}/indexing",
            "/organizations/{}/repositories/{}/indexing".format(
                org_id, urllib.parse.quote(repository, safe="")
            ),
        ]
        last_error: IndexingError | None = None
        for variant in variants:
            try:
                return self._put(variant, body)
            except IndexingError as error:
                last_error = error
                if "http 404" not in str(error):
                    raise
        assert last_error is not None
        raise last_error

    def _put(self, path: str, body: bytes) -> dict[str, Any]:
        request = urllib.request.Request(
            self._base + path,
            data=body,
            method="PUT",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors="replace")[:300]
            raise IndexingError(f"Devin indexing request failed: http {error.code}: {detail}") from error
        except urllib.error.URLError as error:
            raise IndexingError(f"Devin indexing request failed: {error.reason}") from error
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError as error:
            raise IndexingError("Devin indexing response was not JSON") from error
        if not isinstance(payload, dict):
            raise IndexingError("Devin indexing response was not an object")
        return payload


def projected_acu_range(effort: str, branch_count: int) -> tuple[int, int]:
    low, high = EFFORT_ACU_PER_WIKI[effort]
    return (low * branch_count, high * branch_count)


def check_gates(
    *,
    api_key: str | None,
    org_id: str | None,
    effort: str | None,
    scope: str,
    approve_nonlow_effort: bool,
    branch_count: int,
    account_wide: bool = False,
) -> str:
    """Validate provisioning + cost gates. Returns the normalized effort."""
    missing = [
        name
        for name, value in (
            ("DEVIN_INDEXING_API_KEY", api_key),
            ("DEVIN_ORG_ID", org_id),
        )
        if not value
    ]
    if missing:
        raise GateRefusal(
            "not_provisioned",
            "Missing provisioning (names only): " + ", ".join(missing) + ". "
            "Create the Devin service-user token with IndexOrgRepositories and store it as the "
            "Actions secret DEVIN_INDEXING_API_KEY; copy the org-... ID from Devin Settings -> "
            "General or Settings -> Devin API into the Actions variable DEVIN_ORG_ID.",
        )
    assert org_id is not None
    if not ORG_ID_PATTERN.fullmatch(org_id):
        raise GateRefusal(
            "invalid_org_id",
            "DEVIN_ORG_ID does not look like an org-... identifier. Copy the Organization ID "
            "from Devin Settings -> General or Settings -> Devin API; the org slug/name is not "
            "the API identifier.",
        )
    if effort is None or effort.lower() not in EFFORT_ACU_PER_WIKI:
        raise GateRefusal(
            "effort_unrecorded",
            "DEVIN_WIKI_EFFORT is not recorded as low|medium|high. Read the effort level on "
            "the org's DeepWiki page (configurable per org, overridable per repo) and set the "
            "Actions variable DEVIN_WIKI_EFFORT to the value seen before any indexing run.",
        )
    normalized = effort.lower()
    bulk = scope == "all" or account_wide
    if bulk and normalized != "low" and not approve_nonlow_effort:
        low_acu, high_acu = projected_acu_range(normalized, branch_count)
        raise GateRefusal(
            "cost_gate",
            f"Bulk backfill of {branch_count} branches at {normalized} effort projects "
            f"~{low_acu}-{high_acu} ACUs. Refused without a per-run approval "
            "(workflow input approve_nonlow_effort) or the org effort set to low.",
        )
    return normalized


def _paginated(client: GitHubBranches, endpoint: str) -> list[Any]:
    rows: list[Any] = []
    page = 1
    while True:
        separator = "&" if "?" in endpoint else "?"
        payload = client.request(
            "GET", f"{endpoint}{separator}per_page=100&page={page}", attempts=LIVE_READ_ATTEMPTS
        )
        if not isinstance(payload, list):
            raise IndexingError(f"GitHub list for {endpoint} did not return an array")
        rows.extend(payload)
        if len(payload) < 100:
            return rows
        page += 1


def list_all_branches(client: GitHubBranches, repository: str) -> list[str]:
    rows = _paginated(client, f"repos/{repository}/branches")
    names: list[str] = []
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("name"), str):
            names.append(row["name"])
    return names


def default_branch(client: GitHubBranches, repository: str) -> str:
    payload = client.request("GET", f"repos/{repository}", attempts=LIVE_READ_ATTEMPTS)
    if not isinstance(payload, dict) or not isinstance(payload.get("default_branch"), str):
        raise IndexingError("repository lookup did not return a default branch")
    return str(payload["default_branch"])


def open_pr_head_branches(client: GitHubBranches, repository: str) -> list[str]:
    rows = _paginated(client, f"repos/{repository}/pulls?state=open")
    heads: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        head = row.get("head")
        if not isinstance(head, dict) or not isinstance(head.get("ref"), str):
            continue
        head_repo = head.get("repo")
        if not isinstance(head_repo, dict) or head_repo.get("full_name") != repository:
            continue  # fork heads are not branches of this repository
        heads.append(str(head["ref"]))
    return heads


def _is_safe_branch(name: str) -> bool:
    return bool(SAFE_BRANCH.fullmatch(name)) and ".." not in name and not name.endswith("/")


def select_branches(
    client: GitHubBranches,
    repository: str,
    *,
    scope: str,
    explicit: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Return (selected, skipped_unsafe_or_missing) for the requested scope."""
    existing = list_all_branches(client, repository)
    existing_set = set(existing)
    skipped: list[str] = []

    def accept(candidates: list[str]) -> list[str]:
        selected: list[str] = []
        for name in candidates:
            if not _is_safe_branch(name) or name not in existing_set:
                if name not in skipped:
                    skipped.append(name)
                continue
            if name not in selected:
                selected.append(name)
        return selected

    if scope == "all":
        return accept(existing), skipped
    if scope == "single":
        if not explicit:
            raise IndexingError("scope 'single' requires at least one --branch")
        return accept(list(explicit)), skipped
    if scope == "first-pass":
        candidates = [default_branch(client, repository), *open_pr_head_branches(client, repository)]
        return accept(candidates), skipped
    raise IndexingError(f"unknown scope: {scope}")


def parse_branch_statuses(response: dict[str, Any], requested: list[str]) -> list[BranchIndex]:
    statuses: dict[str, BranchIndex] = {}
    indexing_status = response.get("indexing_status")
    latest = indexing_status.get("latest_indexes") if isinstance(indexing_status, dict) else None
    if isinstance(latest, list):
        for entry in latest:
            if not isinstance(entry, dict) or not isinstance(entry.get("branch_name"), str):
                continue
            statuses[str(entry["branch_name"])] = BranchIndex(
                branch=str(entry["branch_name"]),
                status=str(entry.get("status", "unknown")),
                commit=entry.get("commit") if isinstance(entry.get("commit"), str) else None,
                job_id=entry.get("job_id") if isinstance(entry.get("job_id"), str) else None,
            )
    return [statuses.get(name, BranchIndex(branch=name, status="not_reported")) for name in requested]


def index_branches(
    devin: DevinClient,
    *,
    org_id: str,
    repository: str,
    branches: list[str],
) -> list[BranchIndex]:
    results: list[BranchIndex] = []
    for start in range(0, len(branches), CHUNK_SIZE):
        chunk = branches[start : start + CHUNK_SIZE]
        response = devin.index_repository(org_id, repository, chunk)
        results.extend(parse_branch_statuses(response, chunk))
    return results


def index_account(
    devin: DevinClient | None,
    github: GitHubBranches,
    *,
    org_id: str,
    scope: str,
    effort: str | None,
    pre_index_hook: Any = None,
) -> dict[str, Any]:
    """Index every accessible repository's selected branches, account-wide.

    The inventory is the access reconciler's credential-scoped list (owner,
    organization-member, and collaborator repositories). Archived repositories
    are skipped. Selection happens for every repository before any Devin call
    so the report — and the caller's counted cost gate — sees true totals.
    A failure in one repository is recorded and never stops the others.
    """
    if scope == "single":
        raise IndexingError("scope 'single' names branches of one repository; it is not supported account-wide")
    inventory = list_accessible_repositories(github)  # type: ignore[arg-type]
    selections: list[tuple[str, list[str], list[str]]] = []
    selection_errors: list[dict[str, Any]] = []
    for record in inventory:
        if record.archived:
            continue
        try:
            selected, skipped = select_branches(github, record.full_name, scope=scope)
        except (IndexingError, ReconcilerError) as error:
            selection_errors.append({"repository": record.full_name, "error": str(error)})
            continue
        selections.append((record.full_name, selected, skipped))
    total_branches = sum(len(selected) for _, selected, _ in selections)
    if pre_index_hook is not None:
        pre_index_hook(total_branches)

    repositories: list[dict[str, Any]] = []
    status_counts: dict[str, int] = {}
    failed = 0
    for full_name, selected, skipped in selections:
        entry: dict[str, Any] = {
            "repository": full_name,
            "branch_count": len(selected),
            "skipped_branches": skipped,
            "status_counts": {},
            "branches": [],
            "error": None,
        }
        if devin is not None and selected:
            try:
                results = index_branches(devin, org_id=org_id, repository=full_name, branches=selected)
                entry["branches"] = [asdict(result) for result in results]
                for result in results:
                    entry["status_counts"][result.status] = entry["status_counts"].get(result.status, 0) + 1
                    status_counts[result.status] = status_counts.get(result.status, 0) + 1
            except IndexingError as error:
                entry["error"] = str(error)
                failed += 1
        repositories.append(entry)
    for error_entry in selection_errors:
        repositories.append(
            {
                "repository": error_entry["repository"],
                "branch_count": 0,
                "skipped_branches": [],
                "status_counts": {},
                "branches": [],
                "error": error_entry["error"],
            }
        )
        failed += 1
    acu = projected_acu_range(effort, total_branches) if effort in EFFORT_ACU_PER_WIKI else None
    return {
        "schema_version": 1,
        "provider": "Devin Wiki indexing (v3 API)",
        "account_wide": True,
        "scope": scope,
        "mode": "apply" if devin is not None else "dry_run",
        "state": "partial" if failed else "indexed",
        "effort": effort,
        "projected_acu_range": list(acu) if acu else None,
        "repository_count": len(repositories),
        "failed_repository_count": failed,
        "branch_count": total_branches,
        "status_counts": status_counts,
        "repositories": repositories,
        "additive_only": True,
    }


def _account_summary_report(report: dict[str, Any]) -> dict[str, Any]:
    """Artifact-safe account projection: counts only, no repository names.

    The account inventory can include private repositories, so — as with the
    access reconciler's summary — names, commits, and job IDs stay out.
    """
    return {
        "schema_version": report.get("schema_version"),
        "provider": report.get("provider"),
        "account_wide": True,
        "scope": report.get("scope"),
        "mode": report.get("mode"),
        "state": report.get("state"),
        "effort": report.get("effort"),
        "projected_acu_range": report.get("projected_acu_range"),
        "repository_count": report.get("repository_count"),
        "failed_repository_count": report.get("failed_repository_count"),
        "branch_count": report.get("branch_count"),
        "status_counts": report.get("status_counts", {}),
        "additive_only": True,
        "redaction": "Repository names, Devin org ID, API token, per-branch commits and job IDs are intentionally omitted.",
    }


def _report(
    *,
    repository: str,
    scope: str,
    effort: str | None,
    mode: str,
    selected: list[str],
    skipped: list[str],
    results: list[BranchIndex],
    state: str = "indexed",
    detail: str = "",
) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
    acu = projected_acu_range(effort, len(selected)) if effort in EFFORT_ACU_PER_WIKI else None
    return {
        "schema_version": 1,
        "provider": "Devin Wiki indexing (v3 API)",
        "repository": repository,
        "scope": scope,
        "mode": mode,
        "state": state,
        "detail": detail,
        "effort": effort,
        "projected_acu_range": list(acu) if acu else None,
        "branch_count": len(selected),
        "skipped_branches": skipped,
        "status_counts": counts,
        "branches": [asdict(result) for result in results],
        "additive_only": True,
    }


def _summary_report(report: dict[str, Any]) -> dict[str, Any]:
    """Artifact-safe projection: no org ID, no token, no job IDs or commits."""
    return {
        "schema_version": report.get("schema_version"),
        "provider": report.get("provider"),
        "scope": report.get("scope"),
        "mode": report.get("mode"),
        "state": report.get("state"),
        "detail": report.get("detail"),
        "effort": report.get("effort"),
        "projected_acu_range": report.get("projected_acu_range"),
        "branch_count": report.get("branch_count"),
        "skipped_branch_count": len(report.get("skipped_branches", [])),
        "status_counts": report.get("status_counts", {}),
        "additive_only": True,
        "redaction": "Devin org ID, API token, per-branch commits and job IDs are intentionally omitted.",
    }


def _write_reports(
    report: dict[str, Any],
    report_path: str,
    summary_path: str | None,
    summary_builder: Any = _summary_report,
) -> None:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if summary_path:
        summary = Path(summary_path)
        summary.parent.mkdir(parents=True, exist_ok=True)
        summary.write_text(json.dumps(summary_builder(report), indent=2) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Repository, OWNER/REPO. Mutually exclusive with --all-repos.")
    parser.add_argument(
        "--all-repos",
        action="store_true",
        help="Index every repository in the access reconciler's credential-scoped inventory.",
    )
    parser.add_argument(
        "--scope",
        choices=["first-pass", "all", "single"],
        default="first-pass",
        help="first-pass = default branch + open PR heads; all = every branch; single = --branch list.",
    )
    parser.add_argument("--branch", action="append", default=[], help="Branch for scope 'single' (repeatable).")
    parser.add_argument(
        "--approve-nonlow-effort",
        action="store_true",
        help="Approve a bulk 'all' run at medium/high DeepWiki effort (projected ACUs are reported).",
    )
    parser.add_argument("--report", required=True, help="Path for the detailed local JSON report.")
    parser.add_argument("--summary-report", help="Optional artifact-safe aggregate report.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Select branches and report the plan only; no Devin call, no provisioning gates.",
    )
    return parser.parse_args(argv)


def _account_gate_report(args: argparse.Namespace, effort_raw: str | None, refusal: GateRefusal, branch_count: int) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "provider": "Devin Wiki indexing (v3 API)",
        "account_wide": True,
        "scope": str(args.scope),
        "mode": "apply",
        "state": refusal.state,
        "detail": refusal.detail,
        "effort": effort_raw.lower() if effort_raw else None,
        "projected_acu_range": None,
        "repository_count": 0,
        "failed_repository_count": 0,
        "branch_count": branch_count,
        "status_counts": {},
        "repositories": [],
        "additive_only": True,
    }


def _main_account(args: argparse.Namespace) -> int:
    api_key = os.environ.get("DEVIN_INDEXING_API_KEY")
    org_id = os.environ.get("DEVIN_ORG_ID")
    effort_raw = os.environ.get("DEVIN_WIKI_EFFORT")
    github = GhClient()
    effort_hint = (effort_raw or "").lower()
    if args.dry_run:
        report = index_account(
            None,
            github,
            org_id="",
            scope=str(args.scope),
            effort=effort_hint if effort_hint in EFFORT_ACU_PER_WIKI else None,
        )
        report["state"] = "planned"
        report["detail"] = "Dry run: account-wide branch selection only; no Devin API call was made."
        _write_reports(report, args.report, args.summary_report, _account_summary_report)
        print(
            json.dumps(
                {
                    "mode": "dry_run",
                    "scope": args.scope,
                    "account_wide": True,
                    "repository_count": report["repository_count"],
                    "branch_count": report["branch_count"],
                }
            )
        )
        return 0

    try:
        effort = check_gates(
            api_key=api_key,
            org_id=org_id,
            effort=effort_raw,
            scope=str(args.scope),
            approve_nonlow_effort=True,  # cost gate deferred to the counted check in the hook
            branch_count=0,
            account_wide=True,
        )
    except GateRefusal as refusal:
        report = _account_gate_report(args, effort_raw, refusal, 0)
        _write_reports(report, args.report, args.summary_report, _account_summary_report)
        print(f"::error title=Devin Wiki indexing gated::{refusal.detail}")
        print(json.dumps({"mode": "apply", "state": refusal.state, "account_wide": True}))
        return 0

    assert api_key is not None and org_id is not None
    if not api_key.startswith("cog_"):
        print(
            "::warning title=Devin Wiki indexing::DEVIN_INDEXING_API_KEY does not carry the "
            "expected cog_ service-user/personal-token prefix; the API call will surface any "
            "resulting authentication failure."
        )
    counted: list[int] = []

    def counted_gate(total: int) -> None:
        counted.append(total)
        check_gates(
            api_key=api_key,
            org_id=org_id,
            effort=effort_raw,
            scope=str(args.scope),
            approve_nonlow_effort=bool(args.approve_nonlow_effort),
            branch_count=total,
            account_wide=True,
        )

    try:
        report = index_account(
            DevinClient(api_key),
            github,
            org_id=org_id,
            scope=str(args.scope),
            effort=effort,
            pre_index_hook=counted_gate,
        )
    except GateRefusal as refusal:
        report = _account_gate_report(args, effort_raw, refusal, counted[0] if counted else 0)
        _write_reports(report, args.report, args.summary_report, _account_summary_report)
        print(f"::error title=Devin Wiki indexing gated::{refusal.detail}")
        print(json.dumps({"mode": "apply", "state": refusal.state, "account_wide": True}))
        return 0
    _write_reports(report, args.report, args.summary_report, _account_summary_report)
    print(
        json.dumps(
            {
                "mode": "apply",
                "scope": args.scope,
                "account_wide": True,
                "repository_count": report["repository_count"],
                "failed_repository_count": report["failed_repository_count"],
                "branch_count": report["branch_count"],
                "status_counts": report["status_counts"],
            },
            sort_keys=True,
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or [])
    if bool(args.all_repos) == bool(args.repo):
        raise IndexingError("exactly one of --repo or --all-repos is required")
    if args.all_repos:
        return _main_account(args)
    repository = str(args.repo)
    if not SAFE_REPOSITORY.fullmatch(repository):
        raise IndexingError(f"unsafe repository name: {repository!r}")
    api_key = os.environ.get("DEVIN_INDEXING_API_KEY")
    org_id = os.environ.get("DEVIN_ORG_ID")
    effort_raw = os.environ.get("DEVIN_WIKI_EFFORT")
    if not args.dry_run:
        # Provisioning/org/effort gates first, so an unprovisioned run reports
        # its gate state even if GitHub branch listing is unavailable. The cost
        # gate is re-checked with the real branch count after selection.
        try:
            check_gates(
                api_key=api_key,
                org_id=org_id,
                effort=effort_raw,
                scope=str(args.scope),
                approve_nonlow_effort=True,  # cost gate deferred to the counted check below
                branch_count=0,
            )
        except GateRefusal as refusal:
            report = _report(
                repository=repository,
                scope=str(args.scope),
                effort=effort_raw.lower() if effort_raw else None,
                mode="apply",
                selected=[],
                skipped=[],
                results=[],
                state=refusal.state,
                detail=refusal.detail,
            )
            _write_reports(report, args.report, args.summary_report)
            print(f"::error title=Devin Wiki indexing gated::{refusal.detail}")
            print(json.dumps({"mode": "apply", "state": refusal.state, "branch_count": 0}))
            return 0
    github = GhClient()
    selected, skipped = select_branches(
        github, repository, scope=str(args.scope), explicit=list(args.branch)
    )
    if args.dry_run:
        report = _report(
            repository=repository,
            scope=str(args.scope),
            effort=(os.environ.get("DEVIN_WIKI_EFFORT") or "").lower() or None,
            mode="dry_run",
            selected=selected,
            skipped=skipped,
            results=[BranchIndex(branch=name, status="planned") for name in selected],
            state="planned",
            detail="Dry run: branch selection only; no Devin API call was made.",
        )
        _write_reports(report, args.report, args.summary_report)
        print(json.dumps({"mode": "dry_run", "scope": args.scope, "branch_count": len(selected)}))
        return 0

    try:
        effort = check_gates(
            api_key=api_key,
            org_id=org_id,
            effort=effort_raw,
            scope=str(args.scope),
            approve_nonlow_effort=bool(args.approve_nonlow_effort),
            branch_count=len(selected),
        )
    except GateRefusal as refusal:
        report = _report(
            repository=repository,
            scope=str(args.scope),
            effort=effort_raw.lower() if effort_raw else None,
            mode="apply",
            selected=selected,
            skipped=skipped,
            results=[],
            state=refusal.state,
            detail=refusal.detail,
        )
        _write_reports(report, args.report, args.summary_report)
        print(f"::error title=Devin Wiki indexing gated::{refusal.detail}")
        print(json.dumps({"mode": "apply", "state": refusal.state, "branch_count": len(selected)}))
        return 0

    assert api_key is not None and org_id is not None
    if not api_key.startswith("cog_"):
        print(
            "::warning title=Devin Wiki indexing::DEVIN_INDEXING_API_KEY does not carry the "
            "expected cog_ service-user/personal-token prefix; the API call will surface any "
            "resulting authentication failure."
        )
    devin = DevinClient(api_key)
    results = index_branches(devin, org_id=org_id, repository=repository, branches=selected)
    report = _report(
        repository=repository,
        scope=str(args.scope),
        effort=effort,
        mode="apply",
        selected=selected,
        skipped=skipped,
        results=results,
    )
    _write_reports(report, args.report, args.summary_report)
    print(
        json.dumps(
            {"mode": "apply", "scope": args.scope, "branch_count": len(selected), "status_counts": report["status_counts"]},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(__import__("sys").argv[1:]))
    except (IndexingError, ReconcilerError) as error:
        print(f"indexing error: {error}", file=__import__("sys").stderr)
        raise SystemExit(2)
