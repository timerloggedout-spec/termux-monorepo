#!/usr/bin/env python3
"""Dry-run or transfer all repositories from an expiring Enterprise org.

Repository contents move through GitHub's repository-transfer endpoint. The
receipt contains metadata only; secret values and webhook URLs stay private.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.github.verify_enterprise_org_detachment import (  # noqa: E402
    ApiError,
    collect,
    compare_snapshots,
    get,
    pages,
)

API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"
EXPECTED_ACTOR = "timerloggedout-spec"


def api_call(method: str, path: str, token: str, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API_ROOT}{path}",
        data=body,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "Content-Type": "application/json",
            "User-Agent": "termux-monorepo-enterprise-org-transfer",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raise ApiError(exc.code, urllib.parse.urlparse(req.full_url).path) from None


def org_membership_role(org: str, token: str):
    membership = get(f"/user/memberships/orgs/{urllib.parse.quote(org, safe='')}", token)
    return membership.get("role"), membership.get("state")


def build_manual_followups(baseline):
    integrations = baseline.get("organization", {}).get("integrations", {})
    items = []
    if integrations.get("actions_secret_names"):
        items.append({
            "resource": "organization_actions_secrets",
            "names": integrations["actions_secret_names"],
            "action": "Re-enter secret values in the destination organization.",
        })
    if integrations.get("actions_variable_names"):
        items.append({
            "resource": "organization_actions_variables",
            "names": integrations["actions_variable_names"],
            "action": "Recreate organization variables in the destination organization.",
        })
    if integrations.get("webhooks"):
        items.append({
            "resource": "organization_webhooks",
            "items": integrations["webhooks"],
            "action": "Recreate webhooks; re-enter each webhook secret.",
        })
    if integrations.get("app_installations"):
        items.append({
            "resource": "github_app_installations",
            "items": integrations["app_installations"],
            "action": "Install and authorize each app in the destination organization.",
        })
    items.append({
        "resource": "organization_access_and_shared_assets",
        "items": [],
        "action": "Reconcile teams, membership, project boards, discussions, and package ownership.",
    })
    return items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-org", default="search-astute-ly")
    parser.add_argument("--target-org", default="asastraneonexus")
    parser.add_argument("--mode", choices=("dry_run", "apply"), default="dry_run")
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, default=Path("enterprise-org-transfer-receipt.json"))
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9-]+", args.source_org) or not re.fullmatch(r"[A-Za-z0-9-]+", args.target_org):
        print("Organization slugs must contain letters, numbers, and hyphens.", file=sys.stderr)
        return 2
    if args.source_org.casefold() == args.target_org.casefold():
        print("The destination organization must differ from the source.", file=sys.stderr)
        return 2

    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        print("Configure the existing operator GitHub PAT secret as GH_TOKEN.", file=sys.stderr)
        return 2
    if not args.baseline.is_file():
        print("A baseline artifact JSON file is required.", file=sys.stderr)
        return 2

    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    baseline_org = baseline.get("organization", {})
    if baseline_org.get("login", "").casefold() != args.source_org.casefold():
        print("Baseline organization mismatch for the requested source.", file=sys.stderr)
        return 2

    try:
        actor = get("/user", token).get("login", "")
        if actor.casefold() != EXPECTED_ACTOR.casefold():
            raise RuntimeError(f"Credential identity mismatch: expected {EXPECTED_ACTOR}, received {actor or 'empty'}")

        source = get(f"/orgs/{urllib.parse.quote(args.source_org, safe='')}", token)
        target = get(f"/orgs/{urllib.parse.quote(args.target_org, safe='')}", token)
        if (target.get("plan") or {}).get("name", "").casefold() != "free":
            raise RuntimeError("Destination organization must report the GitHub Free plan.")

        role, state = org_membership_role(args.target_org, token)
        if role != "admin" or state != "active":
            raise RuntimeError("Authenticated operator must have active organization-owner access to the destination.")

        baseline_repos = baseline_org.get("repositories", [])
        if not baseline_repos:
            raise RuntimeError("Baseline contains zero source repositories.")
        expected_ids = {str(repo.get("id")) for repo in baseline_repos}
        expected_names = {repo.get("name") for repo in baseline_repos}

        source_repos = pages(f"/orgs/{args.source_org}/repos?type=all&per_page=100", token)
        target_repos = pages(f"/orgs/{args.target_org}/repos?type=all&per_page=100", token)
        source_by_name = {repo["name"]: repo for repo in source_repos}
        target_by_name = {repo["name"]: repo for repo in target_repos}

        source_names = set(source_by_name)
        if source_names - expected_names:
            raise RuntimeError("Source organization changed after baseline capture; capture a fresh baseline.")
        for repo in baseline_repos:
            name = repo["name"]
            source_repo = source_by_name.get(name)
            target_repo = target_by_name.get(name)
            if source_repo and str(source_repo.get("id")) != str(repo.get("id")):
                raise RuntimeError(f"Source repository identity changed: {name}")
            if target_repo and str(target_repo.get("id")) != str(repo.get("id")):
                raise RuntimeError(f"Destination name collision: {name}")
            if source_repo and not (source_repo.get("permissions") or {}).get("admin", False):
                raise RuntimeError(f"Administrator permission is required for {args.source_org}/{name}.")
            visibility = (source_repo or target_repo or {}).get("visibility", repo.get("visibility"))
            if visibility == "internal":
                raise RuntimeError(f"Internal repository requires a separate visibility migration: {name}")
            if not source_repo and not target_repo:
                raise RuntimeError(f"Repository is absent from both source and destination: {name}")

        confirmation = f"TRANSFER {len(baseline_repos)} REPOSITORIES FROM {args.source_org} TO {args.target_org}"
        plan = [{
            "repository_id": str(repo.get("id")),
            "name": repo.get("name"),
            "source": f"{args.source_org}/{repo.get('name')}",
            "destination": f"{args.target_org}/{repo.get('name')}",
            "visibility": repo.get("visibility"),
            "state": "already_transferred" if repo.get("name") in target_by_name else "ready",
        } for repo in baseline_repos]

        results = []
        if args.mode == "dry_run":
            results = [{"repository": item["name"], "status": item["state"]} for item in plan]
        else:
            if args.confirmation != confirmation:
                raise RuntimeError(f"Confirmation mismatch. Required exact value: {confirmation}")
            for item in plan:
                name = item["name"]
                if item["state"] == "already_transferred":
                    results.append({"repository": name, "status": "already_transferred"})
                    continue
                api_call(
                    "POST",
                    f"/repos/{args.source_org}/{urllib.parse.quote(name, safe='')}/transfer",
                    token,
                    {"new_owner": args.target_org},
                )
                deadline = time.time() + 600
                moved = None
                while time.time() < deadline:
                    try:
                        moved = get(f"/repos/{args.target_org}/{urllib.parse.quote(name, safe='')}", token)
                    except ApiError as exc:
                        if exc.status != 404:
                            raise
                    if moved and str(moved.get("id")) == item["repository_id"] and moved.get("owner", {}).get("login", "").casefold() == args.target_org.casefold():
                        break
                    time.sleep(5)
                else:
                    raise RuntimeError(f"Transfer accepted but destination verification timed out: {name}")
                results.append({"repository": name, "repository_id": item["repository_id"], "status": "transferred"})

            current_source = pages(f"/orgs/{args.source_org}/repos?type=all&per_page=100", token)
            if current_source:
                raise RuntimeError(f"Source organization retains {len(current_source)} repositories after transfer.")
            current = collect(args.target_org, token)
            findings = compare_snapshots(baseline, current, "transferred", args.target_org)
            if findings:
                raise RuntimeError("Post-transfer reconciliation findings: " + "; ".join(findings))
            current_target_ids = {str(repo.get("id")) for repo in current["organization"]["repositories"]}
            if not expected_ids.issubset(current_target_ids):
                raise RuntimeError("Destination repository ID set is missing baseline repository IDs.")

        receipt = {
            "schema": "github.enterprise-org-transfer.v1",
            "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "actor": actor,
            "mode": args.mode,
            "source_org": args.source_org,
            "target_org": args.target_org,
            "source_enterprise_plan": (source.get("plan") or {}).get("name"),
            "target_plan": (target.get("plan") or {}).get("name"),
            "expected_confirmation": confirmation,
            "repositories": plan,
            "results": results,
            "manual_followups": build_manual_followups(baseline),
            "status": "DRY_RUN_READY" if args.mode == "dry_run" else "TRANSFERRED_AND_RECONCILED",
        }
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(receipt, indent=2))
        return 0
    except (ApiError, RuntimeError, ValueError) as exc:
        print(f"Transfer workflow stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
