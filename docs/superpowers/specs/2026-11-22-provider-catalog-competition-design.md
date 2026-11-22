# Provider Catalog Competition — Design v2

**Date:** 2026-11-22  
**Proposal:** MSM-025  
**DoE:** DOE-VULTR-CATALOG-001 v2.0.0

## Goal

Build and compare two repository-owned catalogue variants: the incumbent multi-provider `provider-model-catalog/v5` and a native `VultrInspired` projection. Use the pinned Vultr Python and TypeScript repositories as equivalent design references only.

## Architecture

- Incumbent v5 remains the source collector and current evidence contract.
- VultrInspired v1 is implemented in `scripts/provider_model_catalog_vultr_inspired.py` as a pure offline projection over incumbent v5 documents.
- Vultr Python and TypeScript pins live in reference metadata and the DoE `source_references` list; local execution uses repository-owned code.
- The projection preserves the incumbent record and adds structured limits, modalities, capability groups, pricing provenance, lifecycle, access evidence, extensions and per-row diagnostics.
- Provider-specific wire protocols remain in their existing adapter modules.

## Compute and side-effect contract

Local fixture comparison uses the repository's existing Python runtime and ordinary local CPU/RAM. The projection performs zero HTTP requests, zero credential lookups and zero inference calls. Live catalogue observation remains a separate authorized workflow. Inference remains a separate provider integration. Vultr compute provisioning and promotional capacity are outside scope.

## DoE design

Experiment `DOE-VULTR-CATALOG-001` version `2.0.0` compares `Incumbent` v5.0.0 with `VultrInspired` v1.0.0. Factors cover catalogue variant, fixture family, record quality and price representation. Paired trials use identical incumbent v5 input documents, model rows and timestamps.

Responses measure semantic preservation, exact decimal visibility, modality/capability coverage, unknown-field retention, malformed-row diagnostics, provenance, evidence-boundary preservation and resource footprint. The Python and TypeScript upstream projects remain immutable design references; Incumbent and VultrInspired are the local variants.

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

## Deferred

Source-native provider adapters that retain exact decimal strings before incumbent float conversion; richer modality/capability extraction; raw payload snapshots and cache freshness; full fixture families and model-kind predicates.
