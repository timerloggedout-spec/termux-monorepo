# Provider Inference Catalog References

This slot tracks the repository-owned catalogue variants, the full provider/model candidate population, and equivalent upstream design references.

## Local catalogue implementations

| Catalogue | Version | Implementation | Role |
|---|---:|---|---|
| Incumbent | 6.0.0 | `scripts/provider_catalog_population.py` + existing v5 observation collector | Full-pool source-preserving baseline; v5 is one observation layer |
| VultrInspired | 2.0.0 | `scripts/provider_model_catalog_vultr_inspired.py` | Native loss-aware projection over the complete population |

VultrInspired uses the existing local Python runtime and standard library. Population compilation and projection perform zero network requests, credential reads and inference calls. The full pool comes from canonical repository registries and g4f datasets; the live adapter roster does not define the population boundary.

## Full-pool population and tournament seeding

See [Full Provider/Model Pool Population](../../docs/ops/PROVIDER-CATALOG-POPULATION.md).

```bash
python3 scripts/provider_catalog_population.py --output-dir /tmp/provider-population
python3 -m scripts.provider_catalog_competition \
  --population-input /tmp/provider-population/population-v1.json \
  --output-dir /tmp/provider-tournament
```

The first command reconciles the 172-record/118-provider service registry, the 91-record/89-provider model-lane bench, the 60-provider g4f working catalog and the 160-provider/9,588-pair g4f universe. The second emits both full-pool variants and a digest-bound manifest.

## Incumbent v5 observation layer

The incumbent collector remains the existing networked observation path. Within its separately authorized workflow, it writes a v5 snapshot using configured provider endpoints and environment credentials:

```bash
python3 scripts/provider_model_catalog.py --output /tmp/model-catalog/catalog.json
python3 -m scripts.provider_catalog_competition \
  --input /tmp/model-catalog/catalog.json \
  --output-dir /tmp/model-catalog/competition
```

This legacy paired projection remains available for focused v5 regression comparisons. It does not replace full-pool population or tournament seeding.

## Upstream design references

| Reference | Pinned source | Intended use |
|---|---|---|
| [vultr-model-catalog-python](vultr-model-catalog-python/README.md) | [4a414ab](https://github.com/vultr/model-catalog-python/tree/4a414ab26e1f596cb98b3974a7d12182bf62dab3) | Schema, normalization, parser and cache design reference |
| [vultr-model-catalog-typescript](vultr-model-catalog-typescript/README.md) | [6e55057](https://github.com/vultr/model-catalog-typescript/tree/6e55057cb718213937c4c118271f5a2ca1779d0d) | Equivalent cross-language design reference |

The upstream projects describe equivalent patterns over Vultr's public model-list catalog. Their parity supports one local adaptation; the pinned projects remain provenance references. Transferable patterns include exact decimal pricing, modality-aware descriptors, tool and structured-output metadata, reasoning and parameter descriptors, per-record diagnostics, unknown-field preservation, source/freshness provenance and shared fixtures.

## Compute and provider boundary

- Local population and comparison: existing Python runtime; deterministic file I/O.
- Live catalogue observation: separately authorized provider endpoints and network path.
- Inference: separately configured provider, task-specific admission, entitlement and quota.
- Vultr compute provisioning, credentials, inference and promotional capacity: outside this integration.

Candidate presence, reported working entries, catalog observations, readiness, entitlement, quota, health and successful inference remain distinct evidence classes.

## DoE

[DOE-REGISTRY.json](DOE-REGISTRY.json) records `DOE-VULTR-CATALOG-001` version `3.0.0`. It compares Incumbent v6.0.0 with VultrInspired v2.0.0 over the full candidate pool. The 7,341 historical Actions-verified endpoint floor and 9,588 enumerated g4f candidate pairs remain separate populations. Status is `planned`; result artifacts remain empty pending reproducible paired runs and task receipts.
