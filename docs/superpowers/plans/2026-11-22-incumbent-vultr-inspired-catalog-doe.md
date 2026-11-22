# Incumbent vs VultrInspired Provider Catalogue — Implementation Plan

**DoE:** `DOE-VULTR-CATALOG-001 v2.0.0`  
**Proposal:** MSM-025  
**Branch:** `feat/provider-catalog-vultr-inspired-v1-20261122`

## Goal

Compare the incumbent v5 provider catalogue with one repository-native VultrInspired projection. Treat the two pinned Vultr language implementations as equivalent source references.

## Task 1 — establish the native competitor

- [x] Add `scripts/provider_model_catalog_vultr_inspired.py` with a pure offline projection from incumbent v5.
- [x] Preserve identity, limits, source pricing values, access evidence and source provenance.
- [x] Add structured modality/capability/lifecycle fields and unknown-field preservation.
- [x] Isolate malformed rows and diagnose non-exact numeric pricing values.
- [x] Declare zero network, credential and inference side effects.

## Task 2 — version the experiment

- [x] Promote registry and experiment design to v2.0.0.
- [x] Define Incumbent v5.0.0 and VultrInspired v1.0.0 as the two local variants.
- [x] Move Vultr Python and TypeScript pins into source-reference metadata.
- [x] Define paired controls, factors, response variables, acceptance criteria and immutable run keys.
- [x] Set network and inference modes to disabled; retain planned status and empty result artifacts.

## Task 3 — regression coverage

- [x] Add tests for exact decimal strings, integer prices, float precision diagnostics and unknown fields.
- [x] Add malformed-row isolation and schema rejection tests.
- [x] Update registry tests to assert native catalogue variants and separate upstream reference pins.
- [ ] Run focused tests and strict refTemplates inventory validation on the final head.
- [ ] Run same-head repository gate and Termux smoke.

## Task 4 — documentation and governance

- [x] Distinguish local competitors from equivalent upstream references in the catalogue README.
- [x] Record compute/network/inference boundaries and incumbent-vs-VultrInspired comparison in RECON.
- [x] Update design specification and DoE registry.
- [ ] Reconcile MSM-025 proposal status and independent review.

## Deferred follow-on

1. Add source-native adapters that retain exact pricing before incumbent float conversion.
2. Expand deterministic fixtures across modality and capability families.
3. Add raw payload snapshots and cache freshness only against a supported local source contract.
4. Run paired measurements; increment DoE version for any design changes.
5. Promote runtime adoption only through a separately reviewed change.

## Validation record

Implementation and tests are committed to the feature branch. Focused test execution, CI, Termux smoke, independent review and experiment measurements remain pending. Termux device health is unobserved because the device-info MCP action is unavailable in this session.
