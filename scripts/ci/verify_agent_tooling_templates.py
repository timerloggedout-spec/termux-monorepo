#!/usr/bin/env python3
"""Validate agent runtime integration templates and their smods dispositions.

Stdlib-only and offline. A fork_required entry is an explicit pending state,
not a gitlink. A pinned entry must match .gitmodules and a 160000 gitlink.
"""

from __future__ import annotations

import argparse
import configparser
import json
import re
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


def parse_gitlinks(root: Path) -> dict[str, str]:
    result = subprocess.run(
        ["git", "ls-files", "--stage"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    found: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if not line.startswith("160000 ") or "\t" not in line:
            continue
        metadata, path = line.split("\t", 1)
        fields = metadata.split()
        if len(fields) >= 3:
            found[path] = fields[1]
    return found


def validate_manifest(
    manifest: dict,
    smods_index: dict,
    module_urls: dict[str, str],
    gitlinks: Iterable[str] | dict[str, str],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["integration.json: JSON root must be an object"]
    if not isinstance(smods_index, dict):
        return ["smods/INTEGRATIONS.json: JSON root must be an object"]
    gitlink_shas = gitlinks if isinstance(gitlinks, dict) else {}
    gitlink_set = set(gitlinks)

    if manifest.get("schema") != "agent-toolchain-template/v1":
        errors.append("integration.json: unsupported or missing schema")
    if manifest.get("template_id") != "vercel-agent-toolchain":
        errors.append("integration.json: template_id must be vercel-agent-toolchain")
    lifecycle_status = manifest.get("status")
    if not isinstance(lifecycle_status, str) or lifecycle_status not in {"discovered", "validated", "promoted"}:
        errors.append("integration.json: invalid lifecycle status")

    upstreams = manifest.get("upstreams")
    if not isinstance(upstreams, list):
        upstreams = []
        errors.append("integration.json: upstreams must be a list")
    ids = {u.get("id") for u in upstreams if isinstance(u, dict) and isinstance(u.get("id"), str)}
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

    def key(entry: dict) -> tuple | None:
        values = (entry.get("id"), entry.get("path"), entry.get("status"))
        if not all(isinstance(value, str) and value for value in values):
            return None
        return values

    candidate_keys: set[tuple] = set()
    for candidate_index, candidate in enumerate(candidates):
        candidate_key = key(candidate) if isinstance(candidate, dict) else None
        if candidate_key is None:
            errors.append(f"integration.json: smods_candidates[{candidate_index}] needs non-empty string id/path/status")
        else:
            candidate_keys.add(candidate_key)

    index_keys: set[tuple] = set()
    index_by_key: dict[tuple, dict] = {}
    seen_ids: set[str] = set()
    for entry_index, entry in enumerate(index_entries):
        entry_key = key(entry) if isinstance(entry, dict) else None
        if entry_key is None:
            errors.append(f"smods/INTEGRATIONS.json: entries[{entry_index}] needs non-empty string id/path/status")
        else:
            index_keys.add(entry_key)
            index_by_key[entry_key] = entry
            if entry_key[0] in seen_ids:
                errors.append(f"smods/INTEGRATIONS.json: duplicate integration id {entry_key[0]}")
            seen_ids.add(entry_key[0])
    if not candidate_keys.issubset(index_keys):
        errors.append("smods/INTEGRATIONS.json: one or more template smods_candidates are missing from the global index")
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        candidate_key = key(candidate)
        if candidate_key is None or candidate_key not in index_by_key:
            continue
        indexed = index_by_key[candidate_key]
        for field in ("upstream", "fork_url", "pinned_sha"):
            if candidate.get(field) != indexed.get(field):
                errors.append(f"smods/INTEGRATIONS.json: candidate {candidate_key[0]} has mismatched {field}")

    seen_paths: set[str] = set()
    for index, entry in enumerate(index_entries):
        if not isinstance(entry, dict):
            errors.append(f"smods/INTEGRATIONS.json: entries[{index}] must be an object")
            continue
        status = entry.get("status")
        path = entry.get("path")
        if not isinstance(status, str) or status not in ALLOWED_PIN_STATES:
            errors.append(f"smods/INTEGRATIONS.json: entries[{index}] has invalid status {status!r}")
            continue
        if path is not None and not isinstance(path, str):
            errors.append(f"smods/INTEGRATIONS.json: entries[{index}] path must be a string or null")
            continue
        if path is not None:
            if not path.startswith("refTemplates/smods/"):
                errors.append(f"smods/INTEGRATIONS.json: entries[{index}] path must be under refTemplates/smods/")
                continue
            if path in seen_paths:
                errors.append(f"smods/INTEGRATIONS.json: duplicate path {path}")
            seen_paths.add(path)
        if status in {"fork_required", "pinned"} and not path:
            errors.append(f"smods/INTEGRATIONS.json: entries[{index}] requires a refTemplates/smods path")
            continue
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
            elif gitlink_shas.get(path) != sha:
                errors.append(f"{path}: pinned_sha does not match the actual 160000 gitlink SHA")
        elif status in {"deferred", "research_only"}:
            if entry.get("pinned_sha") is not None:
                errors.append(f"{path}: deferred/research-only entry must have pinned_sha=null")
            if path and (path in module_urls or path in gitlink_set):
                errors.append(f"{path}: deferred/research-only entry must not claim a live gitlink")

    return errors


READ_ONLY_ACTIONS = {"navigate", "snapshot", "scroll", "wait", "read", "get"}
WRITE_ACTIONS = {"click", "fill", "interact", "download", "upload", "state"}


def validate_security_examples(template_dir: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    files = manifest.get("security_policy_files")
    if not isinstance(files, dict):
        return ["integration.json: security_policy_files must be an object"]
    required_keys = {"read_only", "authorized_write", "mcp_read_only", "mcp_authorized_write"}
    if not required_keys.issubset(files):
        return ["integration.json: security_policy_files is missing required policy/example paths"]
    required_files = set(manifest.get("required_files", []))
    for key, name in files.items():
        if not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts or name not in required_files:
            errors.append(f"security_policy_files.{key}: unsafe or unrequired path {name!r}")
    if errors:
        return errors

    def load_json(name: str) -> dict | None:
        path = template_dir / name
        if path.is_symlink():
            errors.append(f"{name}: symlinked policy/config files are not allowed")
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                errors.append(f"{name}: JSON root must be an object")
                return None
            return value
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{name}: cannot read valid JSON: {exc}")
            return None

    readonly = load_json(files["read_only"])
    authorized = load_json(files["authorized_write"])
    if readonly is not None:
        raw_allow = readonly.get("allow")
        if not isinstance(raw_allow, list) or not all(isinstance(action, str) for action in raw_allow):
            errors.append("read-only action policy allow must be a string array")
        else:
            allow = set(raw_allow)
            if readonly.get("default") != "deny" or not allow or not allow.issubset(READ_ONLY_ACTIONS):
                errors.append("read-only action policy must default-deny and allow only read/navigation categories")
    if authorized is not None:
        raw_allow = authorized.get("allow")
        if not isinstance(raw_allow, list) or not all(isinstance(action, str) for action in raw_allow):
            errors.append("authorized-write policy allow must be a string array")
        else:
            allow = set(raw_allow)
            if authorized.get("default") != "deny" or not (READ_ONLY_ACTIONS | WRITE_ACTIONS).issuperset(allow):
                errors.append("authorized-write policy must default-deny and use only reviewed read/write categories")
            if not WRITE_ACTIONS.issubset(allow):
                errors.append("authorized-write policy must explicitly enumerate click/fill/interact/download/upload/state")
            if "eval" in allow or "network" in allow:
                errors.append("authorized-write policy must not enable eval or network control")

    def validate_mcp_config(name: str, policy_name: str, write_mode: bool) -> None:
        config = load_json(name)
        if config is None:
            return
        servers = config.get("mcpServers")
        if not isinstance(servers, dict) or len(servers) != 1:
            errors.append(f"{name}: expected exactly one mcpServers entry")
            return
        server = next(iter(servers.values()))
        args = server.get("args") if isinstance(server, dict) else None
        if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
            errors.append(f"{name}: server args must be a string array")
            return
        if "--tools" not in args or args[args.index("--tools") + 1:args.index("--tools") + 2] != ["core"]:
            errors.append(f"{name}: MCP must start with the least-privilege core tool profile")
        if "--session" not in args:
            errors.append(f"{name}: MCP must use a named isolated session")
        else:
            session_position = args.index("--session")
            session_name = args[session_position + 1] if session_position + 1 < len(args) else ""
            if not re.fullmatch(r"[A-Za-z0-9_-]+", session_name):
                errors.append(f"{name}: session name must be path-safe alphanumeric/hyphen/underscore")
        policy_arg = args[args.index("--action-policy") + 1] if "--action-policy" in args and args.index("--action-policy") + 1 < len(args) else ""
        if not policy_arg.endswith(policy_name):
            errors.append(f"{name}: MCP must reference {policy_name}")
        for flag in ("--content-boundaries", "--max-output", "--allowed-domains"):
            if flag not in args:
                errors.append(f"{name}: missing required security flag {flag}")
        if "--cdp" in args and "--allowed-domains" in args:
            errors.append(f"{name}: upstream domain allowlist cannot be combined with CDP attach")
        if "--tools" in args and "all" in args:
            errors.append(f"{name}: do not expose all MCP tools by default")
        if write_mode:
            if "--confirm-actions" not in args:
                errors.append(f"{name}: authorized-write MCP must require action confirmations")
            else:
                position = args.index("--confirm-actions")
                confirmed = set(args[position + 1].split(",")) if position + 1 < len(args) else set()
                if not WRITE_ACTIONS.issubset(confirmed):
                    errors.append(f"{name}: confirm-actions must cover all write categories")

    validate_mcp_config(files["mcp_read_only"], files["read_only"], False)
    validate_mcp_config(files["mcp_authorized_write"], files["authorized_write"], True)
    return errors


def validate_tree(
    template_dir: Path,
    smods_index_path: Path,
    gitmodules_path: Path,
    module_urls: dict[str, str] | None = None,
    gitlinks: Iterable[str] | dict[str, str] | None = None,
    root: Path = ROOT,
) -> list[str]:
    errors: list[str] = []
    manifest_path = template_dir / "integration.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        return [f"{manifest_path.relative_to(root)}: missing regular integration.json"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        index = json.loads(smods_index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid integration JSON: {exc}"]
    if not isinstance(manifest, dict):
        return ["integration.json: JSON root must be an object"]
    if not isinstance(index, dict):
        return ["smods/INTEGRATIONS.json: JSON root must be an object"]

    required_files = manifest.get("required_files", ["README.md", "SOURCE.txt", "integration.json"])
    if (
        not isinstance(required_files, list)
        or not all(isinstance(name, str) for name in required_files)
        or not {"README.md", "SOURCE.txt", "integration.json"}.issubset(set(required_files))
    ):
        errors.append("integration.json: required_files must be a string array including README.md, SOURCE.txt, and integration.json")
        return errors
    for name in required_files:
        if not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts:
            errors.append(f"integration.json: unsafe required_files path {name!r}")
            continue
        path = template_dir / name
        if path.is_symlink():
            errors.append(f"{path.relative_to(root)}: symlinked template files are not allowed")
            continue
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            errors.append(f"{path.relative_to(root)}: missing or empty required file")

    errors.extend(validate_manifest(
        manifest,
        index,
        module_urls if module_urls is not None else parse_gitmodules(gitmodules_path),
        gitlinks if gitlinks is not None else parse_gitlinks(root),
    ))
    errors.extend(validate_security_examples(template_dir, manifest))
    return errors

def validate_all(root: Path = ROOT) -> list[str]:
    runtime_root = root / "refTemplates/01_Agent_Runtime"
    index_path = root / "refTemplates/smods/INTEGRATIONS.json"
    gitmodules_path = root / ".gitmodules"
    if runtime_root.is_symlink() or not runtime_root.is_dir():
        return ["refTemplates/01_Agent_Runtime: missing regular runtime template root"]
    if index_path.is_symlink() or not index_path.is_file():
        return ["refTemplates/smods/INTEGRATIONS.json: missing canonical or regular-file sMods index"]
    try:
        smods_index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"refTemplates/smods/INTEGRATIONS.json: invalid JSON: {exc}"]
    if not isinstance(smods_index, dict):
        return ["refTemplates/smods/INTEGRATIONS.json: JSON root must be an object"]
    if smods_index.get("schema") != "smods-integration-index/v1":
        return ["refTemplates/smods/INTEGRATIONS.json: unsupported or missing schema"]
    if not isinstance(smods_index.get("entries"), list):
        return ["refTemplates/smods/INTEGRATIONS.json: entries must be a list"]

    try:
        module_urls = parse_gitmodules(gitmodules_path)
        gitlinks = parse_gitlinks(root)
    except (configparser.Error, OSError, subprocess.CalledProcessError) as exc:
        return [f"unable to inspect .gitmodules/gitlinks: {exc}"]
    children = sorted(runtime_root.iterdir())
    errors: list[str] = [
        f"{path.relative_to(root)}: symlinked runtime template directories are not allowed"
        for path in children if path.is_symlink()
    ]
    template_dirs = [
        path for path in children
        if not path.is_symlink() and path.is_dir()
        and any((path / name).exists() for name in ("README.md", "SOURCE.txt", "integration.json"))
    ]
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
        if manifest_path.is_symlink() or not manifest_path.is_file():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(manifest, dict):
            continue
        for candidate in manifest.get("smods_candidates", []):
            if not isinstance(candidate, dict):
                continue
            values = (candidate.get("id"), candidate.get("path"), candidate.get("status"))
            if all(isinstance(value, str) and value for value in values):
                candidate_keys.add(values)

    index_entries = smods_index.get("entries", [])
    index_keys: set[tuple] = set()
    for entry in index_entries:
        if not isinstance(entry, dict):
            continue
        values = (entry.get("id"), entry.get("path"), entry.get("status"))
        if all(isinstance(value, str) and value for value in values):
            index_keys.add(values)
    if candidate_keys != index_keys:
        errors.append("smods/INTEGRATIONS.json: global entries must exactly equal the union of all runtime-template smods_candidates")
    for entry in index_entries:
        if not isinstance(entry, dict):
            continue
        template_path = entry.get("template")
        if not isinstance(template_path, str) or template_path not in template_paths:
            errors.append(f"smods/INTEGRATIONS.json: {entry.get('id')!r} references missing template {template_path!r}")
    return errors

