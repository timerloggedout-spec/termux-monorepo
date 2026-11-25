# Production and legal-research boundary

**Date:** 2026-11-23  
**Proposal item:** AR-32  
**Branch:** `refactor/legal-research-silo-20261123`

## Objective

Remove automated license analysis from production CI, isolate licensing and terms source research, and keep production engineering focused on technical evidence and explicit operator decisions.

## Design

1. Disable license analysis in the dependency advisory while retaining dependency vulnerability detection.
2. Remove the dangling `license_compliance_checker.py` taxonomy entry.
3. Remove license fields and ADOPT license gates from the technical procurement contract; migrate all 26 legacy values into `research/legal-licensing/PROCUREMENT-LICENSE-OBSERVATIONS.jsonl`.
4. Remove license metadata from provider research snapshots and version the snapshot contract to `msm-provider-recon-v2`.
5. Place public-source legal/licensing observations and procurement research under `research/legal-licensing/`.
6. Replace the provider runtime's `terms_accepted` assertion with `operator_authorized` and version the admission contract as `provider-route-admission/v2`.
7. Keep vulnerability scanning, secret scanning, dependency integrity, privacy, account/budget controls, tests, and source provenance as engineering controls.
8. Route legal interpretation and rights determinations to qualified counsel.

## Acceptance

- Workflow sets `license-check: false` and `vulnerability-check: true`.
- Workflow contract test asserts vulnerability-only behavior.
- Runtime policy requires `account_type` from the free-account set, `free_account_verified: true`, and `operator_authorized: true`; trial, promotional, evaluation, paid, unknown, and missing account classes fail admission. Legacy v1 policies remain disabled until v2 configuration.
- Provider workflow documentation distinguishes PR/master contract runs from input-gated manual observation, optional one-request smoke, and per-job permissions.
- Both procurement validators accept technical records and ADOPT decisions without a license field.
- The briefing registry validator accepts the migrated 26-record technical ledger without license metadata.
- Provider snapshots use `msm-provider-recon-v2` and omit `license_designation`.
- Legacy procurement license values are preserved in the research silo with unverified provenance.
- Research documents and procurement matrix are located in the isolated research silo.
- Production documentation points to the silo without claiming legal interpretation.
- Repository gate, Termux smoke, provider tests, and PR checks run against the exact head SHA.

## Execution record

The implementation is committed on the feature branch and submitted as PR #5838. Hosted validation is in progress against the current PR head SHA.
