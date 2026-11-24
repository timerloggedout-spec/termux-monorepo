# Production and legal-research boundary

**Date:** 2026-11-23  
**Proposal item:** AR-27  
**Branch:** `refactor/legal-research-silo-20261123`

## Objective

Remove automated license analysis from production CI, isolate licensing and terms source research, and keep production engineering focused on technical evidence and explicit operator decisions.

## Design

1. Disable license analysis in the dependency advisory while retaining dependency vulnerability detection.
2. Remove the dangling `license_compliance_checker.py` taxonomy entry.
3. Place public-source legal/licensing observations and procurement research under `research/legal-licensing/`.
4. Replace the provider runtime's `terms_accepted` assertion with `operator_authorized` and version the admission contract as `provider-route-admission/v2`.
5. Keep vulnerability scanning, secret scanning, dependency integrity, privacy, account/budget controls, tests, and source provenance as engineering controls.
6. Route legal interpretation and rights determinations to qualified counsel.

## Acceptance

- Workflow sets `license-check: false` and `vulnerability-check: true`.
- Workflow contract test asserts vulnerability-only behavior.
- Runtime policy requires `operator_authorized: true` and no longer reads `terms_accepted`.
- Research documents and procurement matrix are located in the isolated research silo.
- Production documentation points to the silo without claiming legal interpretation.
- Repository gate, Termux smoke, provider tests, and PR checks run against the exact head SHA.

## Execution record

The implementation is committed on the feature branch. Hosted validation remains pending until the PR workflow cohort completes.
