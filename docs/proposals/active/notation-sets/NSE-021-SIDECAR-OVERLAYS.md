# NSE-021 — Sidecar Comment Overlays and Siglary Context Tournament

**Parent:** `notation-sets-evolution`  
**State:** accepted for execution — Operator vote recorded 2026-11-21 (term `NSE-021/1`)  
**Design:** [2026-11-20 design](../../../superpowers/specs/2026-11-20-siglary-sidecar-overlays-design.md)  
**Plan:** [2026-11-20 implementation plan](../../../superpowers/plans/2026-11-20-siglary-sidecar-overlays.md)

## Scope

Create content-addressed sidecar overlays for eligible prose in `docs/icm/**/*.md` and `workspace/llm_map/**/*.md`, plus syntax-aware code comments discovered through authoritative ICM/LLM source references.

Compare four representations—English control, operator-first, dense registered notation, and hybrid—across entry-point, related-context, and mixed placement. Use staged screening, MVT, factorial interaction testing, and held-out replication.

## Required invariants

- Canonical source files remain byte-identical throughout experimental arms.
- Every overlay pins source blob SHA, SHA-256, stable anchor, notation version, renderer version, and provenance.
- Executable code token streams remain identical across comment-overlay materialization.
- Markdown structure and protected technical spans remain byte-identical.
- Root `CLAUDE.md` and `CLAUDE.hum.md` retain their README-declared primary-entry and Linguist/tooling-compatibility roles; historical `AGENTS.md` / `AGENTS.hum.md` projection aliases and rename provenance remain traceable.
- Quality, semantic recovery, parse validity, and comprehension floors gate token/latency optimization.

## Deliverables

1. Bounded source inventory and canonical/projection mapping ledger.
2. Overlay schema, stable-anchor extractor, validator, renderer, and disposable materializer.
3. Deterministic integrity and round-trip fixtures.
4. Pre-registered DoE/MVT campaign using the existing experiment record contract.
5. Replicated, quality-gated release candidate and comment/documentation-only promotion patch.

## Dependencies and governance

Reuse NSE-020's lossless mapping/pointer contract, ICM-08's repository-native FA-ADE maintenance process, `docs/ops/DOE-FAMILY.md`, and `docs/ops/MVT-DOE-ATES-SEPARATION.md`. Keep the proposal posted until the Operator records acceptance. Implementation and corpus conversion begin after acceptance.

**Acceptance:** bounded inventory complete; mapping aliases verified; source/executable-token invariants pass; staged campaign pre-registered; held-out replication meets quality floors; exact-head dual gates green before promotion.
