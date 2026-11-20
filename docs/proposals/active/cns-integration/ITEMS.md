# ITEMS — cns-integration

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| CNS-06 | P1 | executing | Integrate the merged Brain kernel through the canonical QUE/QDesk host, route one bounded MOSAIC specialist call through the typed extension contract, preserve run identity, delegate policy to its authoritative owner, and emit an attributable receipt. | Kernel and MOSAIC packages merged; policy-gated shadow composition passes on Rust 1.85.0 and 1.100.0; receipt artifacts identify orchestration/cycle/attempt and evidence; canonical host and bridge owner verified; fresh Delphi admission recorded before production activation; production host tests prove reasoning-to-handoff while execution and memory authority remain with existing owners. |

## Milestones

- [x] Root Brain kernel and typed extension contract merged in PR #5525.
- [x] MOSAIC pure specialist crate, typed adapter, and cross-crate contract tests present in master.
- [x] Standard Brain reasoning path composed with the injected PolicyGate and MOSAIC typed extension.
- [x] Ready policy decision permits the bounded specialist handoff.
- [x] NeedsApproval policy decision blocks specialist handoff.
- [x] Orchestration, cycle, and attempt identity preserved through the shadow response.
- [x] Rust 1.85.0 and 1.100.0 CI matrices pass; each retains an attributable receipt artifact.
- [ ] Canonical QUE/QDesk Brain host owner and bridge contract verified from the owning source.
- [ ] Versioned production bridge maps host input, policy decision, specialist result, and ORCHESTRATION-RECEIPT fields.
- [ ] Fresh Delphi admission recorded for the production integration surface.
- [ ] Production adapter runs through the verified host policy and revocation path.
- [ ] Host integration tests and runtime receipt validate one bounded production vertical slice.

## Current disposition

CNS-06 remains executing. The kernel-to-specialist shadow composition is merged and validated. Production host wiring remains blocked on canonical QUE/QDesk ownership, bridge-contract evidence, and fresh Delphi admission. Device Termux is outside the dependency chain for the current Rust integration tests; GitHub-hosted Linux runners provide the verified execution surface.
