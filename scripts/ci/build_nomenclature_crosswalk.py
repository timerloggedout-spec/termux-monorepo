#!/usr/bin/env python3
"""Render a deterministic Markdown crosswalk from the candidate nomenclature seed."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED = ROOT / "docs/proposals/active/notation-sets/nomenclature-matrix/seed.json"
DEFAULT_OUTPUT = ROOT / "docs/proposals/active/notation-sets/nomenclature-matrix/CROSSWALK.md"


def cell(value):
    """Escape Markdown table delimiters and normalize line breaks."""
    return str(value if value is not None else "").replace("|", r"\|").replace("\r", " ").replace("\n", " ").strip()


def render_crosswalk(data):
    concepts = sorted(data.get("concepts", []), key=lambda x: x["concept_id"])
    labels_by_concept = {}
    for label in data.get("labels", []):
        labels_by_concept.setdefault(label["concept_id"], []).append(label)
    mappings = sorted(data.get("mappings", []), key=lambda x: x["mapping_id"])
    evidence = sorted(data.get("evidence_records", []), key=lambda x: x["evidence_id"])
    lines = [
        "# Nomenclature Equivalency Crosswalk",
        "",
        "Generated from seed.json by scripts/ci/build_nomenclature_crosswalk.py. Do not edit by hand.",
        "Candidate research data only: this projection does not promote labels or mappings to accepted/runtime authority.",
        "",
        "## Concept and label crosswalk",
        "",
        "| Concept ID | Domain | Preferred concept label | Definition | Label | Label type | Language | Audience | Register | Status | Sources |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for concept in concepts:
        labels = sorted(labels_by_concept.get(concept["concept_id"], []), key=lambda x: (x.get("label_type", ""), x.get("text", "").casefold(), x.get("label_id", "")))
        for label in labels:
            values = (
                concept["concept_id"], concept.get("domain_id", ""), concept.get("preferred_label", ""),
                concept.get("definition", ""), label.get("text", ""), label.get("label_type", ""),
                label.get("language", ""), label.get("audience", ""), label.get("register", ""),
                label.get("status", ""), ", ".join(label.get("source_ids", [])))
            lines.append("| " + " | ".join(cell(v) for v in values) + " |")
    lines.extend([
        "",
        "## Semantic mapping candidates",
        "",
        "| Mapping ID | Source concept | Relation | Target concept | Status | Confidence | Sources | Evidence note |",
        "|---|---|---|---|---|---:|---|---|",
    ])
    for mapping in mappings:
        values = (
            mapping.get("mapping_id", ""), mapping.get("source_concept_id", ""), mapping.get("relation", ""),
            mapping.get("target_concept_id", ""), mapping.get("status", ""), mapping.get("confidence", ""),
            ", ".join(mapping.get("source_ids", [])), mapping.get("evidence_note", ""))
        lines.append("| " + " | ".join(cell(v) for v in values) + " |")
    lines.extend([
        "",
        "## Claim-level evidence",
        "",
        "| Evidence ID | Assertion | Source | Locator | Claim boundary | Excerpt | Retrieved | Reviewer | Status |",
        "|---|---|---|---|---|---|---|---|---|",
    ])
    for item in evidence:
        values = (
            item.get("evidence_id", ""), item.get("assertion_type", "") + ":" + item.get("assertion_id", ""),
            item.get("source_id", ""), item.get("evidence_locator", ""), item.get("claim", ""),
            item.get("evidence_excerpt", ""), item.get("retrieved_on", ""), item.get("reviewer") or "unassigned",
            item.get("status", ""))
        lines.append("| " + " | ".join(cell(v) for v in values) + " |")
    lines.extend([
        "",
        "## Interpretation rules",
        "",
        "- A label is a name or expression for a concept; it is not itself a mapping between concepts.",
        "- same_concept_label, exact_match, close_match, broad_match, narrow_match, and related_match are distinct relations and must not be collapsed.",
        "- Candidate status is preserved from the seed. A generated row is not approval, review, or mathematical verification.",
        "- Evidence excerpts and locators are research aids; reviewers must inspect the cited source before accepting a claim.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = json.loads(args.seed.read_text(encoding="utf-8"))
    output = render_crosswalk(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"OK: rendered crosswalk for {len(data.get('concepts', []))} concepts, {len(data.get('labels', []))} labels, {len(data.get('mappings', []))} mappings, {len(data.get('evidence_records', []))} evidence records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
