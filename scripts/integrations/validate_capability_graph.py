#!/usr/bin/env python3
"""Validate the CEEL capability opportunity graph without third-party dependencies."""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH = ROOT / "docs/integrations/capability-opportunity-graph.json"
NODE_STATES = {"discovered", "classified", "mapped", "proposed", "admitted", "experimentally_validated", "integration_candidate", "integrated", "monitored", "rejected", "deferred", "blocked", "superseded", "retired"}
NODE_KINDS = {"external_platform", "foss_project", "internal_component", "experiment_family", "capability"}
SOURCE_TYPES = {"official_documentation", "source_repository", "repository_file", "github_issue", "github_workflow", "research_paper", "operator_request", "runtime_observation"}
RELATIONSHIPS = {"competes_with", "complements", "measures", "consumes", "implements", "informs", "supersedes", "depends_on"}
EVIDENCE_STATES = {"unverified", "partial", "verified", "refuted", "stale"}
CAPABILITY_STATES = {"hypothesis", "documented", "observed", "tested", "verified", "not_supported", "unknown"}
EDGE_STATES = {"hypothesis", "documented", "observed", "tested", "verified"}


def _member(value: Any, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


def validate_graph(graph: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(graph, dict):
        return ["graph root must be an object"]
    required = {"schema_version", "graph_id", "repository", "updated_at", "authority", "nodes", "edges"}
    missing = sorted(required - graph.keys())
    if missing:
        return [f"graph missing required fields: {', '.join(missing)}"]
    if graph["schema_version"] != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if graph["authority"] != "repository-maintained-capability-index":
        errors.append("authority must identify repository-maintained index")
    if not isinstance(graph["graph_id"], str) or not graph["graph_id"].strip():
        errors.append("graph_id must be a non-empty string")
    if not isinstance(graph["repository"], str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", graph["repository"]):
        errors.append("repository must be owner/name")
    try:
        if not isinstance(graph["updated_at"], str):
            raise TypeError
        date.fromisoformat(graph["updated_at"])
    except (TypeError, ValueError):
        errors.append("updated_at must be an ISO date")
    if not isinstance(graph["nodes"], list) or not isinstance(graph["edges"], list):
        return errors + ["nodes and edges must be arrays"]

    ids: list[str] = []
    for i, node in enumerate(graph["nodes"]):
        p = f"nodes[{i}]"
        if not isinstance(node, dict):
            errors.append(f"{p} must be an object")
            continue
        for field in ("id", "kind", "name", "lifecycle_state", "source", "capabilities", "evidence", "owner"):
            if field not in node:
                errors.append(f"{p} missing {field}")
        node_id = node.get("id")
        if not isinstance(node_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,95}", node_id):
            errors.append(f"{p}.id must be a valid stable identifier")
        else:
            ids.append(node_id)
        if not _member(node.get("kind"), NODE_KINDS):
            errors.append(f"{p}.kind is unsupported")
        if not _member(node.get("lifecycle_state"), NODE_STATES):
            errors.append(f"{p}.lifecycle_state is unsupported")
        if not isinstance(node.get("name"), str) or not node["name"].strip():
            errors.append(f"{p}.name must be non-empty")
        if not isinstance(node.get("owner"), str) or not node["owner"].strip():
            errors.append(f"{p}.owner must be non-empty")

        source = node.get("source")
        if not isinstance(source, dict):
            errors.append(f"{p}.source must be an object")
        else:
            for field in ("source_type", "locator", "revision", "observed_at"):
                if field not in source:
                    errors.append(f"{p}.source missing {field}")
            if not _member(source.get("source_type"), SOURCE_TYPES):
                errors.append(f"{p}.source.source_type is unsupported")
            for field in ("locator", "revision"):
                if source.get(field) is not None and not isinstance(source.get(field), str):
                    errors.append(f"{p}.source.{field} must be string or null")
            try:
                observed = source.get("observed_at")
                if not isinstance(observed, str):
                    raise ValueError
                datetime.fromisoformat(observed.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{p}.source.observed_at must be an ISO timestamp")

        capabilities = node.get("capabilities")
        if not isinstance(capabilities, list):
            errors.append(f"{p}.capabilities must be an array")
        else:
            for ci, capability in enumerate(capabilities):
                cp = f"{p}.capabilities[{ci}]"
                if not isinstance(capability, dict):
                    errors.append(f"{cp} must be an object")
                    continue
                if not isinstance(capability.get("capability_id"), str) or not capability["capability_id"].strip():
                    errors.append(f"{cp}.capability_id must be non-empty")
                if not _member(capability.get("status"), CAPABILITY_STATES):
                    errors.append(f"{cp}.status is unsupported")
                refs = capability.get("evidence_refs", [])
                if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
                    errors.append(f"{cp}.evidence_refs must be an array of strings")

        evidence_items = node.get("evidence")
        if not isinstance(evidence_items, list):
            errors.append(f"{p}.evidence must be an array")
        else:
            for ei, evidence in enumerate(evidence_items):
                ep = f"{p}.evidence[{ei}]"
                if not isinstance(evidence, dict):
                    errors.append(f"{ep} must be an object")
                    continue
                if not isinstance(evidence.get("evidence_id"), str) or not evidence["evidence_id"].strip():
                    errors.append(f"{ep}.evidence_id must be non-empty")
                if not _member(evidence.get("status"), EVIDENCE_STATES):
                    errors.append(f"{ep}.status is unsupported")
                if evidence.get("reference") is not None and not isinstance(evidence.get("reference"), str):
                    errors.append(f"{ep}.reference must be string or null")
                if "notes" in evidence and not isinstance(evidence["notes"], str):
                    errors.append(f"{ep}.notes must be a string")
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        errors.append(f"duplicate node IDs: {', '.join(duplicates)}")

    known = set(ids)
    seen: set[tuple[str, str, str]] = set()
    for i, edge in enumerate(graph["edges"]):
        p = f"edges[{i}]"
        if not isinstance(edge, dict):
            errors.append(f"{p} must be an object")
            continue
        source, target, relation = edge.get("from"), edge.get("to"), edge.get("relationship")
        if not isinstance(source, str) or source not in known:
            errors.append(f"{p}.from references unknown node: {source}")
        if not isinstance(target, str) or target not in known:
            errors.append(f"{p}.to references unknown node: {target}")
        if not _member(relation, RELATIONSHIPS):
            errors.append(f"{p}.relationship is unsupported")
        if not _member(edge.get("status"), EDGE_STATES):
            errors.append(f"{p}.status is unsupported")
        if isinstance(source, str) and isinstance(target, str) and isinstance(relation, str):
            identity = (source, target, relation)
            if identity in seen:
                errors.append(f"duplicate edge: {identity}")
            seen.add(identity)
    return errors


def main() -> int:
    path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_GRAPH
    try:
        graph = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read graph: {exc}", file=sys.stderr)
        return 2
    errors = validate_graph(graph)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"OK: {len(graph['nodes'])} capability nodes; {len(graph['edges'])} relationships; references resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
