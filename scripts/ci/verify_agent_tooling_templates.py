#!/usr/bin/env python3
"""Validate agent runtime integration templates and their smods dispositions.

Stdlib-only and offline. A fork_required entry is an explicit pending state,
not a gitlink. A pinned entry must match .gitmodules and a 160000 gitlink.
"""

from __future__ import annotations

import argparse
import configparser
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "refTemplates/01_Agent_Runtime/vercel-agent-toolchain"
SMODS_INDEX = ROOT / "refTemplates/smods/INTEGRATIONS.json"
REQUIRED_UPSTREAMS = {
    "agent-browser",
    "skills-cli",
    "agent-skills",
    "agent-desktop",
    "portless",
    "kitesurf",
}
ALLOWED_PIN_STATES = {"fork_required", "pinned", "deferred", "research_only"}


def parse_gitmodules(path: Path) -> dict[str, str]:
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    if path.is_file():
        parser.read(path, encoding="utf-8")
    found: dict[str, str] = {}
    for section in parser.sections():
        if not section.startswith("submodule "):
            continue
        module_path = parser.get(section, "path", fallback="")
        url = parser.get(section, "url", fallback="")
        if module_path:
            found[module_path] = url
    return found


def parse_gitlinks(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "--stage"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return {
        line.split("\t", 1)[1]
        for line in result.stdout.splitlines()
        if line.startswith("160000 ") and "\t" in line
    }


def validate_manifest(
    manifest: dict,
    smods_index: dict,
    module_urls: dict[str, str],
    gitlinks: Iterable[str],
) -> list[str]:
    errors: list[str] = []
    gitlink_set = set(gitlinks)

    if manifest.get("schema") != "agent-toolchain-template/v1":
        errors.append("integration.json: unsupported or missing schema")
    if manifest.get("template_id") != "vercel-agent-toolchain":
        errors.append("integration.json: template_id must be vercel-agent-toolchain")
    if manifest.get("status") not in {"discovered", "validated", "promoted"}:
        errors.append("integration.json: invalid lifecycle status")

    upstreams = manifest.get("upstreams")
    if not isinstance(upstreams, list):
        upstreams = []
        errors.append("integration.json: upstreams must be a list")
    ids = {u.get("id") for u in upstreams if isinstance(u, dict)}
    for required in sorted(REQUIRED_UPSTREAMS - ids):
        errors.append(f"integration.json: missing upstream {required}")
    for index, upstream in enumerate(upstreams):
        if not isinstance(upstream, dict):
            errors.append(f"integration.json: upstreams[{index}] must be an object")
            continue
        url = upstream.get("url", "")
        if not isinstance(url, str) or not url.startswith("https://github.com/"):
            errors.append(f"integration.json: upstreams[{index}] needs an HTTPS GitHub URL")

    if manifest.get("smods_index") != "refTemplates/smods/INTEGRATIONS.json":
        errors.append("integration.json: smods_index must point to the canonical INTEGRATIONS.json")

    candidates = manifest.get("smods_candidates")
    if not isinstance(candidates, list):
        candidates = []
        errors.append("integration.json: smods_candidates must be a list")
    index_entries = smods_index.get("entries")
    if not isinstance(index_entries, list):
        index_entries = []
        errors.append("smods/INTEGRATIONS.json: entries must be a list")

    def key(entry: dict) -> tuple:
        return (entry.get("id"), entry.get("path"), entry.get("status"))

    candidate_keys = {key(x) for x in candidates if isinstance(x, dict)}
    index_keys = {key(x) for x in index_entries if isinstance(x, dict)}
    if candidate_keys != index_keys:
        errors.append("smods/INTEGRATIONS.json: entries do not exactly match template smods_candidates")

    seen_paths: set[str] = set()
    for index, entry in enumerate(index_entries):
        if not isinstance(entry, dict):
            errors.append(f"smods/INTEGRATIONS.json: entries[{index}] must be an object")
            continue
        status = entry.get("status")
        path = entry.get("path")
        if status not in ALLOWED_PIN_STATES:
            errors.append(f"smods/INTEGRATIONS.json: entries[{index}] has invalid status {status!r}")
            continue
        if status in {"fork_required", "pinned"}:
            if not isinstance(path, str) or not path.startswith("refTemplates/smods/"):
                errors.append(f"smods/INTEGRATIONS.json: entries[{index}] requires a refTemplates/smods path")
                continue
            if path in seen_paths:
                errors.append(f"smods/INTEGRATIONS.json: duplicate path {path}")
            seen_paths.add(path)
        if status == "fork_required":
            if path in module_urls or path in gitlink_set:
                errors.append(f"{path}: fork_required must not be represented as a .gitmodules entry or gitlink")
            if entry.get("pinned_sha") is not None:
                errors.append(f"{path}: fork_required must have pinned_sha=null")
        elif status == "pinned":
            expected_url = entry.get("fork_url")
            if not isinstance(expected_url, str) or module_urls.get(path) != expected_url:
                errors.append(f"{path}: pinned entry must match the exact .gitmodules fork_url")
            if path not in gitlink_set:
                errors.append(f"{path}: pinned entry is missing its 160000 gitlink")
            sha = entry.get("pinned_sha")
            if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha.lower()):
                errors.append(f"{path}: pinned entry needs a 40-character immutable commit SHA")
        elif path and (path in module_urls or path in gitlink_set):
            errors.append(f"{path}: deferred/research-only entry must not claim a live gitlink")

    return errors


def validate_tree(
    template_dir: Path,
    smods_index_path: Path,
    gitmodules_path: Path,
    module_urls: dict[str, str] | None = None,
    gitlinks: Iterable[str] | None = None,
    root: Path = ROOT,
) -> list[str]:
    errors: list[str] = []
    for name in ("README.md", "SOURCE.txt", "integration.json"):
        path = template_dir / name
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            errors.append(f"{path.relative_to(root)}: missing or empty {name}")
    if errors:
        return errors
    try:
        manifest = json.loads((template_dir / "integration.json").read_text(encoding="utf-8"))
        index = json.loads(smods_index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid integration JSON: {exc}"]
    return errors + validate_manifest(
        manifest,
        index,
        module_urls if module_urls is not None else parse_gitmodules(gitmodules_path),
        gitlinks if gitlinks is not None else parse_gitlinks(root),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate_tree(
        root / "refTemplates/01_Agent_Runtime/vercel-agent-toolchain",
        root / "refTemplates/smods/INTEGRATIONS.json",
        root / ".gitmodules",
        root=root,
    )
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: Vercel agent toolchain template and smods dispositions are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
