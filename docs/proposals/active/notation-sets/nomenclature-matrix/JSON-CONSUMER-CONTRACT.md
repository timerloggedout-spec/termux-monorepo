# Nomenclature Crosswalk — JSON Consumer Contract

**Contract version:** 1  
**Artifact:** [CROSSWALK.json](./CROSSWALK.json)  
**Source of truth:** [seed.json](./seed.json)  
**Generator:** [build_nomenclature_crosswalk.py](../../../../scripts/ci/build_nomenclature_crosswalk.py)

## 1. Purpose and authority

The JSON crosswalk is a deterministic read projection for indexing, inspection, analysis, and downstream research tooling. It is not a write API, canonical database, proof system, or runtime authorization source.

Consumers must honor the authority_boundary field. Candidate or reviewed data must not be treated as accepted runtime vocabulary without a separate, explicit governance decision.

## 2. Top-level shape

| Field | Type | Contract |
|---|---|---|
| projection_version | integer | Consumer-facing projection schema version; currently 1. |
| source_seed | string | Source seed filename; currently seed.json. |
| authority_boundary | string | Explicit warning that the projection is candidate research data, not runtime authority or approval. |
| sources | array | Source bibliography records, kept separate from claims. |
| concepts | array | Concept records with their labels nested under each concept. |
| mappings | array | Typed relationships between concept IDs, separate from labels. |
| evidence_records | array | Claim-level provenance records separate from bibliography and semantic mappings. |

## 3. Consumer rules

1. Treat concept_id, label_id, mapping_id, source_id, and evidence_id as opaque stable identifiers. Do not derive identity from display text.
2. A concept's labels array may be empty. Do not drop the concept because it has no curated labels.
3. Do not merge mappings into labels. A mapping connects concepts; a label names a concept.
4. Preserve each mapping's relation and status. Do not collapse related_match, close_match, exact_match, or explanatory/analogy relations into a generic synonym.
5. Preserve language, audience, and register when ranking or displaying labels. A preferred label is contextual, not universally preferred.
6. Join evidence by assertion type and assertion ID, then verify source IDs. Do not assume that a source record supports every assertion in the seed.
7. Treat missing optional values as missing—not as a positive assertion. In particular, an empty reviewer does not mean anonymous approval.
8. Do not infer acceptance from confidence scores, evidence counts, source authority strings, or successful CI.
9. Unknown future fields should be ignored safely where possible; unknown projection versions must not be parsed as version 1.
10. Never write modifications back into this generated projection. Update the seed, validate, and regenerate both projections.

## 4. Determinism and freshness

For the same valid seed and generator version, output ordering and serialization are deterministic. Regenerate with:

~~~bash
python scripts/ci/build_nomenclature_crosswalk.py
~~~

The generator writes Markdown and JSON projections together. To generate to alternate paths, use --output and --json-output. CI regression tests compare generated output with checked-in artifacts; a mismatch indicates stale generated files or a changed generator/seed contract.

## 5. Compatibility policy

- A breaking top-level shape or meaning change requires incrementing projection_version and updating this document and tests.
- Adding an optional field without changing existing field meaning may remain within the current version, but consumers should ignore unknown fields.
- Removing/renaming a field, changing its type, changing identifier semantics, or changing the authority boundary is breaking.
- Changes to seed records do not automatically change the projection version unless the contract shape or semantics change.
- Consumers should pin or record the projection version and source commit when reproducibility matters.

## 6. Explicit non-goals

This contract does not define an HTTP API, authentication, mutation semantics, a production runtime vocabulary, or a merge/approval policy. Those require separate design and governance decisions.
