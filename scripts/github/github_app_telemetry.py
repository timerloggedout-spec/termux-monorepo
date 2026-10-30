#!/usr/bin/env python3
"""Validate the GitHub App registry and emit safe, evidence-labelled telemetry.

This script distinguishes checked-in declarations from live observations. It
never reads secret stores, prints tokens, or treats a manifest as proof that a
permission or installation is active.

Optional live probe: set GITHUB_APP_INSTALLATION_TOKEN to an ephemeral
installation token. It is used only in Authorization headers and never
serialized. The probe reads /rate_limit and /installation/repositories.
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
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        return exc.code, {}
    except (OSError, TimeoutError):
        return 0, {}


def build_telemetry(registry, token=None):
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
        declared = app.get("declared_permissions", {})
        if any(value not in ("read", "write", "admin", "none")
               for value in declared.values()):
            raise ValueError(f"{slug}: invalid declared permission value")
        rows.append({
            "slug": slug,
            "display_name": app.get("display_name"),
            "app_id": app.get("app_id"),
            "purpose": app.get("purpose"),
            "pilot": bool(app.get("pilot")),
            "declared_permissions": dict(sorted(declared.items())),
            "declared_events": sorted(app.get("declared_events", [])),
            "expected_installations": app.get("expected_installations", []),
            "evidence": {
                "registry": "checked_in_declaration",
                "live_installation": "not_observed",
                "live_permissions": "not_observed",
                "repository_scope": "not_observed",
                "rate_limit": "not_observed",
            },
        })

    if token:
        status, limits = request_json(token, "/rate_limit")
        for row in rows:
            row["evidence"]["rate_limit"] = (
                "observed" if status == 200 and isinstance(limits.get("resources"), dict)
                else f"probe_failed_http_{status}" if status else "probe_failed_network"
            )
            if status == 200:
                core = (limits.get("resources") or {}).get("core") or {}
                row["rate_limit"] = {
                    key: core.get(key) for key in ("limit", "remaining", "reset")
                }
        status, installation = request_json(token, "/installation/repositories?per_page=100")
        if status == 200 and isinstance(installation.get("repositories"), list):
            repos = sorted(r.get("full_name") for r in installation["repositories"]
                           if r.get("full_name"))
            for row in rows:
                row["evidence"]["repository_scope"] = "observed"
                row["observed_repository_scope"] = repos
        else:
            for row in rows:
                row["evidence"]["repository_scope"] = (
                    f"probe_failed_http_{status}" if status else "probe_failed_network"
                )

    return {
        "schema_version": 1,
        "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "registry_id": registry.get("registry_id"),
        "source_class": "checked_in_declaration_plus_optional_live_probe",
        "credential_policy": "no credentials or secret values are emitted",
        "apps": rows,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--output", help="write JSON to this path; default stdout")
    args = parser.parse_args(argv)
    try:
        registry = json.loads(pathlib.Path(args.registry).read_text(encoding="utf-8"))
        result = build_telemetry(registry, os.environ.get("GITHUB_APP_INSTALLATION_TOKEN"))
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
