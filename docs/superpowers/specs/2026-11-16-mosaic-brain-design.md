# MOSAIC Brain — repository-context and methodology reasoning design

**Work package:** MOS-001 through MOS-006  
**Parent lane:** Continuous Capability Evolution Laboratory (CEEL)  
**Methodology family:** DoE  
**Status:** implementation proposal with a bounded pure-Rust core  
**Version:** 0.1.0 · 2026-11-16

## Decision

Use a dedicated ArchWiz subsystem at:

- **Location:** \`archwiz/mosaic_brain/\`
- **Rust module:** \`archwiz/mosaic_brain/src/brain.rs\`
- **Crate:** \`mosaic-brain\`
- **Scope:** \`methodology_intelligence\`
- **Context-graph scope ID:** \`mosaic-brain\`
- **Authority:** advisory recommendation only

Do not place MOSAIC decision logic inside \`archwiz/context_relationships/rust_accel/\`. That crate is an optional hot path for fragment fingerprinting and pointer-cost analysis. Its Python compiler remains authoritative for graph validation, evidence classification and canonical artifacts. Keeping those boundaries separate avoids coupling methodology decisions to an unrelated optimization path.

## Repository consciousness model

Treat repository consciousness as the existing, distributed, source-backed system:

1. Git history, issues, pull requests, reviews and source files provide primary evidence.
2. The Context Relationship Graph (CRG) provides metadata-only, evidence-qualified relationships.
3. ICM and proposal registries provide navigation, ownership and lifecycle.
4. Canonical DoE EXPERIMENT records provide run-level observations.
5. Delphi/EGM and existing proposal/dual-gate governance provide independent challenge and state-transition authority.
6. MOSAIC Brain evaluates bounded methodology evidence and emits a recommendation with references.

MOSAIC Brain is a reasoning subsystem over those sources. It is not a second memory store, context graph, telemetry ledger, experiment registry, event bus, scheduler, orchestrator, provider router or merge authority.

## Location and scope contract

| Field | Value |
|---|---|
| location | \`archwiz/mosaic_brain/\` |
| scope | \`methodology_intelligence\` |
| context_graph_scope_id | \`mosaic-brain\` |
| inputs | immutable method identity, evidence references, independent review, gate snapshot, outcome dimensions |
| output | \`PromotionCandidate\`, \`Hold\` or \`Revise\` recommendation with reasons |
| persistence | source-controlled code and docs; canonical source records remain elsewhere |
| side effects | none in the core |
| promotion authority | existing repository-managed FA-ADE and proposal lifecycle |

The context graph integration is read-only. The scope registry may identify MOSAIC Brain files; the normal graph publisher owns generated index updates. A stale or partial graph snapshot is reported as stale evidence, never silently treated as current.

## Core contract

### Method identity

A method version is identified by:

- stable method ID;
- immutable version label;
- owner identity;
- declared scope ID;
- source commit SHA;
- SHA-256 of the method artifact.

A material change to design, assignment, analysis, stopping, thresholds or promotion logic creates a new method version. Historical versions remain addressable.

### Evidence references

Evidence references contain identifiers, source URIs and evidence kinds. They never copy PR bodies, issue bodies, review text, raw prompts, completions, credentials, private traces or restricted customer data.

Canonical experiment observations remain in \`docs/ops/corpus/EXPERIMENT.schema.json\`. MOSAIC Brain consumes references to those records; it does not define a second experiment schema.

### Evaluation snapshot

An evaluation snapshot records:

- evaluator identity and method-owner identity;
- independent review verdict;
- evidence references;
- practical-gain status;
- critical-regression status;
- required-gates status;
- rollback-readiness status.

Unknown values remain typed unknowns (\`Option\` in the Rust core and schema-native nulls in serialized records). Missing evidence never becomes a pass.

### Recommendation rules

- **Revise:** independent review refutes the claim or a critical regression is evidenced.
- **Hold:** evidence is missing, review is partial/pending, the evaluator is not independent, practical gain is absent/unknown, gates are pending/failed, or rollback readiness is unknown/false.
- **PromotionCandidate:** every required condition is explicitly established: independent verified review, evidence present, practical gain, no critical regression, required gates passed and rollback ready.
- **Cull:** remains a governance decision outside the core.

A PromotionCandidate is not a promotion. Existing repository-managed FA-ADE may promote an independently validated, scope-bounded change after the required dual gates pass and its outcome is verified. MOSAIC Brain cannot grade itself, approve itself, merge, dispatch experiments or change production routing.

## Rust API boundary

The initial crate uses the Rust standard library only.

- \`MethodIdentity\` validates method ID, version, owner, scope, source commit and artifact hash.
- \`EvidenceRef\` stores a source identifier, source URI and evidence kind.
- \`EvaluationSnapshot\` carries independent review and gate facts.
- \`recommend\` is a deterministic, pure function.
- \`Recommendation\` expresses a recommendation and reasons without performing a state transition.

No filesystem, network, GitHub API, model call, environment mutation or persistent state belongs in the core. Adapters may be proposed separately after their source and permission boundaries are reviewed.

## Siglary integration

SON is a proposed Siglary authoring profile, not a private dialect. It uses registered Siglary operators and the existing DO-statement marker. New glyphs and chords require Linguist review and Matrice admission before normative use. The existing DO-statement style workflow remains the enforcement path.

## Validation

- Unit and integration tests cover identity validation, evidence presence, reviewer independence, unknown values, review verdicts, critical regressions and promotion-candidate conditions.
- Rust formatting and tests run through a focused GitHub Actions workflow.
- Context-relationship scope validation runs through existing repository gates.
- Repo-gate, Termux smoke and proposal lifecycle run on the same immutable PR head.
- Independent review remains required before merge.

## Deferred work

Defer live graph clients, persistent recommendations, experiment dispatch, adaptive allocation, automatic methodology mutation, external model calls, paid inference and production promotion. Each requires a separate evidence-backed proposal and existing governance admission.
