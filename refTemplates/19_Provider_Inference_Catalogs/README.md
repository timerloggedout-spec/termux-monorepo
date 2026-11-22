# Provider Inference Catalog References

Metadata-first reference pair for provider model-catalog ingestion and cross-language normalization.

| Reference | Language/runtime | Pinned source |
|---|---|---|
| [vultr-model-catalog-python](vultr-model-catalog-python/README.md) | Python 3.11+ | [4a414ab](https://github.com/vultr/model-catalog-python/tree/4a414ab26e1f596cb98b3974a7d12182bf62dab3) |
| [vultr-model-catalog-typescript](vultr-model-catalog-typescript/README.md) | Node 20+ / Bun | [6e55057](https://github.com/vultr/model-catalog-typescript/tree/6e55057cb718213937c4c118271f5a2ca1779d0d) |

## Shared architecture

Both libraries consume Vultr Inference's public `GET /v1/models` endpoint and normalize its OpenRouter Provider Model Document 2.4 entries into equivalent catalog records. They share language-neutral fixtures and normalized outputs.

The reference is useful for:
- lossless input/output modality records;
- exact decimal pricing strings and explicit pricing units;
- tool, structured-output, streaming and reasoning metadata;
- per-entry parser issues and forward-compatible unknown fields;
- raw-payload cache with freshness/source classification;
- Python/TypeScript semantic parity fixtures.

## Disposition

**Research-only · metadata-only · MIT-licensed upstreams.**

The pinned repositories inform the monorepo's provider catalog design. This slot records source identity and architectural evidence; package installation, upstream execution, custom forks, gitlinks, provider activation and inference remain separate decisions.

DoE experiment design and immutable variant pins: [DOE-REGISTRY.json](DOE-REGISTRY.json). The current experiment is version `1.0.0`, status `planned`; Python and TypeScript variants are independently pinned, and the registry records controlled factors, response variables, acceptance criteria and immutable run keys. Execution results remain empty until reproducible runs are performed.

Comparative analysis: [Vultr Inference Catalog Reference RECON](../../docs/ops/VULTR-INFERENCE-CATALOG-REFERENCE-RECON.md).
