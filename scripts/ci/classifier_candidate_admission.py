#!/usr/bin/env python3
"""Build a deterministic, evidence-aware admission view for classifier candidates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def build_report(registry: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    entries = {item["id"]: item for item in catalog.get("entries", [])}
    rows = []
    for candidate in registry.get("candidates", []):
        if candidate.get("kind") == "local":
            disposition = "incumbent_baseline"
            eligible = True
        elif candidate.get("qualification_state") == "unclassified":
            disposition = "awaiting_capability_qualification"
            eligible = False
        else:
            state = candidate.get("operational_state")
            if state == "evaluated_self_hosted" and candidate.get("adapter_status") == "available":
                disposition, eligible = "replication_candidate", True
            elif state == "blocked_paid_owner_gate":
                disposition, eligible = "requires_owner_paid_approval", False
            elif state == "trial_candidate_composition_required":
                disposition, eligible = "requires_serving_composition", False
            elif state == "trial_candidate_host_blocked":
                disposition, eligible = "host_or_egress_blocked", False
            elif state == "referenced_not_runnable":
                disposition, eligible = "referenced_without_runnable_release", False
            else:
                disposition, eligible = "qualification_required", False
        entry = entries.get(candidate.get("catalog_entry_id"), {})
        rows.append({
            "candidate_id": candidate["candidate_id"],
            "catalog_entry_id": candidate.get("catalog_entry_id"),
            "name": entry.get("name", candidate["candidate_id"]),
            "roles": candidate.get("roles", []),
            "qualification_state": candidate.get("qualification_state"),
            "operational_state": candidate.get("operational_state"),
            "disposition": disposition,
            "eligible_for_role_matched_trial": eligible,
            "source_ref": candidate.get("source_ref"),
        })
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["disposition"]] = counts.get(row["disposition"], 0) + 1
    return {
        "schema": "classifier.candidate-admission-report.v1",
        "registry_id": registry.get("registry_id"),
        "registry_version": registry.get("registry_version"),
        "catalog_model_count": sum(1 for item in entries.values() if item.get("layer") == "model"),
        "infrastructure_reference_count": len(registry.get("infrastructure", [])),
        "candidate_count": len(rows),
        "eligible_count": sum(1 for row in rows if row["eligible_for_role_matched_trial"]),
        "disposition_counts": dict(sorted(counts.items())),
        "candidates": rows,
        "policy": {
            "comparison_scope": "within_role_and_task_contract",
            "catalog_presence_implies_capability": False,
            "paid_route_requires_owner_approval": True,
            "unclassified_candidates_enter_trials": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    registry = json.loads((root / "config/classifier_graph_registry.json").read_text(encoding="utf-8"))
    catalog = json.loads((root / "config/system_one_catalog.json").read_text(encoding="utf-8"))
    report = build_report(registry, catalog)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(
        f"PASS: {report['candidate_count']} candidates; "
        f"{report['eligible_count']} role-matched trial baselines/candidates; "
        f"{report['disposition_counts'].get('awaiting_capability_qualification', 0)} "
        "awaiting capability qualification"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
