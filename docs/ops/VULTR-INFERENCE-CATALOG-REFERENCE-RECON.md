# Provider Catalog Competition: Incumbent vs VultrInspired

**Date:** 2026-11-22  
**Proposal item:** MSM-025  
**DoE:** DOE-VULTR-CATALOG-001 v2.0.0  
**Disposition:** native adaptation prototype + pinned upstream design references  
**Runtime state:** Incumbent remains authoritative; VultrInspired is offline evaluation-only.

## Decision

Compare two repository-owned catalogue versions:

| Catalogue | Version | Code | Execution |
|---|---:|---|---|
| Incumbent | 5.0.0 | `scripts/provider_model_catalog.py` | Existing multi-provider collector; live polling remains in its separately configured workflow/runtime |
| VultrInspired | 1.0.0 | `scripts/provider_model_catalog_vultr_inspired.py` | Pure local projection over an incumbent v5 document; offline, standard library only |

The Vultr Python and TypeScript repositories are equivalent upstream references. They inform schema, parser, cache, capability and fixture design. They are not our competing implementations, installed modules, runtime dependencies or execution targets. Their immutable revisions remain in DoE source-reference metadata.

## Incumbent contract

The incumbent is `provider-model-catalog/v5`. Provider-specific wire normalization lives in `scripts/provider_catalog_protocols.py` and `scripts/provider_extension_catalogs.py`. The collector separates catalog observations, price classification, access claims, documented entitlements, credential presence, quota evidence and inference outcomes.

Current v5 records include provider/model identity, pricing, pricing/access classification, access provenance, entitlement verification, cadence, free suffix, context/output limits, selected capabilities, active state and raw-source label. The collector writes normalized output atomically.

Known incumbent limitations include binary-float pricing classification, numeric conversion in some extension adapters, provider-specific modality/capability fragments, absence of a complete raw-payload snapshot and limited model-level issue diagnostics.

## VultrInspired v1.0.0

The local implementation accepts an incumbent v5 document and emits `provider-model-catalog/vultr-inspired/v1`. Run it with `python3 -m scripts.provider_model_catalog_vultr_inspired --input <incumbent-v5.json> --output <vultr-inspired-v1.json>`. It adds structured limits, input/output modalities, capability groups, exact decimal strings for string/integer price inputs, explicit unknown readiness, separate access/entitlement evidence, provenance, unknown-field preservation and indexed diagnostics for malformed rows.

Float-origin prices are marked as precision-limited. The projection cannot reconstruct decimal text after an incumbent adapter has already converted a source value to binary float. Source-native exact-price capture belongs in a later adapter increment.

VultrInspired is additive and evaluation-only. It does not change incumbent collection, routing, model admission, quota policy, credential handling or inference.

## Upstream references

| Repository | Pinned revision | Role |
|---|---|---|
| [vultr/model-catalog-python](https://github.com/vultr/model-catalog-python) | `4a414ab26e1f596cb98b3974a7d12182bf62dab3` | Python normalization/cache/schema reference |
| [vultr/model-catalog-typescript](https://github.com/vultr/model-catalog-typescript) | `6e55057cb718213937c4c118271f5a2ca1779d0d` | Equivalent TypeScript reference and parity evidence |

Both upstream projects describe equivalent libraries and normalized contracts. Transfer their shared patterns once into our native architecture. Keep the upstream source pins for provenance; introduce no package import, submodule, fork, vendored runtime or upstream execution.

## Compute and network boundary

| Activity | Required resources | Status |
|---|---|---|
| Incumbent vs VultrInspired fixture comparison | Existing local Python runtime; CPU/RAM proportional to fixture size | Offline local tests |
| Vultr reference inspection | GitHub source metadata and documentation | Research complete |
| Live catalogue refresh | Network access to an explicitly supported provider endpoint | Separate observation workflow |
| Model inference | Authorized provider endpoint, credentials and quota | Disabled; outside scope |
| Vultr compute provisioning | Vultr compute API/account access | Not used or configured |

No Vultr compute instance is provisioned or required. The local projection performs no HTTP request, credential lookup or inference call. Vultr promotional compute capacity and hackathon promo-code status have no bearing on this offline comparison.

## DoE v2.0.0

The registry compares Incumbent v5.0.0 with VultrInspired v1.0.0. The two Vultr repositories are source references, not experiment variants. Factors include catalogue variant, fixture family, record quality and price representation. Controls use identical incumbent v5 input rows and timestamps.

Responses measure semantic preservation, exact price visibility, modality/capability coverage, unknown-field retention, diagnostics, provenance, evidence-boundary preservation and resource footprint. Execution is offline deterministic; network, credentials and inference are disabled. Results remain planned with no artifacts until paired runs complete.

## Next implementation sequence

1. Expand fixtures across chat, embedding, rerank, image, audio, video, tools, structured output and reasoning.
2. Add source-native adapter stages that capture exact provider decimal strings before incumbent float classification.
3. Add modality and capability extraction to provider-specific adapters while retaining raw provider extensions.
4. Add deterministic replay and explicit cache freshness only where a supported local snapshot contract exists.
5. Run paired DoE fixtures and publish measurements bound to immutable implementation and fixture revisions.

Each increment receives its own DoE version and remains evaluation-only until separately reviewed and accepted.

## Invariants

- Catalog presence, credentials, entitlement, quota, readiness, health and inference success remain separate facts.
- Missing readiness and entitlement remain unknown.
- Provider-specific wire contracts remain behind existing adapters.
- Catalog evaluation cannot activate providers, change routing weights, retry paid routes or issue inference calls.
- Promotion requires separate review and same-commit validation.

## Related sources

- [Provider capability registry](../schemas/provider-capabilities.md)
- [Provider batch implementation](PROVIDER-BATCH-IMPLEMENTATION.md)
- [Provider routing governance](../icm/objects/knowledge/provider-routing.md)
- [Catalogue reference slot and DoE registry](../../refTemplates/19_Provider_Inference_Catalogs/README.md)
