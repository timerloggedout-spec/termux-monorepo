# Plan — Provider Family × Configured Instance × DoE Settings Observatory

**Proposal:** `provider-family-doe-observatory`  
**Items:** PFDO-001–PFDO-004  
**Base:** `master`  
**Branch:** `feat/provider-family-doe-observatory-20261111`

## Goal

Expose the existing provider, execution-family and DoE settings contracts as one navigable experience without creating a second source of truth or changing `nested-family/v1`.

## Work sequence

1. Register this bounded scope and record owner authorization.
2. Correct Family and Swarm Quota feed references and stale refresh copy.
3. Add a machine-readable DoE settings projection whose values are sourced from the existing DoE register; explicitly preserve unknown singular DoE version as `NOT_ESTABLISHED`.
4. Add a focused DoE Settings page and shared navigation.
5. Display existing `instance_key` values in Family task rows; do not synthesize missing values or expose raw prompt/tool content.
6. Document the relationship and QDesk boundaries.
7. Add offline regression tests for projection semantics, feed paths, navigation and schema preservation.
8. Run focused tests, proposal validation, repo-gate and termux-smoke; open a PR and inspect current checks.

## Non-goals

- Rebuild the quota or nested-family collectors.
- Change `nested-family/v1` or its single-writer workflow.
- Infer missing provider/model/version/prompt/tool identities.
- Create a second scheduler, queue, dispatch engine, outcome ledger or DoE campaign store.
- Provision accounts, mint credentials, modify GitHub App permissions, or execute suspension-class actions.
- Claim deployment or runtime completion before checks and served-state verification.

## Verification

Focused tests:
`python3 -m pytest tests/test_doe_settings_register.py tests/test_tribute_family_integrity.py -q`

Governance and integration:
`python3 scripts/proposals/validate_registry.py`
`python3 scripts/ci/repo_gate.py`
`python3 scripts/ci/termux_smoke.py`
