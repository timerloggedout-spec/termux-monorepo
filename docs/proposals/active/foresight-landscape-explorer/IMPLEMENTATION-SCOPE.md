# Foresight Landscape Explorer — independent implementation track

**Status:** new implementation path; separate from Orbital Syntax PR #2980.  
**Branch:** `feat/foresight-landscape-explorer`  
**Base:** `master`  
**System of record:** existing Foresight Evidence Spine v2.

## Scope

Build a reusable technology-landscape explorer around the existing evidence spine. The goal is research discovery, evidence inspection, temporal comparison and relationship exploration across complementary views. Orbital Syntax is not assumed to be the target architecture or product direction.

## Non-negotiable design constraints

- Do not modify or depend on PR #2980.
- Do not duplicate the canonical registry or invent a parallel evidence schema.
- Preserve `resource_id`, `item_id`, `lane_id`, `canonical_source`, horizon and evidence status.
- Keep horizon, evidence status, confidence, maturity, impact and strategic priority semantically distinct.
- Unknown is not zero; unreachable sources are not contradictions; repetition is not independent corroboration.
- Do not infer relationship edges from tag overlap or text co-occurrence.
- Read-only local fixture first; no write-back to source systems.
- No hosted service or third-party dependency without independent review.

## Architecture direction

1. Canonical evidence records from existing registry/schema.
2. Pure renderer-neutral projection adapter (ephemeral view model only).
3. Complementary views over the same records: table/list first, then hierarchy/tree, radar only where axis semantics are valid, and relationship graph only for explicit evidence-backed edges.
4. Detail/provenance inspector with source, observed date, evidence, contradictions and unresolved questions.
5. Search/filter/sort with stable identity and cross-view selection.
6. Offline local fixture and portable export.

## Phases

- **0 — Repository audit:** inspect current schema, registry corpus, tests and UI conventions. Document existing capabilities and gaps.
- **1 — Projection contract:** pure adapter, fixture, invariants and tests.
- **2 — Table/list and detail:** accessible baseline, search/filter, provenance and stable cross-view selection.
- **3 — Tree and radar:** add only with explicit category/horizon/axis semantics; no invented scores.
- **4 — Relationship graph:** only after a sourced relationship contract exists.
- **5 — Evaluation:** task-based comparison, accessibility, density, mobile and offline testing.
- **6 — Integration decision:** separate review and explicit approval before any SHE or other hub integration.

## Phase 1 acceptance

- deterministic mapping from canonical record to view model;
- stable resource identity independent of array order;
- preservation of disputed status and supporting/contradicting evidence;
- missing/unknown values remain missing;
- no write operations or network requirement;
- tests for malformed records, missing fields, duplicate titles and long labels;
- same filtered record IDs and selected detail across views.

## Governance

This track has its own future PR and review. Do not reuse PR #2980, its branch, artifacts or review state. The RFP is a separate research branch and can inform a later decision, but does not block basic adapter work. Do not merge automatically.
