# Nomenclature crosswalk consumer contract

## Scope

This document describes the checked-in `CROSSWALK.json` projection generated from `seed.json`. It is a local, versioned read model for research and tooling. It is not a network API, canonical ontology, runtime policy, or approval signal.

## Authority and freshness

- Source of truth for this lane: `seed.json`.
- Generator: `scripts/ci/build_nomenclature_crosswalk.py`.
- Generated projections: `CROSSWALK.md` and `CROSSWALK.json`.
- Regenerate with `python scripts/ci/build_nomenclature_crosswalk.py`.
- Do not edit generated outputs manually.
- CI/tests must detect stale projections by comparing generated output with checked-in artifacts.

The JSON metadata currently declares `projection_version: 1`, `source_seed: "seed.json"`, and the authority boundary `candidate research data only; not runtime authority or approval`.

## Top-level shape

| Field | Meaning |
|---|---|
| `projection_version` | Projection format version; consumers should reject unsupported major versions |
| `source_seed` | Relative seed filename used to produce this artifact |
| `authority_boundary` | Explicit candidate-only, non-authoritative boundary |
| `sources` | Source bibliography records |
| `concepts` | Concepts with nested typed labels |
| `mappings` | Typed semantic mapping candidates |
| `evidence_records` | Assertion-level evidence records |

## Consumer rules

1. Treat identifiers (`concept_id`, `label_id`, `mapping_id`, `evidence_id`, `source_id`) as stable references within this versioned dataset, not globally permanent identities.
2. Preserve typed separation: labels belong to concepts; mappings connect concepts; evidence supports one explicitly typed assertion.
3. Do not flatten all labels and mappings into a single synonym list.
4. Preserve language, audience, register, label type, status, relation, confidence, and source/evidence references when transforming records.
5. Do not interpret `confidence` as a calibrated probability unless a future specification defines calibration.
6. Do not treat `candidate`, `evidence_backed`, or `reviewed` as equivalent to `accepted`.
7. Do not infer equivalence from shared strings, symbols, examples, or adjacency in the source.
8. Do not promote records to runtime behavior. Consumers requiring authoritative semantics must consult the relevant domain authority and review process.
9. Unknown fields should be ignored by tolerant readers; missing required top-level fields or unsupported `projection_version` should fail closed.
10. Consumers should retain the source seed revision/commit alongside cached projections to support reproducibility.

## Versioning policy

- Additive fields and new records may remain within projection version 1 only when they preserve existing field meaning and do not break consumers.
- Renaming/removing fields, changing their types or semantics, or changing collection meaning requires a projection-version increment and corresponding consumer migration.
- A change to source seed structure must be accompanied by validator/test updates and regenerated Markdown/JSON.
- Generated JSON ordering is deterministic; consumers must not depend on array position as identity. Use record IDs.

## Not currently promised

- No HTTP endpoint or query API is defined.
- No stable external schema registry is declared.
- No automatic semantic reasoning or equivalence closure is promised.
- No automatic synchronization into the Domain Composition Matrix, notation runtime, or index surfaces is promised.
