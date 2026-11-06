---
id: master-splinter
title: AppID control plane (Registrar)
author: ChatGPT
status: in_review
priority: P1
---

# AppID control plane (Registrar)

This manifest indexes the proposal record and its reconciled scope. The historical proposer title is retained only in `INTAKE.md`; the registry naming ruling in `EVALUATION.md` is authoritative.

## Disposition

**ADAPT** — a read-only control plane over the existing eight-AppID family, not a replacement App identity and not a ninth App. Usage is a join over QUE, telemetry receipts, and lane-events; no parallel usage store is created.

## Source documents

- `INTAKE.md` — relayed proposal, provenance, and binding owner gates
- `EVALUATION.md` — reconciliation, name ruling, and provisioning disposition
- `SPEC.md` — scoped PRD, technical design, read-model schema, and dry-run replay contract

## Binding constraints

- Inventory first.
- No deploy or credential cutover under this proposal package.
- No new App identity or new permission manifest.
- No credential custody, write-token minting, or duplicate source-of-record stores.
- Repo/App provisioning and credential movement remain explicitly owner-gated as recorded in the source documents.

## Governance

The registry status remains `in_review`. This manifest is a navigation and scope record; it does not authorize implementation, deployment, credential movement, or changes to the existing AppID family.
