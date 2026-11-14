# Implementation Plan — QUE Device Validation

**Date:** 2026-11-14  
**Proposal:** `que-device-validation`  
**Branch:** `feat/que-device-validation-20261114`  
**Base:** `master`

## Task 1 — Governance and source record
- Create proposal MANIFEST, ITEMS and source RECON record.
- Register proposal in canonical `docs/proposals/registry.yaml`.
- Add proposal navigation entry.
- Verify proposal registry ↔ active directory consistency.

## Task 2 — Capability registry contract
- Add strict JSON Schema for tool profiles and module lanes.
- Add initial evidence-classified registry.
- Add a human-facing registry and RECON registration guide.
- Preserve separate registration, implementation, discovery, verification and availability states.

## Task 3 — Deterministic validation
- Implement stdlib-only registry validator.
- Validate unique IDs, required fields, lifecycle enums, capability declarations, lane-to-tool references and evidence references.
- Add unit tests for valid records, duplicate IDs, unresolved profiles, missing provenance, invalid states and module-lane independence.

## Task 4 — Architecture and DoE design
- Add control-plane design and Mermaid source.
- Document QUE boundary, backend taxonomy, state machine, evidence, security, failure handling and rollout.
- Pre-register comparison strategies and MoneyBall measurement without fabricated weights or results.

## Task 5 — Repository validation and finish
- Run focused validator and tests where an executable checkout is available.
- Run proposal registry validator, repo-gate and termux-smoke.
- Open PR with `Implements: QDV-001..QDV-007`.
- Re-fetch immutable PR head and wait for named dual gates.
- Merge only if gates are green on the same SHA, PR is mergeable and implementation outcome is verified.
- Record operational follow-up items QDV-008..QDV-010 as queued until their dependencies are satisfied.

## Constraints
- No workflow YAML change without confirming the workflow-write permission boundary.
- No device access or infrastructure provisioning without a verified, authorized runtime and budget.
- No second queue, event ledger, experiment schema, generic evidence envelope or CMDB.
