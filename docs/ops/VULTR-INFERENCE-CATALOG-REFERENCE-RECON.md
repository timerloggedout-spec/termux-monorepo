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
| Incumbent | 5.0.0 | `scripts/provider_model_catalog.py` | Existing provider collector; live polling only through its existing separately configured workflow/runtime |
| VultrInspired | 1.0.0 | `scripts/provider_model_catalog_vultr_inspired.py` | Pure local projection over an incumbent v5 document; offline, standard library only |

The Vultr Python and TypeScript repositories are equivalent upstream references. They inform schema, parser, cache, capability and fixture design. They are not our competing implementations, installed modules, runtime dependencies or execution targets. Their full immutable revisions remain in the DoE source-reference list.

## Existing incumbent contract

The incumbent is `provider-model-catalog/v5`. Its collector is `scripts/provider_model_catalog.py`; provider-specific wire normalization lives in `scripts/provider_catalog_protocols.py` and `scripts/provider_extension_catalogs.py`. It already separates catalog observations, price classification, access claims, documented entitlements, credential presence, quota evidence and inference outcomes.

Current v5 records include provider/model identity, pricing, pricing/access classification, access provenance, entitlement verification, cadence, free suffix, context/output limits, selected capabilities, active state and raw-source label. The collector writes its normalized document atomically.

Known incumbent limitations retained as evaluation targets: pricing classification uses binary floats; some extension normalizers convert rates to numbers; modality/capability representation is provider-specific; normalized output lacks a complete raw-payload snapshot; model-level issue diagnostics are limited.

## VultrInspired v1.0.0

The local implementation is authored for this repository. It accepts an incumbent v5 document and emits `provider-model-catalog/vultr-inspired/v1`. The first projection provides:

- a versioned, structured record with limits, input/output modalities and capability groups;
- source pricing values plus exact decimal strings for string/integer inputs;
- explicit lifecycle readiness (`null` when the incumbent record has no boolean active value);
- separate access/entitlement evidence and source provenance;
- preservation of the full incumbent row and unrecognized extension fields;
- indexed diagnostics for malformed rows and non-exact numeric pricing values.

The projection deliberately exposes float-origin prices as precision-limited diagnostics. It cannot reconstruct original decimal text after an upstream incumbent transformation has converted that value to a binary float. Later iterations should move exact pricing preservation into the provider-specific wire adapters before classification.

VultrInspired v1 is an additive projection, not a drop-in replacement. It does not change incumbent collection, provider routing, model admission, quota policy, credential handling or inference.

## Upstream reference pair

| Repository | Pinned revision | Role |
|---|---|---|
| [vultr/model-catalog-python](https://github.com/vultr/model-catalog-python) | `4a414ab26e1f596cb98b3974a7d12182bf62dab3` | Python implementation used to study normalization and cache patterns |
| [vultr/model-catalog-typescript](https://github.com/vultr/model-catalog-typescript) | `6e55057cb718213937c4c118271f5a2ca1779d0d` | Equivalent TypeScript reference and parity evidence |

Both projects describe the same Vultr Inference model-list surface and shared normalized contract. Their parity means we should transfer the common design once into our own architecture. The references are pinned for traceability; no package import, submodule, fork, vendored runtime or upstream execution is introduced.

## Compute and network boundary

| Activity | Required resources | Current status |
|---|---|---|
| Incumbent vs VultrInspired fixture comparison | Existing local Python runtime; CPU/RAM proportional to fixture size | Available as offline test work |
| Vultr reference inspection | GitHub source metadata and documentation | Completed as research |
| Live catalogue refresh | Network access to an explicitly supported provider catalog endpoint | Separate observation workflow; excluded from this DoE run |
| Model inference | Authorized provider inference endpoint, credentials and quota | Disabled; outside this task |
| Vultr compute provisioning | Vultr compute API/account access | Not used or configured |

No Vultr compute instance is provisioned or required. The local projection performs no HTTP request, credential lookup or inference call. Vultr promotional compute capacity and any hackathon promo-code status have no bearing on this offline comparison.

## DoE v2.0.0

`refTemplates/19_Provider_Inference_Catalogs/DOE-REGISTRY.json` now defines Incumbent v5 and VultrInspired v1 as the two experiment variants. The Python and TypeScript Vultr repositories are stored as `source_references`, not variants.

Factors include catalogue variant, fixture family, record quality and price representation. Controls require byte-identical incumbent input rows and timestamps. Responses measure semantic preservation, exact price retention, modality/capability coverage, unknown-field retention, diagnostics, provenance, evidence-boundary preservation and resource footprint.

Execution policy is offline deterministic; network, credentials and inference are disabled. Results remain `planned` with an empty artifact list until paired fixtures run against pinned implementation revisions.

## Next implementation sequence

1. Expand the fixture set across chat, embeddings, rerank, image, audio, video, tools, structured output and reasoning.
2. Add a source-native adapter stage that captures exact provider decimal strings before incumbent float classification.
3. Add modality and capability extraction to provider-specific adapters while retaining raw provider extensions.
4. Add deterministic replay and explicit freshness/cache provenance only where a supported local snapshot contract exists.
5. Run paired DoE fixtures and publish measurements bound to immutable implementation and fixture revisions.

Each increment receives its own DoE version and remains evaluation-only until separately reviewed and accepted.

## Safety and policy invariants

- Catalog presence, credentials, entitlement, quota, readiness, health and inference success remain separate facts.
- Missing readiness and entitlement remain unknown.
- Provider-specific wire contracts remain behind their existing adapters.
- Catalog evaluation has zero authority to activate providers, change routing weights, retry paid routes or issue inference calls.
- Promotion requires separate review and same-commit validation.

## Related sources

- [Provider capability registry](../schemas/provider-capabilities.md)
- [Provider batch implementation](PROVIDER-BATCH-IMPLEMENTATION.md)
- [Provider routing governance](../icm/objects/knowledge/provider-routing.md)
- [Catalogue reference slot and DoE registry](../../refTemplates/19_Provider_Inference_Catalogs/README.md)
