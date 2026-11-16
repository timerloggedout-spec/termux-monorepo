---
type: object
cluster: operations
universe: live
status: initiated
entity: archwiz/mosaic_brain/
verified_at: 2026-11-16
---

# MOSAIC Brain

MOSAIC is the methodology-intelligence specialist within the Continuous Capability Evolution Laboratory / DoE family. It evaluates immutable method identity and evidence references, then returns an advisory `PromotionCandidate`, `Hold` or `Revise` recommendation.

## Source

- Crate: [`archwiz/mosaic_brain/`](../../../../archwiz/mosaic_brain/)
- Pure recommendation engine: [`src/brain.rs`](../../../../archwiz/mosaic_brain/src/brain.rs)
- Root Brain adapter: [`src/adapter.rs`](../../../../archwiz/mosaic_brain/src/adapter.rs)
- Shared contract: [`brain/src/extensions.rs`](../../../../brain/src/extensions.rs)
- Integration proposal: [MOSAIC ↔ root Brain](../../../proposals/active/continuous-capability-evolution-lab/MOSAIC-BRAIN-ROOT-INTEGRATION-PROPOSAL.md)
- Work ledger: [CEEL ITEMS](../../../proposals/active/continuous-capability-evolution-lab/ITEMS.md)

## Contract

- Crate: `mosaic-brain`; Rust 2021; standard library only beyond the local `termux-brain` path dependency.
- Domain: `methodology_intelligence`; CRG scope ID: `mosaic-brain`.
- Method identity binds method ID, version, owner, scope, source commit and artifact SHA-256.
- Evidence is represented by source IDs and URIs; source bodies remain in canonical records.
- A distinct evaluator, independent verified review, evidence, practical gain, no critical regression, passing required gates and rollback readiness are all required for PromotionCandidate.
- Refutation or critical regression yields Revise; missing, malformed, unknown, incomplete or non-independent facts yield Hold.

## Authority and non-goals

MOSAIC is pure and deterministic. It does not read/write the filesystem, call GitHub or models, dispatch experiments, update DoE records, write CRG, mutate proposal state, merge, deploy or promote. Existing proposal lifecycle and repository-managed FA-ADE retain all state-transition authority.

## Integration status

The crate implements the root Brain extension contract and returns the same orchestration/cycle/attempt identity. The actual production host route is not yet wired: the existing QUE/QDesk host and bridge contract must be verified first. CRG scope metadata is registered, but generated graph publication remains with the existing publisher. The current CRG source collector parses Python only, so Rust source-file graph indexing is not claimed by this card.

## If you change this

Run `cargo fmt`, `cargo check --all-targets`, `cargo test` and Clippy for `archwiz/mosaic_brain/Cargo.toml`, plus proposal lifecycle, CRG scope and repository dual gates on the same PR head.
