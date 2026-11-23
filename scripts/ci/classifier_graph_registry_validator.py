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


def validate_registry(root: Path, registry: Any, catalog: Any, estate: Any, plan: Any) -> list[str]:
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
            actual_groups: dict[str, dict[str, int]] = {}
            for unit in units:
                if not isinstance(unit, dict) or not isinstance(unit.get("group_name"), str):
                    continue
                name = unit["group_name"]
                actual_groups.setdefault(name, {"units": 0, "live": 0, "dormant": 0, "dead": 0})
                actual_groups[name]["units"] += 1
                state = unit.get("state")
                if state in {"live", "dormant", "dead"}:
                    actual_groups[name][state] += 1
            group_rows = estate_ref.get("groups", [])
            group_names = [item.get("group_name") for item in group_rows if isinstance(item, dict)]
            if not isinstance(group_rows, list) or len(group_names) != len(group_rows) or not _unique(group_names):
                errors.append("classifier estate.groups: require unique group names")
            expected_groups = {
                item.get("group_name"): {key: item.get(key) for key in ("units", "live", "dormant", "dead")}
                for item in group_rows if isinstance(item, dict)
            }
            if actual_groups != expected_groups:
                errors.append("classifier estate.groups: group counts mismatch with source rows")
        if estate.get("generated_at") != estate_ref.get("snapshot_date"):
            errors.append("classifier estate.snapshot_date: generated_at mismatch")

    if not isinstance(plan, dict) or plan.get("schema") != "classifier.tournament-experiment-plan.v1":
        errors.append("experiment plan: expected classifier.tournament-experiment-plan.v1")
    else:
        plan_cohort = plan.get("canonical_cohort")
        if not isinstance(plan_cohort, dict) or plan_cohort.get("schema") != "manager.tournament.v1":
            errors.append("experiment plan: canonical cohort must be manager.tournament.v1")
        if plan.get("execution_ready") is not False or plan.get("status") != "design_only":
            errors.append("experiment plan: execution remains design_only until qualification gates pass")
        phases = plan.get("phases", [])
        phase_ids = [phase.get("phase_id") for phase in phases if isinstance(phase, dict)]
        if len(phase_ids) != len(phases) or not _unique(phase_ids) or len(phases) < 5:
            errors.append("experiment plan.phases: require five uniquely identified phases")
        expected_units = {"classifier_capability", "routing_policy", "composition_graph", "tournament_implementation"}
        comparison_units = plan.get("comparison_units")
        if not isinstance(comparison_units, list) or set(comparison_units) != expected_units:
            errors.append("experiment plan.comparison_units: all four comparison units are required")
        analysis = plan.get("analysis", {})
        if not isinstance(analysis, dict) or analysis.get("missing_observation") != "null" or analysis.get("raw_objectives_preserved") is not True:
            errors.append("experiment plan.analysis: preserve null observations and raw objective vectors")
        if not isinstance(plan.get("allocation"), dict) or plan["allocation"].get("resource_budget_required") is not True:
            errors.append("experiment plan.allocation: explicit resource budget required")
        if not isinstance(plan.get("stopping"), dict) or plan["stopping"].get("promotion_requires_human_approval") is not True:
            errors.append("experiment plan.stopping: production promotion requires human approval")

    cohort = registry.get("canonical_cohort")
    if not isinstance(cohort, dict) or cohort.get("schema") != "manager.tournament.v1":
        errors.append("registry.canonical_cohort: manager.tournament.v1 is required")
    elif cohort.get("contract_path") != "docs/ops/MANAGER-TOURNAMENT.schema.json":
        errors.append("registry.canonical_cohort.contract_path: expected canonical manager cohort schema")

    if not isinstance(catalog, dict) or catalog.get("schema") != "system-one-catalog/1":
        errors.append("catalog: expected system-one-catalog/1")
        catalog_ids: set[str] = set()
        catalog_by_id: dict[str, dict] = {}
    else:
        entries = catalog.get("entries")
        if not isinstance(entries, list):
            errors.append("catalog.entries: expected list")
            catalog_ids = set()
            catalog_by_id = {}
        else:
            catalog_by_id = {
                entry.get("id"): entry for entry in entries
                if isinstance(entry, dict) and isinstance(entry.get("id"), str)
            }
            catalog_ids = set(catalog_by_id)
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
        role_ids = {value for value in role_values if isinstance(value, str) and value}

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
            qualification_state = candidate.get("qualification_state")
            if qualification_state not in {"role_mapped", "role_mapped_unverified", "unclassified"}:
                errors.append(f"{prefix}.qualification_state: unknown or missing state {qualification_state!r}")
            elif qualification_state == "unclassified" and candidate_roles != ["unclassified"]:
                errors.append(f"{prefix}.qualification_state: unclassified candidates must use only the unclassified role")
            elif qualification_state != "unclassified" and candidate_roles == ["unclassified"]:
                errors.append(f"{prefix}.qualification_state: mapped candidates require an explicit role")
            operational_state = candidate.get("operational_state")
            allowed_states = {
                "dispatch_only_baseline", "blocked_paid_owner_gate",
                "trial_candidate_composition_required", "evaluated_self_hosted",
                "referenced_not_runnable", "trial_candidate_host_blocked",
                "catalogued_unverified", "trial_candidate_unverified", "evaluated_recorded",
            }
            if not isinstance(operational_state, str) or operational_state not in allowed_states:
                errors.append(f"{prefix}.operational_state: unknown or missing state {operational_state!r}")
            kind = candidate.get("kind")
            if kind == "catalog":
                catalog_id = candidate.get("catalog_entry_id")
                if catalog_id not in catalog_ids:
                    errors.append(f"{prefix}.catalog_entry_id: unknown catalog entry {catalog_id!r}")
                elif catalog_by_id[catalog_id].get("layer") != "model":
                    errors.append(f"{prefix}.catalog_entry_id: model candidate must reference a model-layer catalog entry")
                else:
                    source_entry = catalog_by_id[catalog_id]
                    if candidate.get("catalog_claim") != source_entry.get("note"):
                        errors.append(f"{prefix}.catalog_claim: claim must match catalog source text")
                    if candidate.get("catalog_source_url") != source_entry.get("source_url"):
                        errors.append(f"{prefix}.catalog_source_url: source URL must match catalog entry")
            elif kind == "local":
                source_ref = candidate.get("source_ref")
                if not isinstance(source_ref, str) or not source_ref:
                    errors.append(f"{prefix}.source_ref: expected repository path")
                elif not (root / source_ref).is_file():
                    errors.append(f"{prefix}.source_ref: local source file is missing: {source_ref}")
            else:
                errors.append(f"{prefix}.kind: expected local or catalog")

    if isinstance(catalog, dict) and isinstance(catalog.get("entries"), list):
        expected_model_ids = {
            entry.get("id") for entry in catalog["entries"]
            if isinstance(entry, dict) and entry.get("layer") == "model"
        }
        actual_model_ids = {
            candidate.get("catalog_entry_id") for candidate in candidate_by_id.values()
            if candidate.get("kind") == "catalog"
        }
        if actual_model_ids != expected_model_ids:
            errors.append(
                f"registry.candidates: model catalog coverage mismatch "
                f"(missing={sorted(expected_model_ids - actual_model_ids)}, "
                f"extra={sorted(actual_model_ids - expected_model_ids)})"
            )

    infrastructure = registry.get("infrastructure")
    expected_infrastructure_ids = {
        entry.get("id") for entry in catalog_by_id.values()
        if entry.get("layer") in {"adapter", "runtime", "directory"}
    }
    actual_infrastructure_ids: set[str] = set()
    if not isinstance(infrastructure, list):
        errors.append("registry.infrastructure: expected list")
    else:
        for index, item in enumerate(infrastructure):
            prefix = f"registry.infrastructure[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix}: expected object")
                continue
            catalog_id = item.get("catalog_entry_id")
            if not isinstance(catalog_id, str) or catalog_id not in catalog_by_id:
                errors.append(f"{prefix}.catalog_entry_id: unknown catalog entry {catalog_id!r}")
                continue
            if catalog_id in actual_infrastructure_ids:
                errors.append(f"{prefix}.catalog_entry_id: duplicate infrastructure entry {catalog_id!r}")
            actual_infrastructure_ids.add(catalog_id)
            expected_layer = catalog_by_id[catalog_id].get("layer")
            if expected_layer == "model" or item.get("layer") != expected_layer:
                errors.append(f"{prefix}.layer: catalog layer mismatch for {catalog_id!r}")
            if item.get("operational_state") != "infrastructure_reference":
                errors.append(f"{prefix}.operational_state: expected infrastructure_reference")
        if actual_infrastructure_ids != expected_infrastructure_ids:
            errors.append(
                f"registry.infrastructure: layer coverage mismatch "
                f"(missing={sorted(expected_infrastructure_ids - actual_infrastructure_ids)}, "
                f"extra={sorted(actual_infrastructure_ids - expected_infrastructure_ids)})"
            )

    implementation = registry.get("implementation_competition")
    if not isinstance(implementation, dict) or implementation.get("schema") != "tournament.implementation-competition.v1":
        errors.append("registry.implementation_competition: expected tournament.implementation-competition.v1")
    else:
        if implementation.get("canonical_cohort") != "manager.tournament.v1":
            errors.append("registry.implementation_competition.canonical_cohort: expected manager.tournament.v1")
        comparator = implementation.get("comparison_engine", {})
        comparator_source = comparator.get("source_ref") if isinstance(comparator, dict) else None
        if not isinstance(comparator_source, str) or not (root / comparator_source).is_file():
            errors.append(f"registry.implementation_competition.comparison_engine: missing source {comparator_source!r}")
        comparator_cli = comparator.get("cli_source_ref") if isinstance(comparator, dict) else None
        if not isinstance(comparator_cli, str) or not (root / comparator_cli).is_file():
            errors.append(f"registry.implementation_competition.comparison_engine: missing CLI source {comparator_cli!r}")
        receipt_schema = comparator.get("receipt_schema_ref") if isinstance(comparator, dict) else None
        if not isinstance(receipt_schema, str) or not (root / receipt_schema).is_file():
            errors.append(f"registry.implementation_competition.comparison_engine: missing receipt schema {receipt_schema!r}")
        incumbent = implementation.get("incumbent", {})
        components = incumbent.get("components", []) if isinstance(incumbent, dict) else []
        if not components:
            errors.append("registry.implementation_competition.incumbent.components: expected non-empty list")
        for component in components:
            source_ref = component.get("source_ref") if isinstance(component, dict) else None
            if not isinstance(source_ref, str) or not (root / source_ref).is_file():
                errors.append(f"registry.implementation_competition.incumbent: missing component source {source_ref!r}")
        challengers = implementation.get("challengers", [])
        if not isinstance(challengers, list) or not challengers:
            errors.append("registry.implementation_competition.challengers: expected non-empty list")
        else:
            for challenger in challengers:
                source_ref = challenger.get("source_ref") if isinstance(challenger, dict) else None
                if not isinstance(source_ref, str) or not (root / source_ref).is_file():
                    errors.append(f"registry.implementation_competition.challengers: missing source {source_ref!r}")
        protocol = implementation.get("protocol", {})
        for gate in ("matched_cohort_required", "held_out_required", "independent_evaluator_required",
                     "immutable_receipts_required", "rollback_target_required", "owner_approval_for_production"):
            if not isinstance(protocol, dict) or protocol.get(gate) is not True:
                errors.append(f"registry.implementation_competition.protocol.{gate}: must be true")

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
                dependencies = node.get("depends_on", [])
                if not isinstance(dependencies, list):
                    continue
                for dependency in dependencies:
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
        plan_path = root / "config/classifier_tournament_experiment_plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2
    errors = validate_registry(root, registry, catalog, estate, plan)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: {registry['registry_id']}@{registry['registry_version']} — "
        f"{len(registry['candidates'])} candidates, {len(registry['infrastructure'])} infrastructure refs, "
        f"{len(registry['graphs'])} graphs, {len(estate['units'])} classifier-estate units, "
        f"{len(catalog['entries'])} catalog entries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
