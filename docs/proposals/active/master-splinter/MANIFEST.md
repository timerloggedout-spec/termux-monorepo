---
id: master-splinter
title: "AppID control plane (proposer title: Master Splinter; not adopted)"
author: ChatGPT
posted_at: 2026-11-03
source: "INTAKE.md, EVALUATION.md, SPEC.md, AppID migration plan, and merged PR #4642"
status: in_review
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
  - id: appid-migration-plan
    role: evaluator
    status: executing
related_issues: []
related_prs:
  - 4642
related_branches:
  - control-plane-readmodel
gates_required:
  - repo-gate
  - termux-smoke
---

# MANIFEST — AppID control plane

## Summary

This proposal records the adapted AppID control-plane concept. The original proposer title "Master Splinter" is retained only as attributed provenance in INTAKE.md and is explicitly **not adopted** as a product, repository, App, or family name. The Registry-issued working name is **Registrar**; the family vocabulary is **AppID migration**.

The control plane is a read model over the existing eight-AppID family. It consolidates inventory, declared-versus-observed permission snapshots, migration lineage, dry-run replay receipts, and usage joins while preserving the existing Apps and stores of record.

## Scope and boundaries

- Read from the existing AppID inventory, permission manifests/readbacks, migration records, telemetry receipts, QUE admission data, and lane-events store.
- Keep usage as a view/join over existing records; do not create a parallel usage system.
- Keep repo replay and commit replay engines/stores separate; migration dry-run replay is limited to migration-wave simulation.
- No new App identity, no new credential, no credential cutover, and no deployment authorization is implied by this proposal.
- Collector reads and Publisher writes remain the existing authorized pair; any future workflow-resident minting identity question returns to the AppID lane.

## Evidence

- The detailed reconciliation and naming ruling are in EVALUATION.md.
- The scoped PRD/technical/schema/replay contract is in SPEC.md.
- PR #4642 merged the AppID control-plane read model over lane-events, a dispatch-only loader, and a G4-shaped receipt path. The PR body reports a dry-tested load (30 INSERTs).
- MIGRATION-ITEMS.md remains the fleet's item-level evidence ledger; this manifest is a proposal navigation/governance contract, not a replacement for that ledger.

## Promotion

The proposal remains in review until remaining open items have owner-lane evidence and the operator disposition is recorded. A merged implementation slice does not imply that every migration, telemetry, drift-audit, or cadence item is complete.
