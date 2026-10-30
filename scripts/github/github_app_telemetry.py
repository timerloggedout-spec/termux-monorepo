#!/usr/bin/env python3
"""Validate the GitHub App registry and emit safe, evidence-labelled telemetry.

This script distinguishes checked-in declarations from live observations. It
never reads secret stores, prints tokens, or treats a manifest as proof that a
permission or installation is active.

Optional manual probe: a caller may supply an ephemeral installation token via
GITHUB_APP_INSTALLATION_TOKEN. It is used only in Authorization headers and
never serialized. Scheduled CI intentionally does not provide a token while
SEC-01/02 secret provisioning remains unverified. The probe reads /rate_limit
and /installation/repositories.
"""
import argparse
import datetime
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "ops/github-apps/registry.json"
API = "https://api.github.com"


def request_json(token, path):
    req = urllib.request.Request(
        API + path,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.status, json.load(response), response.headers
    except urllib.error.HTTPError as exc:
        return exc.code, {}, exc.headers
    except (OSError, TimeoutError):
        return 0, {}, {}


def _load_manifest(app):
    path = app.get("manifest_path")
    if not path:
        return None
    manifest_path = ROOT / path
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if "default_permissions" not in manifest or "default_events" not in manifest:
        raise ValueError(
            f"{app.get('slug')}: manifest must declare default_permissions and default_events"
        )
    permissions = manifest["default_permissions"]
    events = manifest["default_events"]
    if not isinstance(permissions, dict) or not isinstance(events, list):
        raise ValueError(f"{app.get('slug')}: invalid manifest permission/event shape")
    if any(value not in ("read", "write", "admin", "none")
           for value in permissions.values()):
        raise ValueError(f"{app.get('slug')}: invalid manifest permission value")
    return manifest, permissions, events


def _installation_repositories(token):
    """Fetch every installation repository page; never return partial scope as observed."""
    path = "/installation/repositories?per_page=100"
    repositories = []
    while path:
        status, payload, headers = request_json(token, path)
        if status != 200 or not isinstance(payload.get("repositories"), list):
            return status, None
        repositories.extend(
            repo["full_name"] for repo in payload["repositories"]
            if isinstance(repo, dict) and isinstance(repo.get("full_name"), str)
        )
        link_header = headers.get("Link", "") if headers else ""
        next_path = None
        for part in link_header.split(","):
            if 'rel="next"' in part:
                url = part[part.find("<") + 1:part.find(">")]
                if url.startswith(API):
                    next_path = url[len(API):]
                else:
                    next_path = url
                break
        path = next_path
    return 200, sorted(set(repositories))


def build_telemetry(registry, token=None, probe_app_slug=None):
    if registry.get("schema_version") != 1:
        raise ValueError("unsupported registry schema_version")
    apps = registry.get("apps")
    if not isinstance(apps, list):
        raise ValueError("registry apps must be a list")

    seen = set()
    rows = []
    for app in apps:
        slug = app.get("slug")
        if not isinstance(slug, str) or not slug or slug in seen:
            raise ValueError("each app must have a unique non-empty slug")
        seen.add(slug)
        loaded = _load_manifest(app)
        if loaded is None:
            raise ValueError(f"{slug}: manifest_path is required for registered apps")
        manifest, declared, events = loaded
        rows.append({
            "slug": slug,
            "display_name": app.get("display_name"),
            "app_id": app.get("app_id"),
            "role": app.get("role"),
            "status": app.get("status", "unknown"),
            "purpose": app.get("purpose"),
            "declared_permissions": dict(sorted(declared.items())),
            "declared_events": sorted(events),
            "expected_installations": app.get("expected_installations", []),
            "evidence": {
                "registry": "checked_in_declaration",
                "manifest": "checked_in_declaration",
                "live_installation": "not_observed",
                "live_permissions": "not_observed",
                "repository_scope": "not_observed",
                "rate_limit": "not_observed",
            },
        })

    if token and not probe_app_slug:
        raise ValueError("probe_app_slug is required when a live installation token is supplied")
    if probe_app_slug and not token:
        raise ValueError("a live installation token is required when probe_app_slug is supplied")
    if token:
        # A token is evidence for exactly one named app row. The caller must
        # supply an ephemeral installation token and its registry slug together.
        target = next((row for row in rows if row["slug"] == probe_app_slug), None)
        if target is None:
            raise ValueError(f"probe_app_slug is not registered: {probe_app_slug}")
        status, limits, _ = request_json(token, "/rate_limit")
        target["evidence"]["rate_limit"] = (
            "observed" if status == 200 and isinstance(limits.get("resources"), dict)
            else f"probe_failed_http_{status}" if status else "probe_failed_network"
        )
        if status == 200:
            core = (limits.get("resources") or {}).get("core") or {}
            target["rate_limit"] = {
                key: core.get(key) for key in ("limit", "remaining", "reset")
            }
        scope_status, repos = _installation_repositories(token)
        if scope_status == 200 and repos is not None:
            target["evidence"]["repository_scope"] = "observed"
            target["observed_repository_scope"] = repos
        else:
            target["evidence"]["repository_scope"] = (
                f"probe_failed_http_{scope_status}" if scope_status else "probe_failed_network"
            )

    planned_roles = registry.get("planned_roles", [])
    if not isinstance(planned_roles, list):
        raise ValueError("registry planned_roles must be a list")
    return {
        "schema_version": 1,
        "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "registry_id": registry.get("registry_id"),
        "source_class": "checked_in_declaration_plus_optional_manual_live_probe",
        "planned_roles": planned_roles,
        "credential_policy": "no credentials or secret values are emitted",
        "apps": rows,
    }


G4_CONCLUSIONS = {
    "success", "failure", "cancelled", "timed_out", "action_required",
    "neutral", "skipped", "stale", "startup_failure",
}


def validate_g4_receipt(receipt):
    """Validate a sanitized G4 runtime receipt; never creates or fabricates evidence."""
    required = {
        "schema_version", "receipt_type", "app_slug", "mint_outcome",
        "rate_limit_before", "rate_limit_after", "api_calls_by_status",
        "repositories_inspected", "workflow", "duration_seconds",
        "conclusion", "observed_at",
    }
    if not isinstance(receipt, dict) or set(receipt) != required:
        raise ValueError("G4 receipt must contain exactly the required fields")
    if receipt["schema_version"] != 1 or receipt["receipt_type"] != "github_app_g4_runtime_receipt":
        raise ValueError("unsupported G4 receipt schema or type")
    if not isinstance(receipt["app_slug"], str) or not receipt["app_slug"].strip():
        raise ValueError("G4 receipt app_slug must be a non-empty string")
    if receipt["mint_outcome"] not in ("success", "failure"):
        raise ValueError("G4 receipt mint_outcome must be success or failure")

    for key in ("rate_limit_before", "rate_limit_after"):
        reading = receipt[key]
        if not isinstance(reading, dict) or set(reading) != {"limit", "remaining", "reset"}:
            raise ValueError(f"G4 receipt {key} must contain limit, remaining, and reset")
        if any(type(reading[field]) is not int or reading[field] < 0
               for field in ("limit", "remaining", "reset")):
            raise ValueError(f"G4 receipt {key} values must be non-negative integers")
        if reading["remaining"] > reading["limit"]:
            raise ValueError(f"G4 receipt {key} remaining exceeds limit")

    calls = receipt["api_calls_by_status"]
    if not isinstance(calls, dict):
        raise ValueError("G4 receipt api_calls_by_status must be an object")
    for status, count in calls.items():
        if (not isinstance(status, str) or len(status) != 3 or
                not status.isdigit() or status[0] not in "12345" or
                type(count) is not int or count < 0):
            raise ValueError("G4 receipt API status counts must use HTTP status keys and non-negative integers")

    if type(receipt["repositories_inspected"]) is not int or receipt["repositories_inspected"] < 0:
        raise ValueError("G4 receipt repositories_inspected must be a non-negative integer")
    workflow = receipt["workflow"]
    if not isinstance(workflow, dict) or set(workflow) != {"run_id", "attempt", "head_sha"}:
        raise ValueError("G4 receipt workflow must contain run_id, attempt, and head_sha")
    if any(type(workflow[field]) is not int or workflow[field] <= 0
           for field in ("run_id", "attempt")):
        raise ValueError("G4 receipt run_id and attempt must be positive integers")
    sha = workflow["head_sha"]
    if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("G4 receipt head_sha must be a lowercase 40-character commit SHA")
    duration = receipt["duration_seconds"]
    if type(duration) not in (int, float) or duration < 0:
        raise ValueError("G4 receipt duration_seconds must be non-negative")
    if receipt["conclusion"] not in G4_CONCLUSIONS:
        raise ValueError("G4 receipt conclusion is not a recognized workflow conclusion")
    observed_at = receipt["observed_at"]
    if not isinstance(observed_at, str):
        raise ValueError("G4 receipt observed_at must be an ISO-8601 timestamp")
    try:
        parsed = datetime.datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("G4 receipt observed_at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError("G4 receipt observed_at must include a timezone")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--output", help="write JSON to this path; default stdout")
    parser.add_argument(
        "--probe-app", help="registry slug for the single app matched to the ephemeral probe token"
    )
    args = parser.parse_args(argv)
    try:
        registry = json.loads(pathlib.Path(args.registry).read_text(encoding="utf-8"))
        result = build_telemetry(
            registry, os.environ.get("GITHUB_APP_INSTALLATION_TOKEN"), args.probe_app
        )
        encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            pathlib.Path(args.output).write_text(encoded, encoding="utf-8")
        else:
            print(encoded, end="")
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"telemetry error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
