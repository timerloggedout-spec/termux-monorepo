#!/usr/bin/env python3
"""Build and atomically publish the canonical context-relationship index."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    from .compiler import CompilationError, compile_seed, write_artifacts
    from .github_collector import (
        GitHubClient,
        collect_github_seed,
        load_checkpoint,
        write_checkpoint,
    )
    from .seed_merger import merge_seeds
    from .source_collector import collect_source_seed
except ImportError:  # Supports direct script use.
    from compiler import CompilationError, compile_seed, write_artifacts
    from github_collector import (
        GitHubClient,
        collect_github_seed,
        load_checkpoint,
        write_checkpoint,
    )
    from seed_merger import merge_seeds
    from source_collector import collect_source_seed

BUILDER_ID = "archwiz.context_relationships.build_index@1.0"


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def replace_artifacts(staging_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for artifact in sorted(staging_dir.iterdir(), key=lambda path: path.name):
        if artifact.is_file():
            os.replace(artifact, output_dir / artifact.name)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CompilationError(f"canonical artifact {path}:{line_number} is invalid JSON") from exc
        if not isinstance(value, dict):
            raise CompilationError(f"canonical artifact {path}:{line_number} must be an object")
        records.append(value)
    return records


def load_canonical_history(output: Path, owner: str, repo: str, ref: str) -> dict[str, Any] | None:
    """Rehydrate prior canonical records as compiler-valid seed data for retention."""
    manifest_path = output / "manifest.json"
    nodes_path = output / "nodes.jsonl"
    edges_path = output / "edges.jsonl"
    if not (manifest_path.exists() and nodes_path.exists() and edges_path.exists()):
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CompilationError(f"canonical manifest {manifest_path} is invalid JSON") from exc
    if not isinstance(manifest, dict):
        raise CompilationError("canonical manifest must be an object")
    if manifest.get("schema_version") != "1.0":
        raise CompilationError("canonical history schema version is not supported")
    if manifest.get("repository") != f"{owner}/{repo}" or manifest.get("default_branch") != ref:
        raise CompilationError("canonical history belongs to a different repository or ref")
    canonical_nodes = read_jsonl(nodes_path)
    canonical_edges = read_jsonl(edges_path)
    node_refs: dict[str, str] = {}
    raw_nodes: list[dict[str, Any]] = []
    for record in canonical_nodes:
        node_id, kind, external_id = record.get("id"), record.get("kind"), record.get("external_id")
        if not all(isinstance(value, str) for value in (node_id, kind, external_id)):
            raise CompilationError("canonical history node is missing stable identity fields")
        attributes = record.get("attributes", {})
        if not isinstance(attributes, dict):
            raise CompilationError(f"canonical history node {node_id} attributes must be an object")
        raw_node: dict[str, Any] = {"kind": kind, "external_id": external_id, "attributes": attributes}
        for field in ("url", "observed_at"):
            if isinstance(record.get(field), str):
                raw_node[field] = record[field]
        node_refs[node_id] = f"{kind}:{external_id}"
        raw_nodes.append(raw_node)
    raw_edges: list[dict[str, Any]] = []
    for record in canonical_edges:
        source_id, target_id = record.get("source"), record.get("target")
        if not isinstance(source_id, str) or not isinstance(target_id, str):
            raise CompilationError("canonical history edge is missing source or target identity")
        if source_id not in node_refs or target_id not in node_refs:
            raise CompilationError("canonical history edge references an unknown node")
        required = ("type", "classification", "observed_at", "evidence")
        if any(field not in record for field in required):
            raise CompilationError("canonical history edge is missing required relationship fields")
        raw_edge = {
            "type": record["type"],
            "source": node_refs[source_id],
            "target": node_refs[target_id],
            "classification": record["classification"],
            "score": record.get("score"),
            "observed_at": record["observed_at"],
            "evidence": record["evidence"],
            "attributes": record.get("attributes", {}),
        }
        raw_edges.append(raw_edge)
    return {
        "schema_version": "1.0",
        "repository": {"owner": owner, "name": repo, "default_branch": ref},
        "nodes": raw_nodes,
        "edges": raw_edges,
    }


def build_index(
    root: Path,
    owner: str,
    repo: str,
    ref: str,
    token: str,
    scope_registry: Path,
    schema: Path,
    output: Path,
    max_items: int,
    max_commits: int,
    max_comments_per_item: int,
    max_cochange_pairs_per_commit: int,
    include_comments: bool,
    max_retries: int,
    full_refresh: bool = False,
) -> dict[str, Any]:
    """Build a complete index, replacing canonical artifacts only after validation."""
    checkpoint_path = output / "checkpoint.json"
    since = None if full_refresh else load_checkpoint(checkpoint_path)
    historical_seed = load_canonical_history(output, owner, repo, ref)
    bootstrap_backfill = historical_seed is None
    collection_max_items = max(max_items, 100) if bootstrap_backfill else max_items
    collection_max_commits = max(max_commits, 100) if bootstrap_backfill else max_commits
    source_seed, source_report = collect_source_seed(root, owner, repo, ref, scope_registry)
    client = GitHubClient(token, max_retries=max_retries)
    github_seed, github_report = collect_github_seed(
        client,
        owner,
        repo,
        ref,
        scope_registry,
        since=since,
        max_items=collection_max_items,
        max_commits=collection_max_commits,
        max_comments_per_item=max_comments_per_item,
        include_comments=include_comments,
        max_cochange_pairs_per_commit=max_cochange_pairs_per_commit,
    )
    github_report["retry_count"] = client.retry_count
    seeds = [seed for seed in (historical_seed, source_seed, github_seed) if seed is not None]
    merged_seed, merge_report = merge_seeds(*seeds)
    merge_report["retained_history"] = historical_seed is not None
    nodes, edges, matrix, manifest = compile_seed(merged_seed, scope_registry, schema)
    manifest.update(
        {
            "builder": BUILDER_ID,
            "source_report": source_report,
            "github_report": github_report,
            "merge_report": merge_report,
            "incremental_since": since,
            "retained_history": historical_seed is not None,
            "bootstrap_backfill": bootstrap_backfill,
        }
    )

    output_parent = output.parent.resolve()
    output_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".context-relationships-", dir=output_parent) as temporary:
        staging_dir = Path(temporary)
        seed_path = staging_dir / "merged-seed.json"
        write_json(seed_path, merged_seed)
        write_artifacts(staging_dir, nodes, edges, matrix, manifest, seed_path)
        seed_path.unlink()
        write_json(staging_dir / "source-report.json", source_report)
        write_json(staging_dir / "github-report.json", github_report)
        write_json(staging_dir / "merge-report.json", merge_report)
        write_checkpoint(staging_dir / "checkpoint.json", github_report["collected_at"], owner, repo, ref)
        summary = {
            "builder": BUILDER_ID,
            "repository": f"{owner}/{repo}",
            "ref": ref,
            "node_count": manifest["node_count"],
            "edge_count": manifest["edge_count"],
            "verified_edge_count": manifest["verified_edge_count"],
            "candidate_edge_count": manifest["candidate_edge_count"],
            "incremental_since": since,
            "retained_history": historical_seed is not None,
            "bootstrap_backfill": bootstrap_backfill,
            "github_requests": github_report["request_count"],
            "github_retries": github_report["retry_count"],
            "parser_failures": len(source_report["parser_failures"]),
            "excluded_history_paths": github_report["counts"].get("excluded_history_paths", 0),
        }
        write_json(staging_dir / "build-summary.json", summary)
        replace_artifacts(staging_dir, output)
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--scope-registry", type=Path, default=Path("config/context_relationships/scope_registry.json"))
    parser.add_argument("--schema", type=Path, default=Path("config/context_relationships/schema.json"))
    parser.add_argument("--output", type=Path, default=Path("workspace/llm_map/context_relationships"))
    parser.add_argument("--max-items", type=int, default=20)
    parser.add_argument("--max-commits", type=int, default=25)
    parser.add_argument("--max-comments-per-item", type=int, default=20)
    parser.add_argument("--max-cochange-pairs-per-commit", type=int, default=100)
    parser.add_argument("--without-comments", action="store_true")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--full-refresh", action="store_true", help="Ignore the existing checkpoint for a bounded reconciliation run")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    token = os.environ.get(args.token_env)
    if not token:
        print(f"context relationship build failed: missing token in {args.token_env}", file=sys.stderr)
        return 2
    try:
        if any(
            value < 1
            for value in (
                args.max_items,
                args.max_commits,
                args.max_comments_per_item,
                args.max_cochange_pairs_per_commit,
            )
        ) or args.max_retries < 0:
            raise CompilationError("collection limits must be positive and max retries must be zero or greater")
        summary = build_index(
            args.root,
            args.owner,
            args.repo,
            args.ref,
            token,
            args.scope_registry,
            args.schema,
            args.output,
            args.max_items,
            args.max_commits,
            args.max_comments_per_item,
            args.max_cochange_pairs_per_commit,
            not args.without_comments,
            args.max_retries,
            args.full_refresh,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except CompilationError as exc:
        print(f"context relationship build failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
