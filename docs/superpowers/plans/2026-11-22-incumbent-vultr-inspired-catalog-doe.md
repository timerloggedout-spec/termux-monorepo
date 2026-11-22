# Full Provider/Model Pool — Incumbent vs VultrInspired Tournament Plan

**DoE:** `DOE-VULTR-CATALOG-001 v3.0.0`  
**Proposal:** MSM-025  
**Branch:** `feat/provider-catalog-competition-v2-20261122`

## Task 1 — compile the full candidate population

- [x] Reconcile the 172-record/118-provider service registry, 91-record/89-provider model bench, 60-provider g4f catalog and 160-provider/9,588-pair g4f universe.
- [x] Preserve the 7,341 historical Actions-verified endpoint floor as a separate dated evidence population.
- [x] Preserve 5,347 upstream-only, 1,156 fork-only and 3,085 overlapping g4f pairs.
- [x] Seed every enumerated candidate with source provenance and closed runtime/admission state.

## Task 2 — establish the native competitor

- [x] Add `scripts/provider_model_catalog_vultr_inspired.py` with a pure offline projection from incumbent v5.
- [x] Preserve identity, limits, source pricing values, provider observations, cadence classes, source errors, access evidence and source provenance.
- [x] Add structured modality/capability/lifecycle fields and unknown-field preservation.
- [x] Isolate malformed rows and diagnose non-exact numeric pricing values.
- [x] Declare zero network, credential and inference side effects.
- [x] Add an offline runner that writes both catalogue snapshots plus a SHA-256 manifest from one supplied v5 document.

## Task 3 — version the experiment

- [x] Register Incumbent v5.0.0 and VultrInspired v1.0.0 as the local variants.
- [x] Pin Vultr Python and TypeScript under source references; keep local catalogue variants repository-owned.
- [x] Define paired controls, factors, response variables, acceptance criteria and immutable run keys.
- [x] Set network and inference modes to disabled; retain planned status and empty result artifacts.

## Task 4 — regression coverage

- [x] Add tests for exact decimal strings, integer prices, float precision diagnostics and unknown fields.
- [x] Add malformed-row isolation, schema rejection and paired catalogue population tests.
- [x] Add registry and metadata inventory regression coverage.
- [ ] Run focused tests and strict refTemplates inventory validation on the final head.
- [ ] Run same-head repository gate and Termux smoke.

## Task 5 — governance and review

- [x] Document local variants, upstream references and compute boundaries.
- [x] Update the MSM-025 proposal record and DoE design.
- [ ] Obtain independent review and reconcile same-head validation.

## Deferred follow-on

1. Add source-native adapters that retain exact pricing before incumbent float conversion.
2. Expand deterministic fixtures across modality and capability families.
3. Add raw payload snapshots and cache freshness only against a supported local source contract.
4. Run task-specific pool tournaments through the existing admission and evaluator path; increment DoE version for design changes.
5. Promote runtime adoption only through a separately reviewed change.

## Validation record

Implementation and tests are committed to the feature branch. Focused test execution, CI, Termux smoke, independent review and experiment measurements remain pending. Termux device health remains unobserved because the device-info MCP action is unavailable in this session.
