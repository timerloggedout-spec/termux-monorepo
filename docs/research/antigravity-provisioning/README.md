# AGY provisioning MVT / DoE research lane

**Status:** research artifacts, not a provisioning authorization  
**Parent:** [#1567 — MVT-DoE/TLM RFP](https://github.com/timerloggedout-spec/termux-monorepo/issues/1567)  
**Operational source context:** [#1497](https://github.com/timerloggedout-spec/termux-monorepo/issues/1497), [PR #1514](https://github.com/timerloggedout-spec/termux-monorepo/pull/1514)

This directory establishes a reproducible comparison lane for the Antigravity CLI provisioning approach. It does not designate the current rollout as correct, and it does not authorize new device access, model calls, settings changes, installation, merge, or promotion.

## Artifacts

- [V0 snapshot manifest](V0-SNAPSHOT.md) — immutable as-found reference and provenance ledger.
- [Provisioning instruction validation matrix](INSTRUCTION-VALIDATION-MATRIX.md) — claims classified by evidence, with gaps and next tests.
- [TLM run receipt contract](TLM-RUN-RECEIPT.md) — shared receipt fields and a minimal example.
- [MVT / DoE / Delphi operating protocol](PROTOCOL.md) — candidate isolation, fair comparison, scoring, evidence freeze, and disposition.

## Current evidence boundary

The available repository records describe work and tests on the existing secondary Termux device, including a bounded implementer/verifier pair. They also record important failures and unknowns: the implementer run ended INCOMPLETE at transport exit 255 with unknown model/token totals; the verifier's PASS missed a deterministic non-finite-quota regression; native enumeration and skill discovery, nested delegation, Termux:Boot first-launch/reboot delivery, whole-app force-stop recovery, and full provisioning remain unverified. See the linked operational records before interpreting this summary.

This documentation branch does not rerun any device operation or model request. No live device validation was performed while preparing these artifacts.

## Decision rule

V0 is a comparison baseline, not a gold standard. Candidate selection requires validated requirements, comparable trials, hard safety gates, raw observations, transparent weights and preserved dissent. The operator retains implementation/promotion authority under the repository's normal review gates.
