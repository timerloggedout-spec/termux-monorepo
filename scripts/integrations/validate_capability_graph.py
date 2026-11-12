#!/usr/bin/env python3
"""Validate the CEEL capability opportunity graph without third-party dependencies."""
from __future__ import annotations
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH = ROOT / "docs/integrations/capability-opportunity-graph.json"
NODE_STATES = {"discovered", "classified", "mapped", "proposed", "admitted", "experimentally_validated", "integration_candidate", "integrated", "monitored", "rejected", "deferred", "blocked", "superseded", "retired"}
NODE_KINDS = {"external_platform", "foss_project", "internal_component", "experiment_family", "capability"}
RELATIONSHIPS = {"competes_with", "complements", "measures", "consumes", "implements", "informs", "supersedes", "depends_on"}
EVIDENCE_STATES = {"unverified", "partial", "verified", "refuted", "stale"}
CAPABILITY_STATES = {"hypothesis", "documented", "observed", "tested", "verified", "not_supported", "unknown"}


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
    try:
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
        if not isinstance(node.get("id"), str) or not node["id"].strip():
            errors.append(f"{p}.id must be a non-empty string")
        else:
            ids.append(node["id"])
        if node.get("kind") not in NODE_KINDS:
            errors.append(f"{p}.kind is unsupported")
        if node.get("lifecycle_state") not in NODE_STATES:
            errors.append(f"{p}.lifecycle_state is unsupported")
        source = node.get("source")
        if not isinstance(source, dict):
            errors.append(f"{p}.source must be an object")
        else:
            for field in ("source_type", "locator", "revision", "observed_at"):
                if field not in source:
                    errors.append(f"{p}.source missing {field}")
            try:
                datetime.fromisoformat(str(source.get("observed_at", "")).replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{p}.source.observed_at must be an ISO timestamp")
        if not isinstance(node.get("capabilities"), list):
            errors.append(f"{p}.capabilities must be an array")
        else:
            for ci, capability in enumerate(node["capabilities"]):
                if not isinstance(capability, dict) or not isinstance(capability.get("capability_id"), str):
                    errors.append(f"{p}.capabilities[{ci}] requires capability_id")
                elif capability.get("status") not in CAPABILITY_STATES:
                    errors.append(f"{p}.capabilities[{ci}].status is unsupported")
        if not isinstance(node.get("evidence"), list):
            errors.append(f"{p}.evidence must be an array")
        else:
            for ei, evidence in enumerate(node["evidence"]):
                if not isinstance(evidence, dict):
                    errors.append(f"{p}.evidence[{ei}] must be an object")
                    continue
                if not isinstance(evidence.get("evidence_id"), str) or not isinstance(evidence.get("status"), str):
                    errors.append(f"{p}.evidence[{ei}] requires string evidence_id and status")
                if evidence.get("status") not in EVIDENCE_STATES:
                    errors.append(f"{p}.evidence[{ei}].status is unsupported")
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
        if source not in known:
            errors.append(f"{p}.from references unknown node: {source}")
        if target not in known:
            errors.append(f"{p}.to references unknown node: {target}")
        if relation not in RELATIONSHIPS:
            errors.append(f"{p}.relationship is unsupported")
        if edge.get("status") not in {"hypothesis", "documented", "observed", "tested", "verified"}:
            errors.append(f"{p}.status is unsupported")
        identity = (str(source), str(target), str(relation))
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
