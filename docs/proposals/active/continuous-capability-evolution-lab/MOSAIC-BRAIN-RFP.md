# RFP — MOSAIC Brain: bounded methodology intelligence subsystem

**RFP ID:** MOS-BRAIN-001  
**Parent:** CEEL / DoE family  
**Related:** MOSAIC meta-methodology specification; Siglary Notation Sets Linguist lane  
**Status:** proposed implementation slice · 2026-11-16

## DO

Establish a bounded, repository-native reasoning subsystem that evaluates versioned methodology evidence and returns explainable, source-linked recommendations.

## Location | Scope

| Dimension | Contract |
|---|---|
| location | \`archwiz/mosaic_brain/\` |
| module | \`archwiz/mosaic_brain/src/brain.rs\` |
| crate | \`mosaic-brain\` |
| scope | \`methodology_intelligence\` |
| CRG scope ID | \`mosaic-brain\` |
| read authority | metadata-only Context Relationship Graph references, canonical DoE records, proposal lifecycle and independent review evidence |
| output authority | advisory recommendation plus evidence references |
| state authority | existing proposal lifecycle and repository-managed FA-ADE |

## Problem statement

MOSAIC is the meta-methodology program that evaluates the methods used to design, assign, execute, analyze and promote experiments. It needs a small deterministic core that can validate method identity, test evidence completeness and distinguish a promotion candidate from a HOLD or REVISE outcome.

The repository already has a metadata-only Context Relationship Graph and an optional Rust accelerator. The graph's Python compiler remains authoritative. The accelerator is narrowly scoped to fragment fingerprinting and pointer-cost analysis. A methodology decision engine placed inside that accelerator would mix unrelated responsibilities.

The current published graph snapshot is dated 2026-10-26 and reports partial GitHub history coverage. The implementation must therefore treat graph freshness as explicit evidence metadata and use the existing publisher for refreshes.

## Requested deliverables

1. A Rust crate at \`archwiz/mosaic_brain/\` with a pure, deterministic recommendation API.
2. Immutable method identity and artifact provenance validation.
3. Evidence-reference types that point to canonical records without copying source bodies.
4. Independent-review and gate-aware recommendation rules.
5. Tests for missing/unknown evidence, self-review, regression, practical gain and rollback readiness.
6. A dedicated Rust test workflow.
7. A Context Relationship Graph scope entry and ICM route card.
8. Siglary SON proposal integration through the existing Notation Matrice and Linguist lane.
9. Architecture, lifecycle and sequence diagrams in Mermaid source.
10. MOS-001 through MOS-006 implementation plans with testable acceptance criteria.

## Functional requirements

- Preserve method ID, version, owner, scope, source commit and artifact SHA-256.
- Treat method versions as immutable.
- Consume evidence references rather than copying run, issue, PR or review bodies.
- Require evaluator identity distinct from the method owner.
- Preserve unknown values as unknown; do not coerce missing data to false or pass.
- Recommend HOLD when evidence or required gate facts are missing.
- Recommend REVISE when a refutation or critical regression is evidenced.
- Emit PromotionCandidate only when all promotion conditions are explicitly satisfied.
- Leave CULL and all actual state transitions to existing governance.
- Keep the core free of network, filesystem, model and GitHub side effects.

## Architecture constraints

- Reuse the existing Context Relationship Graph, DoE experiment schema, CEEL proposal, Delphi/EGM, SHE/3L0/MoneyBall and FA-ADE.
- Keep the existing Context Relationship Rust accelerator dedicated to its current hot-path responsibility.
- Let the normal context-graph publisher update generated artifacts after scope registration.
- Keep Siglary notation definitions under Linguist custody.
- Use the existing DO-statement style workflow and policy gates.
- Keep credentials, paid inference, external account writes and production routing outside this RFP.

## MOS work packages

| ID | Priority | Work | Acceptance |
|---|---:|---|---|
| MOS-001 | P0 | Location/scope and architecture contract | RFP, design, ICM route, CRG scope and source-of-truth boundaries are documented |
| MOS-002 | P0 | Immutable method identity and evidence types | Valid identities pass; malformed commit/hash/empty identity fails; evidence references preserve source provenance |
| MOS-003 | P0 | Pure recommendation function | Tests prove independent review, missingness, practical gain, regression, gates and rollback rules |
| MOS-004 | P1 | Repository consciousness integration | CRG scope is registered; generated index is refreshed only by its publisher; ICM routes to the smallest source set |
| MOS-005 | P1 | Siglary SON Linguist admission | Candidate grammar uses registered operators; Linguist ruling and Matrice state are recorded; existing gate remains authoritative |
| MOS-006 | P0 | CI and repository validation | Cargo fmt/test, repo-gate, Termux smoke and proposal lifecycle have same-head receipts |

## Acceptance gates

- Method identity is immutable and source-backed.
- The recommendation function is deterministic and side-effect free.
- Every PromotionCandidate has independent review, evidence, practical gain, no critical regression, passing gates and rollback readiness.
- Unknown evidence yields HOLD, not promotion.
- Context graph scope and ICM routing remain metadata-only and source-linked.
- SON remains candidate until the Linguist ruling is recorded.
- Focused Rust checks and repository dual gates pass on one immutable PR head.
- Independent review is recorded before merge.

## Explicitly deferred

Defer a live graph client, persistent brain memory, LLM inference, experiment dispatch, adaptive allocation, automatic self-modification, automatic CULL, merge automation and production routing. Submit each as a separate proposal with source evidence, permission analysis and rollback.

## Review request

Request independent review from the MOSAIC/DoE methodology owner, Context Relationship Graph maintainer and Siglary Linguist. Record disagreements and dispositions in the proposal review log. Keep the RFP open until all required evidence is present.
