#!/usr/bin/env python3
"""Validate typed, candidate-only references between nomenclature and domain matrices."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
LINKS_PATH = ROOT / "docs/proposals/active/notation-sets/nomenclature-matrix/DOMAIN-COMPOSITION-LINKS.json"
NOMENCLATURE_PATH = ROOT / "docs/proposals/active/notation-sets/nomenclature-matrix/seed.json"
DOMAIN_PATH = ROOT / "docs/proposals/active/domain-composition-matrix/seed.json"
TARGETS = {
    "domain": ("domains", "domain_id", {"domain_scope"}),
    "entity_type": ("entity_types", "entity_type_id", {"describes_entity_type"}),
    "operation": ("operations", "operation_id", {"describes_operation"}),
    "composition_rule": ("composition_rules", "rule_id", {"contextualized_by_rule"}),
}
STATUSES = {"candidate", "reviewed", "accepted", "rejected", "deprecated", "superseded"}

def validate(links, nomenclature, domain):
    errors = []
    if links.get("schema_version") != 1:
        errors.append("unsupported links schema_version")
    contracts = links.get("source_contracts", {})
    for name, data in (("nomenclature", nomenclature), ("domain_composition", domain)):
        declared = contracts.get(name, {}).get("schema_version")
        if declared != data.get("schema_version"):
            errors.append(f"{name} source schema_version mismatch")
    if "candidate only" not in links.get("authority_boundary", ""):
        errors.append("authority_boundary must preserve candidate-only status")

    concepts = {item.get("concept_id"): item for item in nomenclature.get("concepts", [])}
    targets = {
        target_type: {item.get(id_key): item for item in domain.get(collection, [])}
        for target_type, (collection, id_key, _) in TARGETS.items()
    }
    seen_ids = set()
    seen_edges = set()
    for item in links.get("links", []):
        link_id = item.get("link_id")
        if not isinstance(link_id, str) or not link_id.strip():
            errors.append("link requires nonblank link_id")
            continue
        if link_id in seen_ids:
            errors.append(f"duplicate link_id: {link_id}")
        seen_ids.add(link_id)

        concept_id = item.get("concept_id")
        if concept_id not in concepts:
            errors.append(f"{link_id} references unknown nomenclature concept: {concept_id}")
        target_type = item.get("target_type")
        if target_type not in TARGETS:
            errors.append(f"{link_id} has unsupported target_type: {target_type}")
            continue
        _, _, allowed_relations = TARGETS[target_type]
        relation = item.get("relation")
        if relation not in allowed_relations:
            errors.append(f"{link_id} relation {relation} is invalid for target_type {target_type}")
        target_id = item.get("target_id")
        if target_id not in targets[target_type]:
            errors.append(f"{link_id} references unknown {target_type}: {target_id}")
        elif target_type == "domain" and concept_id in concepts:
            if concepts[concept_id].get("domain_id") != target_id:
                errors.append(f"{link_id} domain scope disagrees with concept domain")
        elif target_type == "entity_type" and concept_id in concepts:
            target_domain = targets[target_type][target_id].get("domain_id")
            if concepts[concept_id].get("domain_id") != target_domain:
                errors.append(f"{link_id} entity type crosses concept domain")
        elif target_type == "composition_rule" and concept_id in concepts:
            target_domain = targets[target_type][target_id].get("domain_id")
            if concepts[concept_id].get("domain_id") != target_domain:
                errors.append(f"{link_id} composition rule crosses concept domain")

        edge = (concept_id, target_type, target_id, relation)
        if edge in seen_edges:
            errors.append(f"duplicate cross-matrix edge: {edge}")
        seen_edges.add(edge)

        status = item.get("status")
        if status not in STATUSES:
            errors.append(f"{link_id} has invalid status: {status}")
        if not isinstance(item.get("basis"), str) or not item["basis"].strip():
            errors.append(f"{link_id} requires a bounded basis")
        if not isinstance(item.get("non_equivalence_note"), str) or not item["non_equivalence_note"].strip():
            errors.append(f"{link_id} requires a non-equivalence boundary")
        if status == "accepted":
            reviewer = item.get("reviewer")
            reviewed_on = item.get("reviewed_on")
            if not isinstance(reviewer, str) or not reviewer.strip():
                errors.append(f"{link_id} accepted link requires nonblank reviewer")
            if not isinstance(reviewed_on, str) or len(reviewed_on) != 10:
                errors.append(f"{link_id} accepted link requires reviewed_on YYYY-MM-DD")
    return errors

def main():
    try:
        links = json.loads(LINKS_PATH.read_text(encoding="utf-8"))
        nomenclature = json.loads(NOMENCLATURE_PATH.read_text(encoding="utf-8"))
        domain = json.loads(DOMAIN_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unable to load cross-matrix inputs: {exc}", file=sys.stderr)
        return 1
    errors = validate(links, nomenclature, domain)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"nomenclature-domain-links: OK links={len(links.get('links', []))} status=candidate-only")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
