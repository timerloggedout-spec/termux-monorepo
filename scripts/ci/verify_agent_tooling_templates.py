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
    if not candidate_keys.issubset(index_keys):
        errors.append("smods/INTEGRATIONS.json: one or more template smods_candidates are missing from the global index")

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
        elif status in {"deferred", "research_only"}:
            if entry.get("pinned_sha") is not None:
                errors.append(f"{path}: deferred/research-only entry must have pinned_sha=null")
            if path and (path in module_urls or path in gitlink_set):
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


def validate_all(root: Path = ROOT) -> list[str]:
    runtime_root = root / "refTemplates/01_Agent_Runtime"
    index_path = root / "refTemplates/smods/INTEGRATIONS.json"
    gitmodules_path = root / ".gitmodules"
    if not runtime_root.is_dir():
        return ["refTemplates/01_Agent_Runtime: missing runtime template root"]
    if not index_path.is_file():
        return ["refTemplates/smods/INTEGRATIONS.json: missing canonical smods index"]
    try:
        smods_index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"refTemplates/smods/INTEGRATIONS.json: invalid JSON: {exc}"]

    module_urls = parse_gitmodules(gitmodules_path)
    gitlinks = parse_gitlinks(root)
    template_dirs = [
        path for path in sorted(runtime_root.iterdir())
        if path.is_dir() and any((path / name).exists() for name in ("README.md", "SOURCE.txt", "integration.json"))
    ]
    errors: list[str] = []
    if not template_dirs:
        return ["refTemplates/01_Agent_Runtime: no integration templates discovered"]

    candidate_keys: set[tuple] = set()
    template_paths = {str(path.relative_to(root)) for path in template_dirs}
    for template_dir in template_dirs:
        errors.extend(validate_tree(
            template_dir, index_path, gitmodules_path,
            module_urls=module_urls, gitlinks=gitlinks, root=root,
        ))
        manifest_path = template_dir / "integration.json"
        if not manifest_path.is_file():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for candidate in manifest.get("smods_candidates", []):
            if isinstance(candidate, dict):
                candidate_keys.add((candidate.get("id"), candidate.get("path"), candidate.get("status")))

    index_entries = smods_index.get("entries", [])
    index_keys = {
        (entry.get("id"), entry.get("path"), entry.get("status"))
        for entry in index_entries if isinstance(entry, dict)
    }
    if candidate_keys != index_keys:
        errors.append("smods/INTEGRATIONS.json: global entries must exactly equal the union of all runtime-template smods_candidates")
    for entry in index_entries:
        if not isinstance(entry, dict):
            continue
        template_path = entry.get("template")
        if template_path not in template_paths:
            errors.append(f"smods/INTEGRATIONS.json: {entry.get('id')!r} references missing template {template_path!r}")
    return errors

