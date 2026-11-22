# Incumbent vs VultrInspired Provider Catalogue — Implementation Plan

**DoE:** `DOE-VULTR-CATALOG-001 v2.0.0`  
**Proposal:** MSM-025  
**Branch:** `feat/provider-catalog-competition-v2-20261122`

## Task 1 — establish the native competitor

- [x] Add `scripts/provider_model_catalog_vultr_inspired.py` with a pure offline projection from incumbent v5.
- [x] Preserve identity, limits, source pricing values, access evidence and source provenance.
- [x] Add structured modality/capability/lifecycle fields and unknown-field preservation.
- [x] Isolate malformed rows and diagnose non-exact numeric pricing values.
- [x] Declare zero network, credential and inference side effects.
- [x] Add an offline runner that writes both catalogue snapshots plus a SHA-256 manifest from one supplied v5 document.

## Task 2 — version the experiment

- [x] Register Incumbent v5.0.0 and VultrInspired v1.0.0 as the local variants.
- [x] Pin Vultr Python and TypeScript under source references; keep local catalogue variants repository-owned.
- [x] Define paired controls, factors, response variables, acceptance criteria and immutable run keys.
- [x] Set network and inference modes to disabled; retain planned status and empty result artifacts.

## Task 3 — regression coverage

- [x] Add tests for exact decimal strings, integer prices, float precision diagnostics and unknown fields.
- [x] Add malformed-row isolation, schema rejection and paired catalogue population tests.
- [x] Add registry and metadata inventory regression coverage.
- [ ] Run focused tests and strict refTemplates inventory validation on the final head.
- [ ] Run same-head repository gate and Termux smoke.

## Task 4 — governance and review

- [x] Document local variants, upstream references and compute boundaries.
- [x] Update the MSM-025 proposal record and DoE design.
- [ ] Obtain independent review and reconcile same-head validation.

## Deferred follow-on

1. Add source-native adapters that retain exact pricing before incumbent float conversion.
2. Expand deterministic fixtures across modality and capability families.
3. Add raw payload snapshots and cache freshness only against a supported local source contract.
4. Run paired measurements; increment DoE version for design changes.
5. Promote runtime adoption only through a separately reviewed change.

## Validation record

Implementation and tests are committed to the feature branch. Focused test execution, CI, Termux smoke, independent review and experiment measurements remain pending. Termux device health remains unobserved because the device-info MCP action is unavailable in this session.
