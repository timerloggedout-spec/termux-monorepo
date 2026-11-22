# Provider Inference Catalog References

This slot contains two different asset classes: local competing catalogues and equivalent upstream design references.

## Local catalogue implementations

| Catalogue | Version | Implementation | Role |
|---|---:|---|---|
| Incumbent | 5.0.0 | [scripts/provider_model_catalog.py](../../../scripts/provider_model_catalog.py) | Existing multi-provider collector and v5 evidence contract |
| VultrInspired | 1.0.0 | [scripts/provider_model_catalog_vultr_inspired.py](../../../scripts/provider_model_catalog_vultr_inspired.py) | Native loss-aware offline projection over incumbent v5 records |

VultrInspired uses the existing local Python runtime and standard library. Its execution profile is zero credentials, zero network requests and zero inference calls. It serves as an evaluation candidate, with runtime replacement and routing authority governed separately. Populate both catalogue files from one supplied v5 snapshot with `python3 -m scripts.provider_catalog_competition --input /path/to/incumbent-v5.json --output-dir /path/to/catalogues`; the runner writes `incumbent-v5.json`, `vultr-inspired-v1.json` and a digest-bound `manifest.json`.

## Upstream design references

| Reference | Pinned source | Intended use |
|---|---|---|
| [vultr-model-catalog-python](vultr-model-catalog-python/README.md) | [4a414ab](https://github.com/vultr/model-catalog-python/tree/4a414ab26e1f596cb98b3974a7d12182bf62dab3) | Schema, normalization, parser and cache design reference |
| [vultr-model-catalog-typescript](vultr-model-catalog-typescript/README.md) | [6e55057](https://github.com/vultr/model-catalog-typescript/tree/6e55057cb718213937c4c118271f5a2ca1779d0d) | Equivalent cross-language design reference |

The upstream projects describe equivalent patterns over Vultr's public model-list catalog. Their parity supports one local adaptation; the pinned projects remain provenance references.

Transferable patterns include exact decimal pricing, modality-aware input/output descriptors, tool and structured-output metadata, reasoning and parameter descriptors, per-record diagnostics, unknown-field preservation, source/freshness provenance and shared fixtures.

## Compute and provider boundary

- Local comparison: existing Python runtime; offline fixture input.
- Live catalogue observation: a separately authorized provider endpoint and network path.
- Inference: a separately configured and authorized inference provider.
- Vultr compute provisioning, Vultr credentials, Vultr inference and promotional capacity: outside this integration.

Catalog presence, readiness, account entitlement, quota, health and successful inference remain separate evidence classes.

## DoE

[DOE-REGISTRY.json](DOE-REGISTRY.json) records `DOE-VULTR-CATALOG-001` version `2.0.0`, comparing Incumbent v5 with VultrInspired v1.0.0. The two Vultr repositories are pinned under `source_references`, separately from experiment variants. Status is `planned`; result artifacts remain empty pending deterministic paired runs.

Comparative analysis: [Vultr Inference Catalog Reference RECON](../../docs/ops/VULTR-INFERENCE-CATALOG-REFERENCE-RECON.md).
