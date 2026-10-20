#!/usr/bin/env python3
"""Validate the candidate nomenclature equivalency seed without network access."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / "docs/proposals/active/notation-sets/nomenclature-matrix/seed.json"
LABEL_TYPES = {
    "preferred_formal", "preferred_plain_language", "alternative_synonym",
    "colloquial", "ad_hoc", "jargon", "abbreviation", "symbolic_notation",
    "historical", "deprecated", "misspelling", "translation", "analogy",
    "near_synonym", "related_term", "external_identifier",
}
RELATIONS = {
    "same_concept_label", "exact_match", "close_match", "broad_match",
    "narrow_match", "related_match", "explains", "analogy_to",
    "translates_to", "supersedes", "ambiguous_with", "contradicts",
}
STATUSES = {"discovered", "candidate", "evidence_backed", "reviewed", "accepted", "rejected", "deprecated", "superseded"}

def validate(data):
    errors = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    sources = data.get("sources", [])
    concepts = data.get("concepts", [])
    labels = data.get("labels", [])
    mappings = data.get("mappings", [])
    source_ids = [x.get("source_id") for x in sources]
    concept_ids = [x.get("concept_id") for x in concepts]
    label_ids = [x.get("label_id") for x in labels]
    mapping_ids = [x.get("mapping_id") for x in mappings]
    for name, ids in (("source", source_ids), ("concept", concept_ids), ("label", label_ids), ("mapping", mapping_ids)):
        if None in ids or len(ids) != len(set(ids)):
            errors.append(f"{name} IDs must be present and unique")
    source_set, concept_set = set(source_ids), set(concept_ids)
    for s in sources:
        if not all(s.get(k) for k in ("title", "url", "source_type", "authority")):
            errors.append(f"source {s.get('source_id')} missing required metadata")
    for c in concepts:
        if not all(c.get(k) for k in ("domain_id", "preferred_label", "definition")):
            errors.append(f"concept {c.get('concept_id')} missing required fields")
        if c.get("status") not in STATUSES or not isinstance(c.get("version"), int) or c.get("version", 0) < 1:
            errors.append(f"concept {c.get('concept_id')} has invalid status/version")
        if not set(c.get("source_ids", [])).issubset(source_set):
            errors.append(f"concept {c.get('concept_id')} references unknown sources")
    for l in labels:
        if l.get("concept_id") not in concept_set:
            errors.append(f"label {l.get('label_id')} references unknown concept")
        if l.get("label_type") not in LABEL_TYPES or l.get("status") not in STATUSES:
            errors.append(f"label {l.get('label_id')} has invalid type/status")
        if not all(l.get(k) for k in ("text", "language", "audience", "register")):
            errors.append(f"label {l.get('label_id')} missing label metadata")
        if not set(l.get("source_ids", [])).issubset(source_set):
            errors.append(f"label {l.get('label_id')} references unknown sources")
    for m in mappings:
        if m.get("source_concept_id") not in concept_set or m.get("target_concept_id") not in concept_set:
            errors.append(f"mapping {m.get('mapping_id')} references unknown concept")
        if m.get("relation") not in RELATIONS or m.get("status") not in STATUSES:
            errors.append(f"mapping {m.get('mapping_id')} has invalid relation/status")
        if not isinstance(m.get("confidence"), (int, float)) or not 0 <= m.get("confidence", -1) <= 1:
            errors.append(f"mapping {m.get('mapping_id')} confidence must be within [0,1]")
        if not m.get("evidence_note") or not set(m.get("source_ids", [])).issubset(source_set):
            errors.append(f"mapping {m.get('mapping_id')} needs evidence note and valid sources")
        if m.get("relation") == "exact_match" and m.get("status") == "accepted" and not m.get("source_ids"):
            errors.append(f"accepted exact mapping {m.get('mapping_id')} requires evidence")
    return errors

def main():
    try:
        data = json.loads(SEED.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot load seed: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors), file=sys.stderr)
        return 1
    print(f"OK: {len(data['concepts'])} concepts, {len(data['labels'])} labels, {len(data['mappings'])} mappings, {len(data['sources'])} sources (candidate data only)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
