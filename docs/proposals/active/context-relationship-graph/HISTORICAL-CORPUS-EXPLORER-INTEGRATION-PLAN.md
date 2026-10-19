# Historical Corpus Explorer — Integration Plan

**Proposal:** `context-relationship-graph`  
**Work item:** CRG-15  
**Status:** Proposed / not yet implemented  
**Target:** Existing SHE dashboard and canonical context-relationship corpus  
**Evidence baseline:** `master` at `9241ecdc8f44a447cade8ad59bd0491780cdcbf8` (inspected 2026-10-19)

## Executive decision

Build the Historical Corpus Explorer as a **read-only view of existing canonical evidence**, integrated with SHE. Do not create a second collector, graph database, manifest, history store, or scheduler. The canonical Git-tracked corpus remains authoritative; SHE snapshots and UI are projections.

The MVP should answer four questions quickly:

1. **What does this corpus actually cover?**
2. **Which relationships are verified versus candidate, and why?**
3. **What changed between two immutable observations?**
4. **Can every displayed claim be traced to evidence and an immutable source revision?**

The user experience must prioritize comprehension over density: plain-language labels first, source terminology available in details, warnings adjacent to the numbers they qualify, and no color-only encoding. “Missing,” “unknown,” “candidate,” and “not yet validated” are different states and must remain different.

## Verified repository facts

Observed via the connected GitHub read API. Links point to canonical repository sources.

- Canonical corpus: [`workspace/llm_map/context_relationships/`](https://github.com/timerloggedout-spec/termux-monorepo/tree/master/workspace/llm_map/context_relationships).
- Schema: [`config/context_relationships/schema.json`](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/config/context_relationships/schema.json).
- Core corpus artifacts documented by [corpus README](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/corpus/README.md): `manifest.json`, `nodes.jsonl`, `edges.jsonl`, `matrix.json`, source/GitHub/merge reports, checkpoint, and build summary.
- SHE PRD: [`docs/ops/SHE-DASHBOARD-PRD.md`](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/SHE-DASHBOARD-PRD.md). It defines SHE as a projection, not the source of truth, and forbids presenting partial evidence as complete.
- SHE snapshot contract: [`docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md`](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md). It requires source SHA, generation time, coverage state, and provenance; `UNVERIFIED` must not become zero.
- SHE architecture: [`docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd`](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd). The `.mmd` file is the architecture source.
- Existing bounded backfill and read-only progression observer: [backfill workflow](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/.github/workflows/context-relationship-backfill.yml), [watcher workflow](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/.github/workflows/context-relationship-backfill-watcher.yml).
- Existing proposal process: [`docs/proposals/PROCESS.md`](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/proposals/PROCESS.md); proposal work is registered in `docs/proposals/registry.yaml` and itemized in the active proposal.
- PR #523 is currently **closed, not merged**: [PR #523](https://github.com/timerloggedout-spec/termux-monorepo/pull/523). Its history is contextual evidence, not proof of a merged implementation.
- The path [`workspace/llm_map/context_relationships/temporal/temporal-current.json`](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/workspace/llm_map/context_relationships/temporal/temporal-current.json) returned 404 at inspection. The backfill status document describes an L2 temporal layer, but the existence of that exact current-file path is not verified.

### Current corpus snapshot observed on master

Manifest blob SHA: `abef63ef1bb3278bdc144fcfc32dac22a0510979`.

| Signal | Observed value |
|---|---:|
| Nodes | 30,978 |
| Edges | 52,624 |
| Verified edges | 47,845 |
| Candidate edges | 4,779 |
| History start page | 13 |
| `next_start_page` | `null` |
| PRs in declared history window | 0 |
| Issues in declared history window | 25 |
| PR window stubs | 18 |
| `checkpoint_eligible` | `false` |
| Latest observation | 2026-10-15T19:16:02.945529Z |

The build summary says `coverage: COMPLETE`, while the manifest reports zero PRs, 18 PR window stubs, and `checkpoint_eligible: false`. This is a real semantic/reconciliation question. A null continuation cursor is not, by itself, proof of exhaustive all-time history. The Explorer must show the declared status and separately flag unresolved contradictions; it must not silently redefine canonical source fields.

The counts above are an inspection-time evidence record, **not constants**. Runtime values must be read from the selected manifest/snapshot.

## Product design

### 1. Coverage and provenance strip

Always display source ref/SHA, snapshot ID, manifest blob SHA, generated/observed time, counts, declared coverage, reconciliation state, and known exclusions/failures.

Use the canonical coverage status unchanged. Add a separate projection-level reconciliation state, for example `RECONCILIATION_REQUIRED`, when facts conflict. Explain the difference between “collector reports complete for its declared window” and “all-time exhaustiveness proven.”

### 2. Bounded graph explorer

Render a filtered neighborhood, not the full graph by default. Provide filters for node kind, edge type, verified/candidate classification, time (only when supported), score (only when present), evidence kind, and neighborhood depth.

Node detail: safe metadata, kind, canonical URL, observation time, neighboring edges.  
Edge detail: source/target, type, classification, optional score, evidence references, collector, snapshot identity.

Verified and candidate relationships must remain visibly and semantically distinct. Missing scores stay missing, not zero. Provide a keyboard-accessible table/list fallback.

### 3. Evidence drawer

For each displayed relationship, show evidence URL when safe and available, evidence type, collector, observed time, source snapshot ID, source SHA, classification, and explicit unknown/low-confidence values where provenance is incomplete.

Do not infer causality, intent, model/provider authorship, or personal attribution from graph proximity or actor names.

### 4. Timeline and snapshot comparison — gated

Enable timeline/range/point-in-time features only after verifying the repository-native temporal query CLI, output schema, immutable snapshots, deltas, and lineage. The SHE contract documents:

- `temporal_query --timeline`
- `temporal_query --at TIMESTAMP`
- `temporal_query --between START END`
- `temporal_query --changes-only --between START END`

These commands are documented interfaces, but the exact executable and current L2 files still require verification. If unavailable, show a clear `UNVERIFIED / TEMPORAL DATA UNAVAILABLE` state; do not manufacture history from the latest L1 graph.

## Integration architecture

```text
GitHub evidence
  -> existing context-relationship collector
  -> canonical Git-tracked corpus
  -> schema / integrity / coverage validator
  -> SHE versioned snapshot and pure reducers
  -> Historical Corpus Explorer
  -> deep links to canonical GitHub evidence
```

Reuse existing components:

- Collector: `archwiz.context_relationships.build_index`.
- Canonical artifacts: `workspace/llm_map/context_relationships/`.
- Schema: `config/context_relationships/schema.json`.
- Projection contract: `docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md`.
- Backfill/watch operations: existing workflows and their current permission boundaries.
- Diagrams: extend the existing authoritative `.mmd` → generated-asset automation if a diagram is added.
- Deployment: extend the existing SHE/Vercel-first path; Pages is an optional static mirror; Hex remains an optional consumer, never a runtime dependency.

Do not scaffold a second app until the actual SHE app root and package/test commands have been located.

## Proposed snapshot extension

Only add fields if the existing SHE contract cannot express the view. Preserve required fields `schema_version`, `snapshot_id`, `source_ref`, `source_sha`, `generated_at`, coverage, and manifest identity.

Projection-only fields may include:

- `reconciliation.status` and `reconciliation.warnings[]`;
- `temporal.available` and a reason when unavailable;
- source-bound counts and integrity-check results.

Never overwrite canonical coverage with a UI interpretation. Do not hard-code inspection-time counts in production output.

## Integrity and validation requirements

Before publishing a new snapshot:

1. Parse JSON and JSONL and validate records against the checked-in schema.
2. Verify node IDs are unique and all edge endpoints resolve.
3. Verify edge classifications remain exactly `verified` or `candidate`.
4. Verify evidence structure and safe URL handling.
5. Reconcile manifest counts with parsed records and report mismatches.
6. Confirm verified + candidate counts reconcile to total edges, or emit an explicit failure if the contract changes.
7. Bind snapshot to the checked-out source SHA and manifest blob SHA.
8. Verify deterministic output for identical inputs, excluding explicitly volatile fields.
9. If temporal data exists, validate parent references, acyclic lineage, snapshot hashes, and delta reconciliation.
10. Treat `next_start_page: null` as one input to coverage evaluation, never as the only all-time completeness gate.
11. Preserve and display parser failures, excluded files, unresolved references, and `checkpoint_eligible: false`.

Failed validation blocks publication of a new snapshot but preserves the last known-good snapshot, marked stale with its source SHA.

## Security boundaries

- Read-only explorer; no GitHub writes and no workflow dispatch.
- No write token in browser bundles. Snapshot generation should use least-privilege read access.
- No raw discussion bodies, credentials, cookies, tokens, browser/session state, or arbitrary payloads.
- Treat all corpus strings as untrusted; escape rendered text, reject unsafe URL schemes, and never render arbitrary HTML/SVG from records.
- Bound response size, neighborhood depth, time range, and displayed nodes/edges.
- Do not execute candidate code or untrusted PR content in the explorer or observer.
- Preserve unknown attribution and evidence confidence; no unsupported identity or causal claims.
- Each snapshot is auditable through source SHA, manifest SHA, schema version, generation time, and validation receipt.

## Phased delivery and exit gates

### Phase 0 — reconcile evidence (P0)
- Re-fetch manifest, nodes, edges, reports, and build summary at one immutable SHA.
- Explain zero PR count versus 18 PR stubs and `checkpoint_eligible: false`.
- Define exactly what `coverage: COMPLETE` means.
- Locate the real temporal CLI, L2 files, lineage, tests, and SHE app root.
- Reconcile stale/missing documentation references.
**Exit:** coverage semantics and temporal availability are documented and testable.

### Phase 1 — pure validator and snapshot (P0)
- Add deterministic validation/reduction under existing code conventions.
- Add fixtures for complete, partial, failed, unverified, malformed, and contradictory inputs.
- Surface reconciliation separately from canonical coverage.
**Exit:** focused tests pass and output is reproducible.

### Phase 2 — graph MVP (P1)
- Add Explorer to the existing SHE application.
- Implement bounded graph queries, filters, evidence drawer, deep links, and accessible table fallback.
**Exit:** graph remains bounded; every item has provenance or an explicit unavailable state.

### Phase 3 — temporal UX (P1, gated)
- Consume verified immutable L2 snapshots/deltas/lineage.
- Implement timeline and comparison only against validated historical snapshots.
**Exit:** a view is reproducible from snapshot IDs; no history is inferred from latest-state data.

### Phase 4 — CI and publication (P1)
- Integrate into existing validation and publication lanes.
- Preserve last-known-good output on failure.
- Publish a receipt containing source SHA, manifest SHA, snapshot ID, test results, and publication outcome.
**Exit:** Actions evidence confirms actual execution and validation; deployment is claimed only after URL and source revision are re-fetched.

## Test matrix

- **Unit:** schema validation, malformed input, duplicate IDs, missing endpoints, evidence URL safety, classification preservation, missing-score semantics, count reconciliation, deterministic IDs, privacy projection, and coverage contradictions.
- **Temporal:** lineage validity, delta correctness, snapshot identity, unavailable-data behavior.
- **Integration:** frozen canonical-shaped fixtures; source SHA and manifest blob SHA binding; source count reconciliation; evidence deep links; no write/dispatch capability.
- **UI acceptance:** coverage visible; verified/candidate distinction; bounded rendering; keyboard operation; semantic table fallback; explicit stale/error/unknown states.
- **Repository gates:** run `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py` on the same immutable head SHA, and record actual results. Do not infer green from queued/in-progress states.

## Immediate next actions

1. Reconcile corpus completeness semantics and the manifest's PR/stub/checkpoint fields.
2. Verify the actual L2 temporal implementation and SHE app root.
3. Implement the validator before UI work.
4. Deliver the read-only graph MVP.
5. Add temporal comparison only after Phase 0 passes.
6. Wire into existing CI/publication and capture a provenance receipt.

## Delivery status

This file is a proposal/integration plan. At authoring time, no Explorer code, tests, workflow dispatch, deployment, commit, or merge is claimed by this document. Repository changes should be tracked through CRG-15 and the normal proposal/PR lifecycle.
