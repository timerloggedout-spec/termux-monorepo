"""MSM-008 offline deterministic resource and provider-candidate index."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

SCHEMA_VERSION = "msm-resource-index-v1"
REGISTRY_SCHEMA = "msm-resource-registry-v1"
PROVIDER_SCHEMA = "msm-provider-recon-v1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


class IndexError(ValueError):
    """Malformed or unsafe input rejected fail-closed."""


def _fail(message: str) -> None:
    raise IndexError(message)


def _str(value: Any, label: str, *, nonempty: bool = True) -> str:
    if not isinstance(value, str) or (nonempty and not value.strip()):
        _fail(f"{label} must be {'a non-empty' if nonempty else 'a'} string")
    return value


def _string_list(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value) or any(
        not isinstance(x, str) or not x.strip() for x in value
    ):
        _fail(f"{label} must be {'a non-empty ' if nonempty else 'a '}list of non-empty strings")
    return value


def _url(value: Any, label: str) -> str:
    text = _str(value, label)
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in text):
        _fail(f"invalid {label}")
    try:
        parsed = urlsplit(text)
        # Accessing port also rejects malformed port syntax.
        _ = parsed.port
    except ValueError as exc:
        raise IndexError(f"invalid {label}") from exc
    if parsed.scheme != "https" or not parsed.hostname or parsed.username is not None or parsed.password is not None:
        _fail(f"{label} must be an HTTPS URL without credentials")
    forbidden = {"token", "api_key", "access_token", "key", "auth", "password"}
    if any(k.casefold() in forbidden for k, _ in parse_qsl(parsed.query, keep_blank_values=True)):
        _fail(f"{label} query contains a prohibited credential parameter")
    return text


def _validate_provider(snapshot: Any) -> tuple[list[dict], set[str]]:
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != PROVIDER_SCHEMA:
        _fail("provider snapshot must use msm-provider-recon-v1")
    sources, candidates = snapshot.get("sources"), snapshot.get("model_candidates")
    if not isinstance(sources, list) or not isinstance(candidates, list):
        _fail("provider snapshot requires sources and model_candidates arrays")
    repos: set[str] = set()
    for i, source in enumerate(sources):
        label = f"sources[{i}]"
        if not isinstance(source, dict): _fail(f"{label} must be an object")
        repo = _str(source.get("repo"), f"{label}.repo")
        if repo in repos: _fail(f"duplicate provider source repo {repo}")
        repos.add(repo)
        sha = _str(source.get("commit_sha"), f"{label}.commit_sha")
        if not SHA_RE.fullmatch(sha): _fail(f"{label} requires a full lowercase commit SHA")
        files = source.get("files")
        if not isinstance(files, dict) or not files: _fail(f"{label}.files must be a non-empty object")
        for path, info in files.items():
            _str(path, f"{label} file path")
            if not isinstance(info, dict): _fail(f"{label}.files[{path}] must be an object")
            url = _url(info.get("url"), f"{label}.files[{path}].url")
            digest = _str(info.get("sha256"), f"{label}.files[{path}].sha256")
            if not HEX64_RE.fullmatch(digest): _fail(f"invalid pinned file hash for {repo}/{path}")
            if url != f"https://raw.githubusercontent.com/{repo}/{sha}/{path}":
                _fail(f"provider file URL is not pinned to its source commit/path: {repo}/{path}")
    for i, row in enumerate(candidates):
        label = f"model_candidates[{i}]"
        if not isinstance(row, dict): _fail(f"{label} must be an object")
        for field in ("provider_key", "model_key", "source_repo"):
            _str(row.get(field), f"{label}.{field}")
        if row["source_repo"] not in repos: _fail(f"{label}.source_repo is unknown to snapshot.sources")
        if row.get("runtime_eligible") is not False:
            _fail(f"{label}.runtime_eligible must be literal false")
        # Preserve candidate evidence and provenance, but check fields used downstream.
        _str(row.get("provider_name"), f"{label}.provider_name")
        _str(row.get("model_name"), f"{label}.model_name")
        if not isinstance(row.get("claims"), dict): _fail(f"{label}.claims must be an object")
        if not isinstance(row.get("blocked_reasons"), list) or any(not isinstance(x, str) for x in row["blocked_reasons"]):
            _fail(f"{label}.blocked_reasons must be a list of strings")
        if row.get("evidence_class") != "THIRD_PARTY_CLAIM": _fail(f"{label}.evidence_class must be THIRD_PARTY_CLAIM")
        if row.get("quota_remaining") is not None: _fail(f"{label}.quota_remaining must be null")
    return candidates, repos


def build_index(registry: dict, provider_snapshot: dict) -> dict:
    """Validate inputs and produce a deterministic aggregate index; performs no I/O."""
    if not isinstance(registry, dict) or registry.get("schema_version") != REGISTRY_SCHEMA:
        _fail("resource registry must use msm-resource-registry-v1")
    resources, source_inputs = registry.get("resources"), registry.get("source_inputs")
    if not isinstance(resources, list) or not isinstance(source_inputs, list):
        _fail("resource registry requires resources and source_inputs arrays")
    resource_ids: set[str] = set()
    normalized: list[dict] = []
    required = ("id", "title", "url", "kind", "tags", "mesh_roles", "implementation_paths", "next_action", "status", "evidence_class", "runtime_eligible")
    for i, row in enumerate(resources):
        label = f"resources[{i}]"
        if not isinstance(row, dict): _fail(f"{label} must be an object")
        for field in required:
            if field not in row: _fail(f"{label}.{field} is required")
        rid = _str(row["id"], f"{label}.id")
        if rid in resource_ids: _fail(f"duplicate resource id {rid}")
        resource_ids.add(rid)
        if row["runtime_eligible"] is not False: _fail(f"{label}.runtime_eligible must be literal false")
        for field in ("title", "kind", "next_action", "status", "evidence_class"):
            _str(row[field], f"{label}.{field}")
        _url(row["url"], f"{label}.url")
        for field in ("tags", "mesh_roles", "implementation_paths"):
            _string_list(row[field], f"{label}.{field}")
        normalized.append({**row, "record_type": "resource"})
    normalized_sources = []
    input_ids: set[str] = set()
    for i, row in enumerate(source_inputs):
        label = f"source_inputs[{i}]"
        if not isinstance(row, dict): _fail(f"{label} must be an object")
        for field in ("id", "url"):
            if field not in row: _fail(f"{label}.{field} is required")
        sid = _str(row["id"], f"{label}.id")
        if sid in input_ids: _fail(f"duplicate source input id {sid}")
        input_ids.add(sid)
        _url(row["url"], f"{label}.url")
        refs = _string_list(row.get("resource_ids"), f"{label}.resource_ids", nonempty=True)
        missing = set(refs) - resource_ids
        if missing: _fail(f"{label} has dangling resource references")
        normalized_sources.append(dict(row))
    candidates, _ = _validate_provider(provider_snapshot)
    provider_sources = provider_snapshot["sources"]
    for i, source in enumerate(provider_sources):
        if not isinstance(source, dict):
            _fail(f"provider sources[{i}] must be an object")
    normalized_provider_sources = sorted((dict(source) for source in provider_sources), key=lambda x: x["repo"])
    normalized_sources.sort(key=lambda x: x["id"])
    seen_provider_ids: set[tuple[str, str, str]] = set()
    for row in candidates:
        identity = (row["source_repo"], row["provider_key"], row["model_key"])
        if identity in seen_provider_ids: _fail(f"duplicate provider candidate identity {identity}")
        seen_provider_ids.add(identity)
        stable_id = "provider:" + json.dumps(identity, ensure_ascii=False, separators=(",", ":"))
        normalized.append({**row, "id": stable_id, "record_type": "provider_candidate", "runtime_eligible": False})
    normalized.sort(key=lambda x: (x["record_type"], x["id"]))
    result = {"schema_version": SCHEMA_VERSION, "resources": normalized, "sources": normalized_provider_sources, "source_inputs": normalized_sources, "blocked_reasons": ["resource and provider records are research metadata only", "runtime eligibility is always false"]}
    references = provider_snapshot.get("integration_references", [])
    if not isinstance(references, list) or any(not isinstance(row, dict) for row in references):
        _fail("provider integration_references must be an array of objects")
    result["provider_integration_references"] = sorted(references, key=lambda row: json.dumps(row, sort_keys=True))
    result["provider_blocked_reasons"] = _string_list(provider_snapshot.get("blocked_reasons", []), "provider blocked_reasons")
    if "notes_sha256" in registry:
        result["notes_sha256"] = registry["notes_sha256"]
    return result


def search(index: dict, query: str = "", *, kind: str | None = None, mesh_role: str | None = None, limit: int = 20) -> list[dict]:
    """Casefold token-AND search across record values; results have stable ID order."""
    if not isinstance(index, dict) or index.get("schema_version") != SCHEMA_VERSION or not isinstance(index.get("resources"), list):
        _fail("invalid resource index")
    if not isinstance(query, str): _fail("query must be a string")
    if kind is not None and not isinstance(kind, str): _fail("kind must be a string")
    if mesh_role is not None and not isinstance(mesh_role, str): _fail("mesh_role must be a string")
    if isinstance(limit, bool) or not isinstance(limit, int) or not limit > 0:
        _fail("limit must be a positive integer")
    tokens = query.casefold().split()
    matches = []
    for row in index["resources"]:
        if not isinstance(row, dict): _fail("index resource records must be objects")
        if kind is not None and (row.get("kind") or "").casefold() != kind.casefold(): continue
        roles = row.get("mesh_roles", [])
        if mesh_role is not None and (not isinstance(roles, list) or mesh_role.casefold() not in [str(r).casefold() for r in roles]): continue
        text = " ".join(_flatten_strings(row)).casefold()
        if all(token in text for token in tokens): matches.append(row)
    matches.sort(key=lambda x: (x.get("record_type", ""), x.get("id", "")))
    return matches[:limit]


def _flatten_strings(value: Any):
    if isinstance(value, str): yield value
    elif isinstance(value, dict):
        for key in sorted(value):
            yield str(key)
            yield from _flatten_strings(value[key])
    elif isinstance(value, list):
        for item in value: yield from _flatten_strings(item)


def write_snapshot(path: str | os.PathLike[str], snapshot: dict) -> None:
    """Atomically serialize JSON; callers construct/validate before invoking."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(snapshot, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=target.parent, prefix=f".{target.name}.", delete=False) as f:
            temp_name = f.name
            f.write(payload); f.flush(); os.fsync(f.fileno())
        os.replace(temp_name, target)
    finally:
        if temp_name and os.path.exists(temp_name): os.unlink(temp_name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default="data/model-selection-market/resource-registry.json")
    parser.add_argument("--providers", default="data/model-selection-market/provider-recon.json")
    parser.add_argument("--output")
    parser.add_argument("--query")
    parser.add_argument("--kind")
    parser.add_argument("--mesh-role")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)
    try:
        with open(args.registry, encoding="utf-8") as f: registry = json.load(f)
        with open(args.providers, encoding="utf-8") as f: providers = json.load(f)
        index = build_index(registry, providers)
        if args.query is not None:
            result = search(index, args.query, kind=args.kind, mesh_role=args.mesh_role, limit=args.limit)
        else:
            if args.kind is not None or args.mesh_role is not None or args.limit != 20:
                parser.error("--kind, --mesh-role and --limit require --query")
            result = index
        if args.output: write_snapshot(args.output, result)
        else: print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
    except (IndexError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"resource index failed; output not written: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
