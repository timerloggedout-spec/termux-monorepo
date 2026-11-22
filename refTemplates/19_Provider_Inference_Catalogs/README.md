# Provider Inference Catalog References

This slot contains two different asset classes:

1. **Local competing catalogues:** `Incumbent` (existing provider-model-catalog/v5) and `VultrInspired` (our native offline projection).
2. **Upstream design references:** pinned Vultr Python and TypeScript projects. They are equivalent reference implementations, not two catalogue variants in our experiment.

## Local catalogue implementations

| Catalogue | Version | Implementation | Role |
|---|---:|---|---|
| Incumbent | 5.0.0 | [scripts/provider_model_catalog.py](../../../scripts/provider_model_catalog.py) | Existing multi-provider collector and v5 evidence contract |
| VultrInspired | 1.0.0 | [scripts/provider_model_catalog_vultr_inspired.py](../../../scripts/provider_model_catalog_vultr_inspired.py) | Native loss-aware projection over incumbent v5 records |

VultrInspired currently runs as a pure local Python transformation over an incumbent v5 document. It uses the standard library, requires no credentials, makes zero network requests and makes zero inference calls. It is an evaluation candidate, not a runtime replacement or routing authority.

## Upstream design references

| Reference | Pinned source | Intended use |
|---|---|---|
| [vultr-model-catalog-python](vultr-model-catalog-python/README.md) | [4a414ab](https://github.com/vultr/model-catalog-python/tree/4a414ab26e1f596cb98b3974a7d12182bf62dab3) | Schema, normalization, parser and cache design reference |
| [vultr-model-catalog-typescript](vultr-model-catalog-typescript/README.md) | [6e55057](https://github.com/vultr/model-catalog-typescript/tree/6e55057cb718213937c4c118271f5a2ca1779d0d) | Equivalent cross-language design reference |

The upstream projects expose equivalent patterns over Vultr's public `GET /v1/models` catalog. Their parity is a reason to consolidate their lessons into one local adaptation, rather than execute both or treat them as competing implementations.

Transferable patterns include exact decimal pricing, modality-aware input/output descriptors, tools and structured-output metadata, reasoning and parameter descriptors, per-record diagnostics, unknown-field preservation, source/freshness provenance, and shared fixtures.

## Compute and provider boundary

- Local comparison: existing Python runtime; offline fixture input.
- Live catalogue observation: a separately authorized provider endpoint and network path.
- Inference: a separately configured and authorized inference provider.
- Vultr compute provisioning, Vultr credentials, Vultr inference and promotional capacity: outside this integration.

A catalog record proves only the source fact represented by that record. Readiness, account entitlement, quota, health and successful inference remain separate evidence.

## DoE

[DOE-REGISTRY.json](DOE-REGISTRY.json) records `DOE-VULTR-CATALOG-001` version `2.0.0`, comparing Incumbent v5 with VultrInspired v1.0.0. The two Vultr repositories remain pinned under `source_references`, not as experiment variants. Status is `planned`; result artifacts remain empty until deterministic paired runs are executed and recorded.

Comparative analysis: [Vultr Inference Catalog Reference RECON](../../docs/ops/VULTR-INFERENCE-CATALOG-REFERENCE-RECON.md).
