# Provider Catalog Competition — Full-Pool Design v3

**Date:** 2026-11-22  
**Proposal:** MSM-025  
**DoE:** DOE-VULTR-CATALOG-001 v3.0.0

## Goal

Build and compare Incumbent and VultrInspired across the complete provider/model candidate pool. The v5 collector remains one live-observation layer; the population also includes registry-backed model providers, the g4f working catalog and the full g4f endpoint universe. Use pinned Vultr Python and TypeScript repositories as equivalent design references only.

## Architecture

- Incumbent v5 remains the source collector and current evidence contract.
- VultrInspired v2 is implemented in `scripts/provider_model_catalog_vultr_inspired.py` as a pure offline projection over the source-hash-bound full-pool population; the v5 projection remains backward-compatible.
- Vultr Python and TypeScript pins live in reference metadata and the DoE `source_references` list; local execution uses repository-owned code.
- The projection preserves the incumbent record and adds structured limits, modalities, capability groups, pricing provenance, lifecycle, access evidence, extensions and per-row diagnostics.
- Provider-specific wire protocols remain in their existing adapter modules.

## Compute and side-effect contract

Local fixture comparison uses the repository's existing Python runtime and ordinary local CPU/RAM. The projection performs zero HTTP requests, zero credential lookups and zero inference calls. Live catalogue observation remains a separate authorized workflow. Inference remains a separate provider integration. Vultr compute provisioning and promotional capacity are outside scope.

## DoE design

Experiment `DOE-VULTR-CATALOG-001` version `3.0.0` compares Incumbent v6.0.0 with VultrInspired v2.0.0. Factors cover catalogue variant, population source, evidence class, task family, record quality and price representation. Both variants consume the same source-hash-bound population manifest.

Responses measure full-pool identity coverage, provider/model candidate coverage, semantic preservation, modality/capability coverage, source provenance, evidence-class preservation, deduplication/alias correctness, tournament stratum coverage and resource footprint. The 7,341 historical Actions-verified endpoint floor and 9,588 enumerated g4f candidate pairs remain separate measures. The Python and TypeScript upstream projects remain immutable design references; Incumbent and VultrInspired are the local variants.

## Invariants

- Catalog presence, pricing, access, entitlement, quota, readiness, health and inference success remain separate evidence classes.
- Missing readiness or entitlement remains unknown.
- The incumbent remains authoritative until a separately reviewed promotion.
- VultrInspired v1 has evaluation-only authority; provider activation, routing, quota mutation and inference follow separate gates.
- Each design change increments the DoE version; each run binds source, fixture and implementation revisions.

## Acceptance

- Unit tests prove deterministic offline projection, exact string/integer price preservation, float precision diagnostics, unknown-field preservation and malformed-row isolation.
- Registry tests prove the two local variants and separate immutable upstream reference pins.
- Paired fixture runs publish measurements and artifact references only after reproducible execution.
- Same-head repo gate, Termux smoke and independent review govern promotion.

## Full-pool population

Run `scripts/provider_catalog_population.py` to reconcile `ops/quota/registry.json`, `ops/challenge/desk-feed.json`, `data/g4f-working/providers.json` and `data/g4f-working/universe.json`. The 9,588 pairs comprise 5,347 upstream-only, 1,156 fork-only and 3,085 overlapping pairs. Then pass `population-v1.json` to `scripts.provider_catalog_competition --population-input`. All candidates seed the tournament population; task-specific execution still requires the existing manager/router/admission path.

## Deferred

Source-native provider adapters that retain exact decimal strings before incumbent float conversion; richer modality/capability extraction; raw payload snapshots and cache freshness; full fixture families and model-kind predicates.
