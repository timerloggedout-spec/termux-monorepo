#!/usr/bin/env python3
"""Validate classifier candidate identities and versioned graph topology offline.

The validator checks registry structure, catalog references, local source paths,
role compatibility, and graph acyclicity. It does not execute classifiers or
establish candidate quality.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _unique(values: list[Any]) -> bool:
    try:
        return len(values) == len(set(values))
    except TypeError:
        return False


def validate_registry(root: Path, registry: Any, catalog: Any, estate: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(registry, dict):
        return ["registry: expected JSON object"]
    if registry.get("schema_version") != "classifier.graph-registry.v1":
        errors.append("registry.schema_version: expected classifier.graph-registry.v1")
    for field in ("registry_id", "registry_version"):
        if not isinstance(registry.get(field), str) or not registry[field].strip():
            errors.append(f"registry.{field}: expected non-empty string")

    estate_ref = registry.get("classifier_estate")
    if not isinstance(estate_ref, dict):
        errors.append("registry.classifier_estate: expected snapshot reference")
    elif not isinstance(estate, dict) or estate.get("schema") != estate_ref.get("schema"):
        errors.append("classifier estate: snapshot schema mismatch")
    else:
        units = estate.get("units")
        headlines = estate.get("headlines")
        expected_states = estate_ref.get("states", {})
        if not isinstance(units, list):
            errors.append("classifier estate.units: expected list")
        else:
            unit_ids = [unit.get("id") for unit in units if isinstance(unit, dict)]
            if len(unit_ids) != len(units) or not _unique(unit_ids):
                errors.append("classifier estate.units: missing or duplicate unit IDs")
            if len(units) != estate_ref.get("unit_count"):
                errors.append("classifier estate.unit_count: snapshot count mismatch")
            actual_states = {
                state: sum(1 for unit in units if isinstance(unit, dict) and unit.get("state") == state)
                for state in ("live", "dormant", "dead")
            }
            if actual_states != expected_states:
                errors.append(f"classifier estate.states: expected {expected_states}, observed {actual_states}")
            if isinstance(headlines, dict):
                for state, count in actual_states.items():
                    if headlines.get(state) != count:
                        errors.append(f"classifier estate.headlines.{state}: mismatch with unit rows")
        if estate.get("generated_at") != estate_ref.get("snapshot_date"):
            errors.append("classifier estate.snapshot_date: generated_at mismatch")

    cohort = registry.get("canonical_cohort")
    if not isinstance(cohort, dict) or cohort.get("schema") != "manager.tournament.v1":
        errors.append("registry.canonical_cohort: manager.tournament.v1 is required")
    elif cohort.get("contract_path") != "docs/ops/MANAGER-TOURNAMENT.schema.json":
        errors.append("registry.canonical_cohort.contract_path: expected canonical manager cohort schema")

    if not isinstance(catalog, dict) or catalog.get("schema") != "system-one-catalog/1":
        errors.append("catalog: expected system-one-catalog/1")
        catalog_ids: set[str] = set()
    else:
        entries = catalog.get("entries")
        if not isinstance(entries, list):
            errors.append("catalog.entries: expected list")
            catalog_ids = set()
        else:
            catalog_ids = {
                entry.get("id") for entry in entries
                if isinstance(entry, dict) and isinstance(entry.get("id"), str)
            }
            if len(catalog_ids) != len(entries):
                errors.append("catalog.entries: missing or duplicate catalog IDs")

    roles = registry.get("roles")
    if not isinstance(roles, list) or not roles:
        errors.append("registry.roles: expected non-empty list")
        role_ids: set[str] = set()
    else:
        role_values = [r.get("role_id") for r in roles if isinstance(r, dict)]
        if len(role_values) != len(roles) or any(not isinstance(x, str) or not x for x in role_values):
            errors.append("registry.roles: each role requires role_id")
        if not _unique(role_values):
            errors.append("registry.roles: duplicate role_id")
        role_ids = set(role_values)

    candidates = registry.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        errors.append("registry.candidates: expected non-empty list")
        candidate_by_id: dict[str, dict] = {}
    else:
        candidate_by_id = {}
        for index, candidate in enumerate(candidates):
            prefix = f"registry.candidates[{index}]"
            if not isinstance(candidate, dict):
                errors.append(f"{prefix}: expected object")
                continue
            candidate_id = candidate.get("candidate_id")
            if not isinstance(candidate_id, str) or not candidate_id:
                errors.append(f"{prefix}.candidate_id: expected non-empty string")
                continue
            if candidate_id in candidate_by_id:
                errors.append(f"{prefix}.candidate_id: duplicate candidate ID {candidate_id}")
                continue
            candidate_by_id[candidate_id] = candidate
            candidate_roles = candidate.get("roles")
            if not isinstance(candidate_roles, list) or not candidate_roles:
                errors.append(f"{prefix}.roles: expected non-empty list")
            else:
                for role_id in candidate_roles:
                    if not isinstance(role_id, str) or role_id not in role_ids:
                        errors.append(f"{prefix}.roles: unknown role {role_id!r}")
            kind = candidate.get("kind")
            if kind == "catalog":
                catalog_id = candidate.get("catalog_entry_id")
                if catalog_id not in catalog_ids:
                    errors.append(f"{prefix}.catalog_entry_id: unknown catalog entry {catalog_id!r}")
            elif kind == "local":
                source_ref = candidate.get("source_ref")
                if not isinstance(source_ref, str) or not source_ref:
                    errors.append(f"{prefix}.source_ref: expected repository path")
                elif not (root / source_ref).is_file():
                    errors.append(f"{prefix}.source_ref: local source file is missing: {source_ref}")
            else:
                errors.append(f"{prefix}.kind: expected local or catalog")

    graphs = registry.get("graphs")
    if not isinstance(graphs, list) or not graphs:
        errors.append("registry.graphs: expected non-empty list")
    else:
        graph_ids: list[str] = []
        for graph_index, graph in enumerate(graphs):
            prefix = f"registry.graphs[{graph_index}]"
            if not isinstance(graph, dict):
                errors.append(f"{prefix}: expected object")
                continue
            graph_id = graph.get("graph_id")
            if not isinstance(graph_id, str) or not graph_id:
                errors.append(f"{prefix}.graph_id: expected non-empty string")
            else:
                graph_ids.append(graph_id)
            nodes = graph.get("nodes")
            if not isinstance(nodes, list) or not nodes:
                errors.append(f"{prefix}.nodes: expected non-empty list")
                continue
            node_by_id: dict[str, dict] = {}
            for node_index, node in enumerate(nodes):
                node_prefix = f"{prefix}.nodes[{node_index}]"
                if not isinstance(node, dict):
                    errors.append(f"{node_prefix}: expected object")
                    continue
                node_id = node.get("node_id")
                if not isinstance(node_id, str) or not node_id:
                    errors.append(f"{node_prefix}.node_id: expected non-empty string")
                    continue
                if node_id in node_by_id:
                    errors.append(f"{node_prefix}.node_id: duplicate node ID {node_id}")
                    continue
                node_by_id[node_id] = node
                role_id = node.get("role_id")
                if not isinstance(role_id, str) or role_id not in role_ids:
                    errors.append(f"{node_prefix}.role_id: unknown role {role_id!r}")
                candidate_id = node.get("candidate_id")
                if candidate_id is not None:
                    candidate = candidate_by_id.get(candidate_id) if isinstance(candidate_id, str) else None
                    if candidate is None:
                        errors.append(f"{node_prefix}.candidate_id: unknown candidate {candidate_id!r}")
                    elif role_id not in candidate.get("roles", []):
                        errors.append(f"{node_prefix}: candidate {candidate_id!r} does not implement role {role_id!r}")
            for node_id, node in node_by_id.items():
                dependencies = node.get("depends_on")
                if not isinstance(dependencies, list):
                    errors.append(f"{prefix}.nodes[{node_id}].depends_on: expected list")
                    continue
                if not _unique(dependencies):
                    errors.append(f"{prefix}.nodes[{node_id}].depends_on: duplicate dependency")
                for dependency in dependencies:
                    if not isinstance(dependency, str) or dependency not in node_by_id:
                        errors.append(f"{prefix}.nodes[{node_id}].depends_on: unknown node {dependency!r}")
            # Kahn's algorithm: reject cycles while preserving the declared DAG.
            indegree = {node_id: 0 for node_id in node_by_id}
            children = {node_id: [] for node_id in node_by_id}
            for node_id, node in node_by_id.items():
                for dependency in node.get("depends_on", []):
                    if isinstance(dependency, str) and dependency in node_by_id:
                        indegree[node_id] += 1
                        children[dependency].append(node_id)
            ready = [node_id for node_id, degree in indegree.items() if degree == 0]
            visited = 0
            while ready:
                current = ready.pop()
                visited += 1
                for child in children[current]:
                    indegree[child] -= 1
                    if indegree[child] == 0:
                        ready.append(child)
            if visited != len(node_by_id):
                errors.append(f"{prefix}: dependency cycle detected")
        if not _unique(graph_ids):
            errors.append("registry.graphs: duplicate graph_id")

    evaluation = registry.get("evaluation")
    if not isinstance(evaluation, dict):
        errors.append("registry.evaluation: expected object")
    else:
        for field in ("evaluator_id", "evaluator_version"):
            if not isinstance(evaluation.get(field), str) or not evaluation[field].strip():
                errors.append(f"registry.evaluation.{field}: expected non-empty string")
        for field in ("hard_gates", "objectives"):
            values = evaluation.get(field)
            if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v for v in values):
                errors.append(f"registry.evaluation.{field}: expected non-empty string list")
        if not isinstance(evaluation.get("held_out_required"), bool):
            errors.append("registry.evaluation.held_out_required: expected boolean")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--registry", type=Path, default=Path("config/classifier_graph_registry.json"))
    args = parser.parse_args()
    root = args.root.resolve()
    registry_path = args.registry if args.registry.is_absolute() else root / args.registry
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        catalog_path = root / registry["catalog"]["path"]
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        estate_path = root / registry["classifier_estate"]["path"]
        estate = json.loads(estate_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2
    errors = validate_registry(root, registry, catalog, estate)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: {registry['registry_id']}@{registry['registry_version']} — "
        f"{len(registry['candidates'])} candidates, {len(registry['graphs'])} graphs, "
        f"{len(estate['units'])} classifier-estate units, {len(catalog['entries'])} catalog entries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
