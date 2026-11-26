"""Pass through canonical registry records using explicit pre-pool gate output.

This module does not run or reproduce eligibility policy. It requires one explicit
boolean decision and a non-empty evidence_ref for every quota.registry.v2 service
ID, preserves the registry's record order and contents, and does not add
provider/model/account mappings or dispatch work. Evidence references are opaque;
the adapter does not fabricate or reinterpret them.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_prepool_cohort(registry: dict[str, Any], gate_output: dict[str, Any]) -> dict[str, Any]:
    """Join exact registry records to a complete, evidence-linked decision set.

    Expected gate output is ``{"decisions": [{"record_id": str,
    "eligible": bool, "evidence_ref": non_empty_str, ...evidence}]}``.
    Additional gate evidence is retained unchanged. Missing, duplicate, unknown,
    non-boolean, or unreferenced decisions fail closed.
    """
    if not isinstance(registry, dict) or registry.get("schema") != "quota.registry.v2":
        raise ValueError("invalid_registry_schema")
    services = registry.get("services")
    if not isinstance(services, list):
        raise ValueError("invalid_registry_services")

    registry_ids: list[str] = []
    seen_registry_ids: set[str] = set()
    for service in services:
        if not isinstance(service, dict):
            raise ValueError("invalid_registry_record")
        record_id = service.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("invalid_registry_record_id")
        if record_id in seen_registry_ids:
            raise ValueError("duplicate_registry_record_id")
        registry_ids.append(record_id)
        seen_registry_ids.add(record_id)

    if not isinstance(gate_output, dict) or not isinstance(gate_output.get("decisions"), list):
        raise ValueError("missing_gate_decisions")
    decisions: dict[str, dict[str, Any]] = {}
    for decision in gate_output["decisions"]:
        if not isinstance(decision, dict):
            raise ValueError("invalid_gate_decision")
        record_id = decision.get("record_id")
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("invalid_gate_record_id")
        if record_id not in seen_registry_ids:
            raise ValueError("unknown_gate_record_id")
        if record_id in decisions:
            raise ValueError("duplicate_gate_record_id")
        if not isinstance(decision.get("eligible"), bool):
            raise ValueError("invalid_gate_eligibility")
        evidence_ref = decision.get("evidence_ref")
        if not isinstance(evidence_ref, str) or not evidence_ref.strip():
            raise ValueError("invalid_gate_evidence_ref")
        decisions[record_id] = decision

    missing = seen_registry_ids.difference(decisions)
    if missing:
        raise ValueError("incomplete_gate_decisions")

    records = []
    planned_cohort_ids = []
    for service, record_id in zip(services, registry_ids):
        gate_decision = decisions[record_id]
        if gate_decision["eligible"]:
            planned_cohort_ids.append(record_id)
        records.append({
            "record_id": record_id,
            "registry_record": deepcopy(service),
            "gate_decision": deepcopy(gate_decision),
        })

    return {
        "schema": "doe.prepool-cohort.v1",
        "registry_schema": "quota.registry.v2",
        "gate_decisions_complete": True,
        "gate_evidence_refs_complete": True,
        "records": records,
        "planned_cohort_ids": planned_cohort_ids,
    }
