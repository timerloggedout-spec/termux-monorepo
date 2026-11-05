---
id: master-splinter
title: "AppID control plane — proposal intake and scoped read-model"
author: ChatGPT
posted_at: 2026-11-03
source: INTAKE.md
status: in_review
priority: P1
reviewers:
  - timerloggedout-spec
  - appid-migration-plan
related_prs: []
related_branches: []
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — AppID control plane

## Summary

Registry wrapper for the AppID control-plane proposal. The evaluation disposition is **ADAPT**: build a read-only control plane over the existing specialist AppID family; do not replace the family with a new identity. The working reference is the AppID control plane; the Registry later issued the name **Registrar** for the software. The standalone repository was created as recorded in EVALUATION.md. This repository's package remains a specification and evidence record; no deployment, credential cutover, or new App identity is authorized by this manifest.

## Source of record

- [INTAKE.md](INTAKE.md) — original relayed proposal and binding intake gates.
- [EVALUATION.md](EVALUATION.md) — reconciliation, ADAPT verdict, naming ruling, and provisioning addenda.
- [SPEC.md](SPEC.md) — scoped PRD, technical specification, read-model schema, and dry-run replay contract.
- `ops/github-apps/MIGRATION-ITEMS.md` — existing migration item ledger; remains the source of truth for migration item IDs, statuses, and evidence.

## Review and authorization

- Registry status: `in_review`.
- Review seats: `timerloggedout-spec` and `appid-migration-plan`.
- This wrapper does not create or imply item-level authorization.
- Owner-gated actions remain gated: deployment, credential movement/cutover, new App provisioning, and any write capability beyond the existing family.

## Process note

The local `ITEMS.md` intentionally points to the existing migration ledger rather than duplicating item IDs or inventing statuses. Any future local work item must be explicitly mapped to the source ledger and carry its own recorded authorization and evidence.
