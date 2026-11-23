---
id: cns-integration
title: "Cognitive Network Systems integration — Brain kernel host composition"
author: ChatGPT
posted_at: 2026-11-20
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_issues:
  - 5693
  - 5588
  - 5501
related_prs:
  - 5525
  - 5712
related_branches:
  - feat/brain-shadow-host-composition-final
gates_required:
  - proposal-lifecycle
  - repo-gate
  - termux-smoke
---

# MANIFEST — cns-integration

## Summary

Integrate the merged Rust Brain kernel through the canonical QUE/QDesk host, compose one bounded specialist route through the typed extension interface, preserve orchestration/cycle/attempt identity, delegate capability policy to its authoritative owner, and emit an attributable orchestration receipt.

## Operator authorization

Operator direction received 2026-11-20: continue Brain integration without device Termux as a prerequisite; use repository CI and provisioned emulators when device-shaped verification is useful. This authorizes the bounded CNS-06 source-reconciliation, contract-test, and shadow-composition scope.

## Scope boundaries

- DO keep Brain focused on domain-neutral reasoning and typed specialist invocation.
- DO route methodology-intelligence evaluation through the MOSAIC pure specialist crate.
- DO delegate QUE admission, capability authorization, dispatch, device I/O, provider calls, memory persistence, proposal mutation, and promotion to their canonical owners.
- DO use the merged shadow composition as evidence for the kernel-to-specialist seam and policy-hold behavior.
- DO confirm the Brain-specific route and bridge with the QUE/QDesk owners while preserving the existing QDesk self-repair and generic QUE admission boundaries.
- DO gate production host activation on fresh Delphi admission and verified canonical QUE/QDesk host and bridge contracts, as recorded in issue #5693 and RFP #5501.
- DO retain the qdesk.brain-rs RFP's parked status at 6.69/25, with recheck after 2026-12-16T09:39Z and filing_grants_execution=false.

## Review log

### 2026-11-20 — timerloggedout-spec

- Disposition: accepted for the bounded CNS-06 source-reconciliation and shadow-integration scope.
- Notes: operator direction explicitly removes device Termux availability from the dependency chain. Production host activation retains the recorded admission and owner-contract gates.

## Checklist

- [x] Registered in docs/proposals/registry.yaml
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [x] Root Brain kernel and typed extension contract merged
- [x] MOSAIC specialist adapter and cross-crate tests present
- [x] Policy-gated shadow composition merged with attributable receipts
- [x] Existing QDesk self-repair host and generic QUE admission surfaces identified
- [ ] Brain-specific QUE/QDesk invocation owner and bridge contract verified
- [ ] Fresh Delphi admission recorded for production activation
- [ ] Production adapter and runtime receipt validated under authoritative policy
- [ ] Close after all items reach terminal disposition

## Links

- ITEMS: ./ITEMS.md
- Host reconnaissance: ./HOST-RECON.md
- Candidate bridge contract: ./BRIDGE-CANDIDATE.md
- Source record: ./source.md
- Implementation plan: ../../../superpowers/plans/2026-11-20-cns-integration.md
- CNS-06 issue: https://github.com/timerloggedout-spec/termux-monorepo/issues/5693
- MOSAIC design: ../continuous-capability-evolution-lab/MOSAIC-BRAIN-ROOT-INTEGRATION-PROPOSAL.md
