#!/usr/bin/env python3
"""Validate third-party reference provenance and sMods promotion claims."""

from __future__ import annotations

import argparse
import configparser
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DISPOSITION = Path("refTemplates/13_Third_Party_Refs/open-source-radar-2026-11-15/smods-disposition.json")
REGISTRY = Path("refTemplates/smods/INTEGRATIONS.json")
ALLOWED = {"research_only", "selected_no_fork", "fork_required", "pinned", "deferred"}


def read_gitmodules(root: Path) -> dict[str, str]:
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    path = root / ".gitmodules"
    if path.is_file():
        parser.read(path, encoding="utf-8")
    return {
        parser.get(section, "path", fallback=""): parser.get(section, "url", fallback="")
        for section in parser.sections()
        if section.startswith("submodule ") and parser.get(section, "path", fallback="")
    }


def read_gitlinks(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "--stage"], cwd=root, capture_output=True,
        text=True, check=True,
    )
    return {
        line.split("\t", 1)[1]
        for line in result.stdout.splitlines()
        if line.startswith("160000 ") and "\t" in line
    }


def validate(
    document: object,
    root: Path,
    modules: dict[str, str],
    gitlinks: set[str],
    registry: object | None = None,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict) or document.get("schema") != "third-party-ref-disposition/v1":
        return ["unsupported or missing third-party-ref-disposition/v1 schema"]
    source_record = document.get("source_record")
    if not isinstance(source_record, str) or not source_record.startswith("refTemplates/13_Third_Party_Refs/"):
        errors.append("source_record must point inside refTemplates/13_Third_Party_Refs")
    else:
        for name in ("README.md", "SOURCE.txt"):
            if not (root / source_record / name).is_file():
                errors.append(f"{source_record}/{name} is missing")
    if document.get("canonical_smods_registry") != str(REGISTRY):
        errors.append(f"canonical_smods_registry must be {REGISTRY.as_posix()}")

    entries = document.get("entries")
    if not isinstance(entries, list):
        return errors + ["entries must be a list"]
    seen: set[str] = set()
    registry_entries = []
    if isinstance(registry, dict) and isinstance(registry.get("entries"), list):
        registry_entries = registry["entries"]

    for i, item in enumerate(entries):
        label = f"entries[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in seen:
            errors.append(f"{label} needs a unique non-empty id")
        else:
            seen.add(ident)
        upstream = item.get("upstream")
        if not isinstance(upstream, str) or not upstream.startswith("https://github.com/"):
            errors.append(f"{label} needs an HTTPS GitHub upstream")
        status = item.get("status")
        if status not in ALLOWED:
            errors.append(f"{label} has invalid status {status!r}")
            continue

        path = item.get("smods_path")
        fork_url = item.get("fork_url")
        sha = item.get("pinned_sha")
        if status in {"research_only", "deferred", "selected_no_fork"}:
            if item.get("fork_required") is not False or item.get("live_gitlink") is not False:
                errors.append(f"{label}: {status} must explicitly keep fork_required=false and live_gitlink=false")
            if path is not None or fork_url is not None or sha is not None:
                errors.append(f"{label}: {status} must not claim a fork path, fork URL, or pinned SHA")
        elif status in {"fork_required", "pinned"}:
            if item.get("fork_required") is not True:
                errors.append(f"{label}: {status} must set fork_required=true")
            if not isinstance(path, str) or not path.startswith("refTemplates/smods/"):
                errors.append(f"{label}: {status} needs a refTemplates/smods path")
            if not isinstance(fork_url, str) or not fork_url.startswith("https://github.com/"):
                errors.append(f"{label}: {status} needs an HTTPS fork_url")
            matches = [
                entry for entry in registry_entries
                if isinstance(entry, dict)
                and entry.get("id") == ident
                and entry.get("path") == path
                and entry.get("fork_url") == fork_url
                and entry.get("status") == status
            ]
            if not matches:
                errors.append(f"{label}: {status} must have a matching entry in {REGISTRY.as_posix()}")
            if status == "fork_required":
                if item.get("live_gitlink") is not False or path in modules or path in gitlinks:
                    errors.append(f"{label}: fork_required must not claim or contain a live gitlink")
                if sha is not None:
                    errors.append(f"{label}: fork_required must have pinned_sha=null")
            else:
                if item.get("live_gitlink") is not True:
                    errors.append(f"{label}: pinned must set live_gitlink=true")
                if modules.get(path) != fork_url:
                    errors.append(f"{label}: pinned fork URL does not match .gitmodules")
                if path not in gitlinks:
                    errors.append(f"{label}: pinned has no 160000 gitlink")
                if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha.lower()):
                    errors.append(f"{label}: pinned needs a 40-character immutable SHA")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        document = json.loads((args.root / DISPOSITION).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read {DISPOSITION}: {exc}", file=sys.stderr)
        return 1
    registry_path = args.root / REGISTRY
    registry = None
    if registry_path.is_file():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"FAIL: invalid {REGISTRY}: {exc}", file=sys.stderr)
            return 1
    errors = validate(document, args.root, read_gitmodules(args.root), read_gitlinks(args.root), registry)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"OK: validated {len(document['entries'])} third-party reference dispositions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
