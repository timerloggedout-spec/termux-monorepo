#!/usr/bin/env python3
"""Compile a validated, metadata-only context relationship matrix.

The compiler deliberately accepts only normalized records.  Collection from GitHub
and source parsing are separate concerns so this command is deterministic, easy to
test, and safe to run on an untrusted pull request fixture.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import sys
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
COMPILER_ID = "archwiz.context_relationships.compiler@1.0"

NODE_KINDS = {
    "repository",
    "directory",
    "file",
    "symbol",
    "module",
    "commit",
    "pull_request",
    "issue",
    "issue_comment",
    "review",
    "review_comment",
    "label",
    "scope",
    "alias",
}

EDGE_TYPES = {
    "DEFINES",
    "IMPORTS",
    "CALLS_OR_REFERENCES",
    "TOUCHES",
    "CHANGED_IN",
    "HAS_COMMIT",
    "COMMENTS_ON",
    "REVIEWS",
    "MENTIONS",
    "CLOSES",
    "REFERENCES",
    "LABELED_AS",
    "IN_SCOPE",
    "CO_CHANGED_WITH",
    "SIMILAR_TO",
    "POSSIBLE_CONTEXT",
}

CANDIDATE_EDGE_TYPES = {"CO_CHANGED_WITH", "SIMILAR_TO", "POSSIBLE_CONTEXT"}
EVIDENCE_KINDS = {
    "ast",
    "git_commit",
    "github_api",
    "github_reference",
    "scope_registry",
    "co_change",
    "lexical_similarity",
    "manual_fixture",
}

BANNED_ATTRIBUTE_KEYS = re.compile(
    r"(?:^|_)(?:body|content|raw_body|thinking_content|token|secret|password|"
    r"cookie|credential|api_key|private_key)(?:$|_)",
    re.IGNORECASE,
)
SENSITIVE_PATH_MARKERS = {
    ".deepcli",
    "session_store",
    "browser-data",
    "browser-profile",
    "chrome-profile",
    "chromium-profile",
    ".ssh",
}


class CompilationError(ValueError):
    """A source record violates the context relationship contract."""


def canonical_json(value: Any) -> str:
    """Return a stable JSON representation suitable for IDs and output files."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_id(prefix: str, *parts: str) -> str:
    """Create a stable opaque identifier from the supplied canonical parts."""
    payload = "\x00".join(parts).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(payload).hexdigest()[:20]}"


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CompilationError(f"{label} must be an object")
    return value


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CompilationError(f"{label} must be a non-empty string")
    return value.strip()


def normalize_timestamp(value: Any, label: str) -> str:
    timestamp = require_string(value, label)
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CompilationError(f"{label} must be ISO-8601: {timestamp!r}") from exc
    if parsed.tzinfo is None:
        raise CompilationError(f"{label} must include a UTC offset: {timestamp!r}")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def path_is_sensitive(path: str, exclusions: Iterable[str]) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    parts = {part.lower() for part in normalized.split("/")}
    if any(marker in part for marker in SENSITIVE_PATH_MARKERS for part in parts):
        return True
    lowered = normalized.lower()
    if any(token in lowered for token in (".env", "_token", "_credential", "_api_key")):
        return True
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in exclusions)


def reject_sensitive_values(value: Any, label: str, exclusions: Iterable[str]) -> None:
    """Reject payload content that cannot safely become shared index metadata."""
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            if BANNED_ATTRIBUTE_KEYS.search(key_text):
                raise CompilationError(f"{label} contains prohibited field {key_text!r}")
            if (
                key_text.lower() in {"path", "file", "file_path"}
                and isinstance(nested, str)
                and path_is_sensitive(nested, exclusions)
            ):
                raise CompilationError(f"{label} references excluded path {nested!r}")
            reject_sensitive_values(nested, f"{label}.{key_text}", exclusions)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            reject_sensitive_values(nested, f"{label}[{index}]", exclusions)


def load_json(path: Path, label: str) -> Mapping[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CompilationError(f"{label} does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CompilationError(f"{label} is not valid JSON: {exc}") from exc
    return require_mapping(loaded, label)


def load_exclusions(scope_registry_path: Path | None) -> tuple[list[str], str | None]:
    if scope_registry_path is None:
        return [], None
    registry = load_json(scope_registry_path, "scope registry")
    exclusions = require_mapping(registry.get("exclusions", {}), "scope registry exclusions")
    patterns = exclusions.get("path_globs", [])
    if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
        raise CompilationError("scope registry exclusions.path_globs must be a string list")
    return sorted(patterns), digest_file(scope_registry_path)


def load_schema(schema_path: Path | None) -> str | None:
    """Verify that the external schema and runtime contract cannot silently drift."""
    if schema_path is None:
        return None
    schema = load_json(schema_path, "relationship schema")
    try:
        version = schema["properties"]["schema_version"]["const"]
        node_kinds = set(schema["$defs"]["node"]["properties"]["kind"]["enum"])
        edge_types = set(schema["$defs"]["edge"]["properties"]["type"]["enum"])
        evidence_kinds = set(schema["$defs"]["evidence"]["properties"]["kind"]["enum"])
    except (KeyError, TypeError) as exc:
        raise CompilationError("relationship schema is missing its required contract definitions") from exc
    if version != SCHEMA_VERSION:
        raise CompilationError(
            f"relationship schema version {version!r} does not match compiler version {SCHEMA_VERSION!r}"
        )
    if node_kinds != NODE_KINDS or edge_types != EDGE_TYPES or evidence_kinds != EVIDENCE_KINDS:
        raise CompilationError("relationship schema vocabulary does not match the compiler contract")
    return digest_file(schema_path)


def raw_reference(kind: str, external_id: str) -> str:
    return f"{kind}:{external_id}"


def normalize_node(
    raw: Mapping[str, Any], repository_key: str, exclusions: Iterable[str]
) -> tuple[str, dict[str, Any]]:
    kind = require_string(raw.get("kind"), "node.kind")
    if kind not in NODE_KINDS:
        raise CompilationError(f"unsupported node kind {kind!r}")
    external_id = require_string(raw.get("external_id"), "node.external_id")
    attributes = require_mapping(raw.get("attributes"), "node.attributes")
    reject_sensitive_values(attributes, f"node {raw_reference(kind, external_id)} attributes", exclusions)
    node_id = stable_id("node", repository_key, kind, external_id)
    node: dict[str, Any] = {
        "id": node_id,
        "kind": kind,
        "external_id": external_id,
        "attributes": json.loads(canonical_json(attributes)),
    }
    if "url" in raw:
        node["url"] = require_string(raw["url"], "node.url")
    if "observed_at" in raw:
        node["observed_at"] = normalize_timestamp(raw["observed_at"], "node.observed_at")
    return raw_reference(kind, external_id), node


def normalize_evidence(
    raw: Mapping[str, Any], exclusions: Iterable[str], edge_label: str
) -> dict[str, Any]:
    kind = require_string(raw.get("kind"), f"{edge_label}.evidence.kind")
    if kind not in EVIDENCE_KINDS:
        raise CompilationError(f"{edge_label} has unsupported evidence kind {kind!r}")
    source = require_string(raw.get("source"), f"{edge_label}.evidence.source")
    collector = require_string(raw.get("collector"), f"{edge_label}.evidence.collector")
    details = raw.get("details", {})
    details = require_mapping(details, f"{edge_label}.evidence.details")
    reject_sensitive_values(details, f"{edge_label}.evidence.details", exclusions)
    evidence: dict[str, Any] = {
        "kind": kind,
        "source": source,
        "collector": collector,
        "details": json.loads(canonical_json(details)),
    }
    if "observed_at" in raw:
        evidence["observed_at"] = normalize_timestamp(
            raw["observed_at"], f"{edge_label}.evidence.observed_at"
        )
    return evidence


def evidence_key(evidence: Mapping[str, Any]) -> str:
    return canonical_json(evidence)


def normalize_edge(
    raw: Mapping[str, Any],
    node_ids: Mapping[str, str],
    exclusions: Iterable[str],
) -> tuple[tuple[str, str, str, str], dict[str, Any]]:
    edge_type = require_string(raw.get("type"), "edge.type")
    if edge_type not in EDGE_TYPES:
        raise CompilationError(f"unsupported edge type {edge_type!r}")
    classification = require_string(raw.get("classification"), "edge.classification")
    if classification not in {"verified", "candidate"}:
        raise CompilationError(f"edge.classification must be verified or candidate, got {classification!r}")
    if (edge_type in CANDIDATE_EDGE_TYPES) != (classification == "candidate"):
        raise CompilationError(
            f"edge {edge_type} must use {'candidate' if edge_type in CANDIDATE_EDGE_TYPES else 'verified'} classification"
        )
    source_ref = require_string(raw.get("source"), "edge.source")
    target_ref = require_string(raw.get("target"), "edge.target")
    if source_ref not in node_ids or target_ref not in node_ids:
        missing = source_ref if source_ref not in node_ids else target_ref
        raise CompilationError(f"edge {edge_type} references unknown node {missing!r}")
    observed_at = normalize_timestamp(raw.get("observed_at"), "edge.observed_at")
    evidence_raw = raw.get("evidence")
    if not isinstance(evidence_raw, list) or not evidence_raw:
        raise CompilationError(f"edge {edge_type} requires one or more evidence records")
    evidence = [
        normalize_evidence(require_mapping(item, "edge.evidence item"), exclusions, f"edge {edge_type}")
        for item in evidence_raw
    ]
    attributes = require_mapping(raw.get("attributes", {}), "edge.attributes")
    reject_sensitive_values(attributes, f"edge {edge_type} attributes", exclusions)
    score = raw.get("score", 1.0 if classification == "verified" else None)
    if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= float(score) <= 1:
        raise CompilationError(f"edge {edge_type} score must be a number from 0 to 1")
    if classification == "candidate" and "score" not in raw:
        raise CompilationError(f"candidate edge {edge_type} requires an explicit score")
    source_id, target_id = node_ids[source_ref], node_ids[target_ref]
    edge_key = (edge_type, source_id, target_id, classification)
    edge = {
        "id": stable_id("edge", edge_type, source_id, target_id, classification),
        "type": edge_type,
        "source": source_id,
        "target": target_id,
        "classification": classification,
        "score": float(score),
        "observed_at": observed_at,
        "evidence": sorted(evidence, key=evidence_key),
        "attributes": json.loads(canonical_json(attributes)),
    }
    return edge_key, edge


def merge_edge(existing: dict[str, Any], incoming: Mapping[str, Any]) -> dict[str, Any]:
    """Merge identical relationships while retaining every distinct evidence record."""
    merged = dict(existing)
    existing_evidence = {evidence_key(item): item for item in existing["evidence"]}
    for item in incoming["evidence"]:
        existing_evidence[evidence_key(item)] = item
    merged["evidence"] = [existing_evidence[key] for key in sorted(existing_evidence)]
    merged["observed_at"] = min(existing["observed_at"], incoming["observed_at"])
    merged["score"] = max(float(existing["score"]), float(incoming["score"]))
    if canonical_json(existing["attributes"]) != canonical_json(incoming["attributes"]):
        raise CompilationError(
            f"duplicate edge {existing['id']} has contradictory attributes; preserve it as a separate relation"
        )
    return merged


def compile_seed(
    seed: Mapping[str, Any],
    scope_registry_path: Path | None = None,
    schema_path: Path | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    """Compile a normalized seed into canonical graph records and a sparse matrix."""
    if seed.get("schema_version") != SCHEMA_VERSION:
        raise CompilationError(f"schema_version must be {SCHEMA_VERSION!r}")
    repository = require_mapping(seed.get("repository"), "repository")
    owner = require_string(repository.get("owner"), "repository.owner")
    name = require_string(repository.get("name"), "repository.name")
    default_branch = require_string(repository.get("default_branch"), "repository.default_branch")
    repository_key = f"{owner}/{name}@{default_branch}"
    exclusions, scope_digest = load_exclusions(scope_registry_path)
    schema_digest = load_schema(schema_path)

    raw_nodes = seed.get("nodes")
    if not isinstance(raw_nodes, list):
        raise CompilationError("nodes must be an array")
    raw_to_node: dict[str, dict[str, Any]] = {}
    for raw in raw_nodes:
        raw_ref, node = normalize_node(require_mapping(raw, "node"), repository_key, exclusions)
        if raw_ref in raw_to_node:
            if canonical_json(raw_to_node[raw_ref]) != canonical_json(node):
                raise CompilationError(f"duplicate node {raw_ref!r} has contradictory metadata")
            continue
        raw_to_node[raw_ref] = node
    if not raw_to_node:
        raise CompilationError("nodes must not be empty")
    node_ids = {raw_ref: node["id"] for raw_ref, node in raw_to_node.items()}

    raw_edges = seed.get("edges")
    if not isinstance(raw_edges, list):
        raise CompilationError("edges must be an array")
    edges_by_key: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for raw in raw_edges:
        edge_key, edge = normalize_edge(require_mapping(raw, "edge"), node_ids, exclusions)
        edges_by_key[edge_key] = (
            merge_edge(edges_by_key[edge_key], edge) if edge_key in edges_by_key else edge
        )

    nodes = sorted(raw_to_node.values(), key=lambda item: item["id"])
    edges = sorted(edges_by_key.values(), key=lambda item: item["id"])
    matrix_rows: dict[tuple[str, str], dict[str, Any]] = {}
    for edge in edges:
        key = (edge["source"], edge["target"])
        row = matrix_rows.setdefault(
            key,
            {"source": edge["source"], "target": edge["target"], "verified": [], "candidate": []},
        )
        row[edge["classification"]].append(
            {"edge_id": edge["id"], "type": edge["type"], "score": edge["score"]}
        )
    for row in matrix_rows.values():
        row["verified"].sort(key=lambda item: (item["type"], item["edge_id"]))
        row["candidate"].sort(key=lambda item: (item["type"], item["edge_id"]))
    matrix = {
        "schema_version": SCHEMA_VERSION,
        "repository": {"owner": owner, "name": name, "default_branch": default_branch},
        "node_order": [node["id"] for node in nodes],
        "rows": sorted(matrix_rows.values(), key=lambda item: (item["source"], item["target"])),
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "compiler": COMPILER_ID,
        "repository": f"{owner}/{name}",
        "default_branch": default_branch,
        "scope_registry_sha256": scope_digest,
        "schema_sha256": schema_digest,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "verified_edge_count": sum(edge["classification"] == "verified" for edge in edges),
        "candidate_edge_count": sum(edge["classification"] == "candidate" for edge in edges),
        "latest_observed_at": max(
            [node.get("observed_at", "") for node in nodes]
            + [edge["observed_at"] for edge in edges]
        )
        or None,
    }
    return nodes, edges, matrix, manifest


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: Iterable[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(canonical_json(record) + "\n")


def write_artifacts(
    output_dir: Path,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    matrix: Mapping[str, Any],
    manifest: Mapping[str, Any],
    seed_path: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_with_input = dict(manifest)
    manifest_with_input["input_sha256"] = digest_file(seed_path)
    write_jsonl(output_dir / "nodes.jsonl", nodes)
    write_jsonl(output_dir / "edges.jsonl", edges)
    write_json(output_dir / "matrix.json", matrix)
    write_json(output_dir / "manifest.json", manifest_with_input)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Normalized JSON seed to validate and compile")
    parser.add_argument(
        "--scope-registry",
        type=Path,
        default=Path("config/context_relationships/scope_registry.json"),
        help="Versioned exclusion and scope registry",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("config/context_relationships/schema.json"),
        help="Versioned relationship schema that must match the compiler contract",
    )
    parser.add_argument("--output", type=Path, help="Directory for canonical index artifacts")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate and summarize only; do not write artifacts",
    )
    args = parser.parse_args(argv)
    if not args.validate and args.output is None:
        parser.error("--output is required unless --validate is used")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        seed = load_json(args.input, "input seed")
        if not args.scope_registry.exists():
            raise CompilationError(f"scope registry does not exist: {args.scope_registry}")
        if not args.schema.exists():
            raise CompilationError(f"relationship schema does not exist: {args.schema}")
        nodes, edges, matrix, manifest = compile_seed(seed, args.scope_registry, args.schema)
        if not args.validate:
            write_artifacts(args.output, nodes, edges, matrix, manifest, args.input)
        summary = dict(manifest)
        summary["input_sha256"] = digest_file(args.input)
        summary["mode"] = "validate" if args.validate else "compile"
        summary["output"] = None if args.validate else str(args.output)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except CompilationError as exc:
        print(f"context relationship compilation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
