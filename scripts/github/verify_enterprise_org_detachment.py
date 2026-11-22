#!/usr/bin/env python3
"""Capture and compare organization metadata around Enterprise detachment.

The report contains identifiers and names only. Secret values, token values,
webhook URLs, and private key material stay outside the report.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"
EXPECTED_ACTOR = "timerloggedout-spec"
EXPECTED_REPOSITORIES = {
    "termux-monorepo_enterprise",
    "termux-monorepo_enterprise_too",
    "manus-public-ui-research",
}
SCHEMA = "github.enterprise-org-preservation.v1"


class ApiError(RuntimeError):
    def __init__(self, status: int, path: str):
        super().__init__(f"GitHub API returned HTTP {status} for {path}")
        self.status = status


def request(url: str, token: str):
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "termux-monorepo-enterprise-org-preservation",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            return json.loads(response.read().decode("utf-8")), response.headers
    except urllib.error.HTTPError as exc:
        raise ApiError(exc.code, urllib.parse.urlparse(url).path) from None


def get(path: str, token: str):
    return request(f"{API_ROOT}{path}", token)[0]


def pages(path: str, token: str):
    url = f"{API_ROOT}{path}"
    output = []
    while url:
        data, headers = request(url, token)
        if not isinstance(data, list):
            raise RuntimeError(f"Expected paginated array from {path}")
        output.extend(data)
        match = re.search(r'<([^>]+)>;\s*rel="next"', headers.get("Link", ""))
        url = match.group(1) if match else ""
    return output


def optional_get(path: str, token: str):
    try:
        return {"status": "observed", "data": get(path, token)}
    except ApiError as exc:
        if exc.status in (403, 404, 422):
            return {"status": "unavailable", "http_status": exc.status, "data": {}}
        raise


def optional_pages(path: str, token: str):
    try:
        return {"status": "observed", "items": pages(path, token)}
    except ApiError as exc:
        if exc.status in (403, 404, 422):
            return {"status": "unavailable", "http_status": exc.status, "items": []}
        raise


def compact_repo(repo: dict, token: str):
    owner, name = repo["owner"]["login"], repo["name"]
    root = f"/repos/{owner}/{name}"
    branches = optional_pages(f"{root}/branches?per_page=100", token)
    tags = optional_pages(f"{root}/tags?per_page=100", token)
    releases = optional_pages(f"{root}/releases?per_page=100", token)
    workflows = optional_get(f"{root}/actions/workflows?per_page=100", token)
    secrets = optional_get(f"{root}/actions/secrets?per_page=100", token)
    variables = optional_get(f"{root}/actions/variables?per_page=100", token)
    hooks = optional_pages(f"{root}/hooks?per_page=100", token)
    environments = optional_get(f"{root}/environments?per_page=100", token)
    deployments = optional_pages(f"{root}/deployments?per_page=100", token)

    workflow_data = workflows["data"] if workflows["status"] == "observed" else {}
    secret_data = secrets["data"] if secrets["status"] == "observed" else {}
    variable_data = variables["data"] if variables["status"] == "observed" else {}
    environment_data = environments["data"] if environments["status"] == "observed" else {}

    return {
        "id": str(repo.get("id", "")),
        "name": name,
        "full_name": repo.get("full_name", ""),
        "visibility": repo.get("visibility", ""),
        "default_branch": repo.get("default_branch", ""),
        "archived": bool(repo.get("archived")),
        "fork": bool(repo.get("fork")),
        "size_kb": int(repo.get("size", 0)),
        "pushed_at": repo.get("pushed_at"),
        "has_pages": bool(repo.get("has_pages")),
        "has_wiki": bool(repo.get("has_wiki")),
        "has_issues": bool(repo.get("has_issues")),
        "open_issues_count": int(repo.get("open_issues_count", 0)),
        "branches_status": branches["status"],
        "branches": sorted(
            [{"name": x.get("name", ""), "sha": (x.get("commit") or {}).get("sha", "")}
             for x in branches["items"]], key=lambda x: x["name"]),
        "tags_status": tags["status"],
        "tags": sorted(
            [{"name": x.get("name", ""), "sha": (x.get("commit") or {}).get("sha", "")}
             for x in tags["items"]], key=lambda x: x["name"]),
        "releases_status": releases["status"],
        "releases": sorted(
            [{"id": str(x.get("id", "")), "tag_name": x.get("tag_name", ""),
              "target_commitish": x.get("target_commitish", ""), "draft": bool(x.get("draft")),
              "prerelease": bool(x.get("prerelease"))} for x in releases["items"]],
            key=lambda x: x["id"]),
        "workflows_status": workflows["status"],
        "workflows": sorted(
            [{"id": str(x.get("id", "")), "name": x.get("name", ""),
              "path": x.get("path", ""), "state": x.get("state", "")}
             for x in workflow_data.get("workflows", [])], key=lambda x: x["id"]),
        "actions_secrets_status": secrets["status"],
        "actions_secret_names": sorted(x.get("name", "") for x in secret_data.get("secrets", [])),
        "actions_variables_status": variables["status"],
        "actions_variable_names": sorted(x.get("name", "") for x in variable_data.get("variables", [])),
        "hooks_status": hooks["status"],
        "hooks": sorted(
            [{"id": str(x.get("id", "")), "active": bool(x.get("active")),
              "events": sorted(x.get("events", []))} for x in hooks["items"]],
            key=lambda x: x["id"]),
        "environments_status": environments["status"],
        "environments": sorted(x.get("name", "") for x in environment_data.get("environments", [])),
        "deployments_status": deployments["status"],
        "deployments": sorted(
            [{"id": str(x.get("id", "")), "environment": x.get("environment", ""),
              "ref": x.get("ref", ""), "sha": x.get("sha", "")}
             for x in deployments["items"]], key=lambda x: x["id"]),
    }


def collect(org_slug: str, token: str):
    actor = get("/user", token)
    login = actor.get("login", "")
    if login.casefold() != EXPECTED_ACTOR.casefold():
        raise RuntimeError(f"Credential identity mismatch: expected {EXPECTED_ACTOR}, received {login or 'empty'}")

    org_path = urllib.parse.quote(org_slug, safe="")
    org = get(f"/orgs/{org_path}", token)
    repos = pages(f"/orgs/{org_path}/repos?type=all&sort=full_name&direction=asc&per_page=100", token)
    secrets = optional_get(f"/orgs/{org_path}/actions/secrets?per_page=100", token)
    variables = optional_get(f"/orgs/{org_path}/actions/variables?per_page=100", token)
    hooks = optional_pages(f"/orgs/{org_path}/hooks?per_page=100", token)
    installations = optional_get(f"/orgs/{org_path}/installations?per_page=100", token)

    secret_data = secrets["data"] if secrets["status"] == "observed" else {}
    variable_data = variables["data"] if variables["status"] == "observed" else {}
    hook_items = sorted(
        [{"id": str(x.get("id", "")), "active": bool(x.get("active")),
          "events": sorted(x.get("events", []))} for x in hooks["items"]],
        key=lambda x: x["id"])
    installation_data = installations["data"] if installations["status"] == "observed" else {}
    app_items = sorted(
        [{"id": str(x.get("id", "")), "app_id": str(x.get("app_id", "")),
          "app_slug": x.get("app_slug", ""), "repository_selection": x.get("repository_selection", "")}
         for x in installation_data.get("installations", [])],
        key=lambda x: x["id"])

    return {
        "schema": SCHEMA,
        "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "actor": login,
        "organization": {
            "id": str(org.get("id", "")),
            "login": org.get("login", ""),
            "html_url": org.get("html_url", ""),
            "plan": (org.get("plan") or {}).get("name"),
            "created_at": org.get("created_at"),
            "public_repos": int(org.get("public_repos", 0)),
            "total_private_repos": int(org.get("total_private_repos", 0)),
            "repositories": [compact_repo(x, token) for x in repos],
            "integrations": {
                "actions_secrets_status": secrets["status"],
                "actions_secret_names": sorted(x.get("name", "") for x in secret_data.get("secrets", [])),
                "actions_variables_status": variables["status"],
                "actions_variable_names": sorted(x.get("name", "") for x in variable_data.get("variables", [])),
                "webhooks_status": hooks["status"],
                "webhooks": hook_items,
                "app_installations_status": installations["status"],
                "app_installations": app_items,
            },
        },
    }


def missing_names(before, after, key):
    return sorted({str(x.get(key, "")) for x in before} - {str(x.get(key, "")) for x in after})


def compare_snapshots(before, after):
    findings = []
    old_org, new_org = before.get("organization", {}), after.get("organization", {})
    if old_org.get("id") != new_org.get("id"):
        findings.append("organization_id_changed")

    old_repos = {x.get("id"): x for x in old_org.get("repositories", [])}
    new_repos = {x.get("id"): x for x in new_org.get("repositories", [])}
    for repo_id in old_repos.keys() - new_repos.keys():
        findings.append(f"repository_missing:{old_repos[repo_id].get('name', repo_id)}")

    for repo_id in old_repos.keys() & new_repos.keys():
        old, new = old_repos[repo_id], new_repos[repo_id]
        name = old.get("name", repo_id)
        if old.get("full_name") != new.get("full_name"):
            findings.append(f"repository_identity_changed:{name}")
        for collection in ("branches", "tags", "releases", "workflows", "hooks", "deployments"):
            status_key = f"{collection}_status"
            if old.get(status_key) != "observed" or new.get(status_key) != "observed":
                findings.append(f"collection_unverified:{name}:{collection}")
                continue
            key = "id" if collection in ("releases", "workflows", "hooks", "deployments") else "name"
            missing = missing_names(old.get(collection, []), new.get(collection, []), key)
            if missing:
                findings.append(f"items_missing:{name}:{collection}:{','.join(missing)}")
        for collection, status_key in (
            ("actions_secret_names", "actions_secrets_status"),
            ("actions_variable_names", "actions_variables_status"),
            ("environments", "environments_status"),
        ):
            if old.get(status_key) != "observed" or new.get(status_key) != "observed":
                findings.append(f"collection_unverified:{name}:{collection}")
                continue
            missing = sorted(set(old.get(collection, [])) - set(new.get(collection, [])))
            if missing:
                findings.append(f"items_missing:{name}:{collection}:{','.join(missing)}")

    old_int, new_int = old_org.get("integrations", {}), new_org.get("integrations", {})
    for collection, status_key, identity_key in (
        ("actions_secret_names", "actions_secrets_status", None),
        ("actions_variable_names", "actions_variables_status", None),
        ("webhooks", "webhooks_status", "id"),
        ("app_installations", "app_installations_status", "id"),
    ):
        if old_int.get(status_key) != "observed" or new_int.get(status_key) != "observed":
            findings.append(f"integration_unverified:{collection}")
            continue
        if identity_key:
            missing = missing_names(old_int.get(collection, []), new_int.get(collection, []), identity_key)
        else:
            missing = sorted(set(old_int.get(collection, [])) - set(new_int.get(collection, [])))
        if missing:
            findings.append(f"integration_items_missing:{collection}:{','.join(missing)}")
    return sorted(findings)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--org", default=os.getenv("ORG_SLUG", "search-astute-ly"))
    parser.add_argument("--phase", choices=("baseline", "verify"), default=os.getenv("PHASE", "baseline"))
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output", type=Path, default=Path("enterprise-org-state.json"))
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9-]+", args.org):
        print("Organization slug must contain letters, numbers, and hyphens.", file=sys.stderr)
        return 2
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        print("Configure the existing operator GitHub PAT secret as GH_TOKEN.", file=sys.stderr)
        return 2

    try:
        snapshot = collect(args.org, token)
    except (ApiError, RuntimeError, ValueError) as exc:
        print(f"Collection failed: {exc}", file=sys.stderr)
        return 2

    org = snapshot["organization"]
    errors, warnings = [], []
    names = {repo.get("name") for repo in org["repositories"]}
    errors.extend(f"expected_repository_missing:{name}" for name in sorted(EXPECTED_REPOSITORIES - names))

    if args.phase == "verify":
        if not args.baseline or not args.baseline.is_file():
            print("Verification requires the baseline artifact JSON.", file=sys.stderr)
            return 2
        before = json.loads(args.baseline.read_text(encoding="utf-8"))
        errors.extend(compare_snapshots(before, snapshot))
        if (org.get("plan") or "").casefold() != "free":
            errors.append(f"plan_not_free:{org.get('plan') or 'unavailable'}")

    if any(repo.get("visibility") == "private" for repo in org["repositories"]):
        warnings.append("private_repository_feature_review_required")
    if any(repo.get("visibility") == "internal" for repo in org["repositories"]):
        warnings.append("internal_repositories_convert_to_private_on_detachment")

    snapshot["verification"] = {
        "phase": args.phase,
        "status": "FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
        "errors": sorted(errors),
        "warnings": sorted(warnings),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        lines = [
            "## Enterprise organization preservation",
            "",
            f"- Phase: {args.phase}",
            f"- Organization: {org.get('login')} ({org.get('html_url')})",
            f"- Organization ID: {org.get('id')}",
            f"- Plan: {org.get('plan') or 'UNVERIFIED'}",
            f"- Repositories: {len(org['repositories'])}",
            f"- Actions secret names: {len(org['integrations']['actions_secret_names'])} ({org['integrations']['actions_secrets_status']})",
            f"- Actions variable names: {len(org['integrations']['actions_variable_names'])} ({org['integrations']['actions_variables_status']})",
            f"- Webhooks: {len(org['integrations']['webhooks'])} ({org['integrations']['webhooks_status']})",
            f"- App installations: {len(org['integrations']['app_installations'])} ({org['integrations']['app_installations_status']})",
            f"- Result: {snapshot['verification']['status']}",
            "",
            "| Repository | Visibility | Default branch | Branches | Tags | Releases | Workflows |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
        for repo in org["repositories"]:
            lines.append(
                f"| {repo['name']} | {repo['visibility']} | {repo['default_branch']} | "
                f"{len(repo['branches'])} | {len(repo['tags'])} | {len(repo['releases'])} | {len(repo['workflows'])} |"
            )
        lines.extend(["", "### Findings"])
        lines.extend([f"- {x}" for x in errors + warnings] or ["- Inventory reconciled."])
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write("\n".join(lines) + "\n")

    print(json.dumps({
        "status": snapshot["verification"]["status"],
        "organization": org.get("login"),
        "plan": org.get("plan"),
        "repositories": len(org["repositories"]),
        "errors": errors,
        "warnings": warnings,
    }, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
