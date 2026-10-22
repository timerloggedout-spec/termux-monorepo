#!/usr/bin/env python3
"""Read-only Tribute GitLab collector and offline candidate planner."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

SCHEMA = "tribute-gitlab-plan/v2"
DEFAULT_PROJECT_ID = 85129320
DEFAULT_TIMEOUT = 20
MAX_PAGES = 5
PER_PAGE = 100
GITLAB_HOST = "gitlab.com"


def _clean_item(kind: str, obj: dict[str, Any]) -> dict[str, Any]:
    """Retain only compact, non-sensitive fields from GitLab objects."""
    result = {key: obj[key] for key in ("iid", "state", "title", "labels", "web_url") if key in obj}
    milestone = obj.get("milestone")
    if isinstance(milestone, dict):
        result["milestone"] = {key: milestone[key] for key in ("id", "title") if key in milestone}
    assignees = obj.get("assignees")
    if isinstance(assignees, list):
        result["assignees"] = [{"username": user["username"]} for user in assignees
                               if isinstance(user, dict) and isinstance(user.get("username"), str)]
    author = obj.get("author")
    if isinstance(author, dict) and isinstance(author.get("username"), str):
        result["author"] = {"username": author["username"]}
    result["kind"] = kind
    if kind == "merge_request":
        for key in ("head_pipeline", "pipeline"):
            if isinstance(obj.get(key), dict):
                result["pipeline"] = {"status": obj[key].get("status")}
                break
    return result


def collect(project_id: int = DEFAULT_PROJECT_ID, timeout: int = DEFAULT_TIMEOUT,
            max_pages: int = MAX_PAGES, runner: Callable[..., Any] = subprocess.run) -> dict[str, Any]:
    """Fetch bounded project/head/issues/MRs through glab's fixed GitLab host."""
    if isinstance(project_id, bool) or not isinstance(project_id, int) or project_id <= 0:
        raise ValueError("project_id must be a positive integer")
    if timeout <= 0 or not 1 <= max_pages <= MAX_PAGES:
        raise ValueError("timeout must be positive and max_pages between 1 and 5")

    def get(endpoint: str) -> Any:
        proc = runner(["glab", "api", "--hostname", GITLAB_HOST, endpoint],
                      check=True, capture_output=True, text=True, timeout=timeout)
        return json.loads(proc.stdout)

    project = get(f"projects/{project_id}")
    if not isinstance(project, dict) or not project.get("path_with_namespace"):
        raise ValueError("GitLab project response missing namespace path")
    base = f"projects/{project_id}"
    default_branch = project.get("default_branch")
    ref = quote(str(default_branch), safe="") if default_branch else ""
    commits = get(f"{base}/repository/commits?ref_name={ref}&per_page=1") if default_branch else []
    head_sha = commits[0].get("id") if isinstance(commits, list) and commits and isinstance(commits[0], dict) else None
    features = {
        "issues": ("issues_enabled", "issues_access_level"),
        "merge_requests": ("merge_requests_enabled", "merge_requests_access_level"),
    }
    items: list[dict[str, Any]] = []
    truncated = False
    collection_status: dict[str, str] = {}
    for endpoint, kind in (("issues", "issue"), ("merge_requests", "merge_request")):
        enabled_key, access_key = features[endpoint]
        explicitly_disabled = (project.get(enabled_key) is False or
                               project.get(access_key) == "disabled")
        if explicitly_disabled:
            collection_status[endpoint] = "disabled"
            continue
        collection_status[endpoint] = "collected"
        for page in range(1, max_pages + 1):
            records = get(f"{base}/{endpoint}?state=opened&per_page={PER_PAGE}&page={page}")
            if not isinstance(records, list):
                raise ValueError(f"unexpected GitLab {endpoint} response")
            items.extend(_clean_item(kind, row) for row in records if isinstance(row, dict))
            if len(records) < PER_PAGE:
                break
            if page == max_pages:
                truncated = True
    return {"project": {"path_with_namespace": project["path_with_namespace"], "web_url": project.get("web_url"),
                        "id": project_id, "default_branch": default_branch},
            "head_sha": head_sha, "items": items, "pagination_truncated": truncated,
            "collection_status": collection_status,
            "collector": {"host": GITLAB_HOST, "read_only": True, "max_pages_per_collection": max_pages}}


def plan(snapshot: dict[str, Any], project_mode: str, allowlisted_projects: set[str] | None = None,
         github_canonical: dict[str, Any] | None = None) -> dict[str, Any]:
    """Plan only. Native repositories require explicit path allowlisting; mirrors require SHA proof."""
    if project_mode not in {"native_gitlab", "github_mirror"}:
        raise ValueError("project_mode must be native_gitlab or github_mirror")
    project = snapshot.get("project") or {}
    project_path, project_url = project.get("path_with_namespace"), project.get("web_url")
    if not isinstance(project_path, str) or not project_path.strip():
        raise ValueError("snapshot.project.path_with_namespace is required")
    if not isinstance(project_url, str) or not project_url.startswith("https://gitlab.com/"):
        raise ValueError("snapshot.project.web_url must be an HTTPS gitlab.com URL")
    gl_sha = snapshot.get("head_sha")
    canonical = github_canonical if github_canonical is not None else snapshot.get("github_canonical") or {}
    gh_repo, gh_sha = canonical.get("repository"), canonical.get("head_sha")
    valid_sha = lambda value: isinstance(value, str) and re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", value) is not None
    # Repository identity and SHA are caller assertions, not independently fetched proof.
    # A GitLab group path need not equal its canonical GitHub owner's namespace.
    valid_repository = isinstance(gh_repo, str) and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", gh_repo) is not None
    mirror_aligned = bool(valid_repository and valid_sha(gl_sha) and valid_sha(gh_sha) and gh_sha == gl_sha)
    native_allowed = project_mode == "native_gitlab" and project_path in (allowlisted_projects or set())
    sync = "aligned" if project_mode == "github_mirror" and mirror_aligned else ("unknown" if project_mode == "github_mirror" else "native")
    candidates = []
    for item in snapshot.get("items", []):
        if not isinstance(item, dict) or item.get("kind") not in {"issue", "merge_request"}:
            continue
        iid = item.get("iid")
        if item.get("state") != "opened" or isinstance(iid, bool) or not isinstance(iid, int) or iid < 1:
            continue
        labels = sorted({str(label) for label in item.get("labels", [])})
        eligible = not item.get("assignees") and (native_allowed if project_mode == "native_gitlab" else mirror_aligned)
        candidates.append({"kind": item["kind"], "iid": iid, "title": str(item.get("title") or ""),
            "url": item.get("web_url") or f"{project_url.rstrip('/')}/-/{'issues' if item['kind']=='issue' else 'merge_requests'}/{iid}",
            "labels": labels, "milestone": item.get("milestone"), "assignee_count": len(item.get("assignees") or []),
            "author": (item.get("author") or {}).get("username"),
            "gitlab_pipeline_status": (item.get("pipeline") or {}).get("status"),
            "canonical_github": {"repository": gh_repo, "head_sha": gh_sha} if project_mode == "github_mirror" and gh_repo else None,
            "sync_state": sync, "eligible_for_review": eligible,
            "plan": "review_candidate" if eligible else "observe_only",
            "reason": "explicitly allowlisted native GitLab project" if native_allowed else
                      "canonical GitHub head matches GitLab snapshot" if project_mode == "github_mirror" and mirror_aligned else
                      "native project is not explicitly allowlisted" if project_mode == "native_gitlab" else
                      "GitHub canonical alignment is missing or unverified; observe only"})
    return {"schema": SCHEMA, "mode": "opt_in_read_only_planning", "project_mode": project_mode,
        "provider": "gitlab", "github_authority": "canonical_production" if project_mode == "github_mirror" else None,
        "snapshot_project": project_path, "head_sha": gl_sha, "pagination_truncated": bool(snapshot.get("pagination_truncated")),
        "sync_state": sync, "collection_status": snapshot.get("collection_status", {}),
        "canonical_evidence": "caller_supplied_not_independently_verified" if project_mode == "github_mirror" else None,
        "candidates": candidates, "write_plan": []}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--project-id", type=int, default=DEFAULT_PROJECT_ID)
    parser.add_argument("--project-mode", choices=("native_gitlab", "github_mirror"), required=True)
    parser.add_argument("--allowlisted-project", action="append", default=[])
    parser.add_argument("--github-repository")
    parser.add_argument("--github-sha")
    args = parser.parse_args(argv)
    if args.collect:
        snapshot = collect(args.project_id)
        canonical = {"repository": args.github_repository, "head_sha": args.github_sha}
        result = plan(snapshot, args.project_mode, set(args.allowlisted_project), canonical if args.github_repository or args.github_sha else None)
    elif args.snapshot:
        snapshot = json.loads(args.snapshot.read_text())
        canonical = {"repository": args.github_repository, "head_sha": args.github_sha}
        result = plan(snapshot, args.project_mode, set(args.allowlisted_project), canonical if args.github_repository or args.github_sha else None)
    else:
        parser.error("choose --collect or --snapshot")
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
