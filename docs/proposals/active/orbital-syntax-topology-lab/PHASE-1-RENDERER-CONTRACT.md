# Phase 1 — Canonical record and renderer adapter contract

**Status:** design contract derived from the current `master` Evidence Spine v2; implementation proposal only  
**Source of truth:** `foresight/schema.json`, `foresight/registry.py`, `docs/ops/FORESIGHT-EVIDENCE-SPINE.md`  
**Branch:** `feat/orbital-syntax-topology-lab`

## 1. Existing contract (do not fork)

The existing record requires:

- identity: `resource_id`, `item_id`, `lane_id`;
- descriptive fields: `title`, `category`, `summary`;
- assessment: `horizon` (H0-H3), `evidence_status`, `confidence` (0-1);
- provenance: `source.url`, matching `canonical_source`, `observed_at`;
- optional evidence, unresolved questions, tags and procurement metadata.

The registry normalizer supplies compatibility defaults for older records, calculates an evidence hash, and validates canonical source equality. The procurement object is restricted by the current validator to the declared fields: license, canonical_source, maintenance, portability, offline_capability, interoperability, reproducibility, provenance, dependency_risk, lock_in_risk, security_surface, resource_cost, operational_fit, horizon, confidence and decision_status.

**Important:** the current schema permits additional top-level properties but the registry validator rejects unknown keys inside `procurement`. Do not add arbitrary vendor scorecards or new procurement keys without a separate schema/validator proposal and tests.

## 2. Renderer-neutral view model

The first implementation should be a pure projection, not a new persisted schema. For each normalized record expose:

| View-model property | Source | Rule |
|---|---|---|
| id | `resource_id` | Stable cross-view key; never use array index |
| itemId | `item_id` | Preserve distinct item identity |
| laneId | `lane_id` | Preserve lane ownership |
| title | `title` | Plain text; escape at renderer boundary |
| category | `category` | Use as category label only; do not assume a quadrant taxonomy |
| horizon | `horizon` | Categorical H0-H3; not a numeric axis |
| evidenceStatus | `evidence_status` | Preserve exact enum |
| confidence | `confidence` | Optional numeric measure; do not substitute for maturity or impact |
| summary | `summary` | Plain text |
| source | `canonical_source` | Must agree with `source.url` |
| observedAt | `observed_at` | Display as observed date/time; do not infer publication date |
| evidence | `evidence` | Preserve source claims and contradictions |
| unresolvedQuestions | `unresolved_questions` | Keep visible as uncertainty |
| tags | `tags` | Filter metadata |
| procurement | `procurement` | Preserve existing typed object; no renderer-side invention |

The projection may add ephemeral display metadata (layout coordinates, filtered state, selection state), but it must not write these values back to the canonical record.

## 3. Axes and encodings — explicit limits

The current canonical record does **not** define a universal impact score, maturity score, strategic-priority score, or dependency graph. Therefore:

- H0-H3 may be used as discrete horizon groupings only where the product question supports that interpretation.
- `confidence` must not be plotted as technology maturity.
- `evidence_status` must not be treated as confidence.
- `category` must not be silently promoted to an impact quadrant.
- No radar x/y coordinate may be calculated from fields that do not exist.
- Until separately specified, use categorical rings/groups or a list/table; label any experimental axes as illustrative and never persist them as facts.
- Relationship graph edges require explicit, sourced relationship records. Similar tags or textual co-occurrence are not proof of a dependency.

## 4. Unknown and contradictory data

- Missing/unknown remains missing; do not coerce to zero, H3, low confidence, or negative evidence.
- Preserve `disputed` as an evidence status and render supporting and contradicting evidence separately.
- A source that cannot be reached is not automatically a contradiction.
- Multiple model outputs or repeated URLs are not independent corroboration without an independence assessment.
- Do not collapse different `resource_id` records solely because titles are similar.

## 5. Cross-view invariants

Every view adapter must satisfy:

1. stable identity and record count after applying the same filters;
2. equivalent selected-record detail and source links;
3. consistent handling of missing values and disputed status;
4. keyboard-accessible selection and a semantic non-visual alternative;
5. deterministic ordering for equivalent input;
6. no hidden data mutation and no external network requirement for local fixtures.

## 6. Minimal test fixture plan

Create synthetic records (not purported real-world technology claims) covering:
- one record per H0-H3;
- one disputed record with both supporting and contradicting evidence;
- one record with unknown confidence;
- one record with missing optional fields;
- two records sharing a category but distinct stable IDs;
- one record with long title and long source URL;
- one procurement assessment with a decision status;
- one pair with explicit relationship evidence only after a relationship schema is approved.

The same fixture is consumed by radar, table/list, tree and orbital adapters. Test equivalence by `resource_id`, not pixel snapshots alone.

## 7. Required follow-on before implementation

- Inspect registry corpus and existing tests to identify actual compatibility requirements.
- Add a pure adapter module with no writes and no browser globals.
- Add unit tests for mapping, stable identity, unknowns and contradiction preservation.
- Keep impact/maturity/priority axes deferred until their definitions, scales, provenance and assessment governance are approved.
- Keep the RFP scorecard separate; map supplier evaluations into existing procurement fields only where semantics match. Do not overload confidence or decision status with a weighted vendor score.

## 8. Evidence references

- `foresight/schema.json`
- `foresight/registry.py`
- `docs/ops/FORESIGHT-EVIDENCE-SPINE.md`
- `docs/research/FORESIGHT-RADAR.md`
