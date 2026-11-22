# Vultr Inference Catalog Reference RECON

**Date:** 2026-11-21  
**Proposal item:** MSM-025  
**Disposition:** reference registration + architecture analysis  
**Runtime state:** existing provider catalog and routing remain unchanged

## Executive finding

Vultr's Python and TypeScript repositories provide a useful reference for a **loss-aware, modality-aware model catalog with deterministic cross-language normalization**. Their strongest transferable ideas are exact pricing, structured input/output modalities, field-level capability descriptors, tolerant per-entry parsing, last-known-good raw-payload caching and shared golden fixtures.

The monorepo already has the more important multi-provider policy boundary: catalog observations, credential presence, pricing classification, documented entitlement, quota evidence and inference outcomes are separate. Preserve that architecture. Adopt Vultr's model-description depth inside provider-specific adapters and a versioned common projection; keep the existing provider wire contracts distinct.

## 1. Source identity and inspection

| Repository | Default branch | Inspected revision | License evidence | Runtime |
|---|---|---|---|---|
| [vultr/model-catalog-python](https://github.com/vultr/model-catalog-python) | `main` | [`4a414ab26e1f596cb98b3974a7d12182bf62dab3`](https://github.com/vultr/model-catalog-python/tree/4a414ab26e1f596cb98b3974a7d12182bf62dab3) | [MIT LICENSE](https://github.com/vultr/model-catalog-python/blob/4a414ab26e1f596cb98b3974a7d12182bf62dab3/LICENSE) | Python 3.11+ |
| [vultr/model-catalog-typescript](https://github.com/vultr/model-catalog-typescript) | `main` | [`6e55057cb718213937c4c118271f5a2ca1779d0d`](https://github.com/vultr/model-catalog-typescript/tree/6e55057cb718213937c4c118271f5a2ca1779d0d) | [MIT LICENSE](https://github.com/vultr/model-catalog-typescript/blob/6e55057cb718213937c4c118271f5a2ca1779d0d/LICENSE) | Node 20+ / Bun |

Both repositories describe equivalent libraries over Vultr Inference's public `GET /v1/models` endpoint. The endpoint returns an OpenRouter Provider Model Document 2.4 envelope. The projects publish zero runtime dependencies and share fixtures; the TypeScript project generates normalized fixtures and the Python project consumes the same expected documents.

Primary source files:
- [Python catalog transport/cache](https://github.com/vultr/model-catalog-python/blob/4a414ab26e1f596cb98b3974a7d12182bf62dab3/src/vultr_model_catalog/catalog.py)
- [Python model normalization](https://github.com/vultr/model-catalog-python/blob/4a414ab26e1f596cb98b3974a7d12182bf62dab3/src/vultr_model_catalog/model.py)
- [Python tolerant parser](https://github.com/vultr/model-catalog-python/blob/4a414ab26e1f596cb98b3974a7d12182bf62dab3/src/vultr_model_catalog/parse.py)
- [Vultr catalog contract](https://github.com/vultr/model-catalog-python/blob/4a414ab26e1f596cb98b3974a7d12182bf62dab3/docs/catalog.md)
- [TypeScript catalog transport/cache](https://github.com/vultr/model-catalog-typescript/blob/6e55057cb718213937c4c118271f5a2ca1779d0d/src/catalog.ts)
- [TypeScript model normalization](https://github.com/vultr/model-catalog-typescript/blob/6e55057cb718213937c4c118271f5a2ca1779d0d/src/model.ts)
- [TypeScript tolerant parser](https://github.com/vultr/model-catalog-typescript/blob/6e55057cb718213937c4c118271f5a2ca1779d0d/src/parse.ts)

## 2. What Vultr implements

### 2.1 Rich canonical model record

The normalized model includes:
- provider model identity, name, description, creation and deprecation data;
- context, prompt and output limits;
- ordered input and output modality lists;
- modality-specific `inputs` and `outputs` retaining source descriptors;
- prompt, cached-prompt, cache-write, completion, internal-reasoning and request prices;
- tool support, structured outputs, streaming and supported parameters;
- reasoning effort, default state and max-token support;
- readiness and helper predicates for chat and agent models.

The modality records preserve information that a chat-only flat row would discard. Image sizes, video durations, speech voices, input constraints and modality-specific prices remain reachable from the normalized model.

### 2.2 Exact pricing

Pricing is represented as decimal strings in USD per token or per request. The `usd_per_million` helper shifts the decimal point rather than multiplying binary floating-point values. Windowed rates are distinguished from base rates through explicit UTC-window fields.

### 2.3 Parser tolerance and forward compatibility

The parser accepts the documented envelope or a bare list. Its entry-level checks validate model identity and modality-list structure; an unexpected schema version is surfaced as an issue while parsing continues. Unknown fields and modality types pass through. These checks do not validate every nested field: for example, a text entry with a string-valued `supported_inputs` can pass parsing, then raise `AttributeError` during Python model normalization and prevent valid sibling entries from being returned. Treat parser tolerance as partial structural validation rather than a guarantee that every malformed row is isolated.

### 2.4 Cache and partial-source resilience

The main cache stores the raw payload together with `base_url` and `fetched_at`. The load result identifies `network`, `cache` or `stale-cache`. Fresh cache, network, stale cache and terminal error have explicit precedence.

The optional media catalog polls multiple public surfaces (public model metadata, image, video, music and per-model speech voices). A partial source failure is retained as an issue while successful sources remain usable. A media cache is replaced only after a complete successful source set.

### 2.5 Cross-language contract

Python and TypeScript expose language-appropriate APIs while emitting a common snake_case document. Shared normalized fixtures pin semantic equivalence. The test suites exercise transport headers, timeout/error mapping, cache freshness, stale fallback, malformed payloads, normalization and fixture parity.

## 3. Existing monorepo baseline

The owning implementation is `scripts/provider_model_catalog.py`, with output schema `provider-model-catalog/v5`.

Existing responsibilities:
- `ENDPOINTS` and `SECRETS` map canonical provider families to their model-list sources and secret names.
- `provider_catalog_protocols.py` and `provider_extension_catalogs.py` own provider-specific wire normalization.
- `provider_model_catalog.py` records model rows and provider observations.
- `provider_quota_managers.py` interprets supported quota evidence.
- `tests/test_provider_model_catalog.py` covers secret alias precedence, price classification, transport, provider-specific model shapes, pagination, malformed responses, redirects, deduplication and provider endpoint identities.

The v5 document already records:
- catalog observation time and provider list;
- per-provider response headers and credential environment-variable **name**;
- catalog authentication mode and contract-source classification;
- documented entitlement claims and verification state;
- quota-manager output and a quota-evidence note;
- model rows with provider/id/name, pricing, pricing/access classifications, access source, entitlement verification, cadence, free suffix, context length, output limit, selected capabilities, active state and raw-source label;
- provider-scoped errors.

The current design already preserves a critical distinction:

**Catalog discovery, credential presence, account entitlement, quota, health and successful inference are separate evidence classes.**

### Current gaps relative to the reference

| Dimension | Current v5 posture | Vultr reference | Opportunity |
|---|---|---|---|
| Context/output limits | Core fields | Context, prompt and per-output limits | Add source-backed prompt and modality limits |
| Modalities | Provider-specific capability fragments | Ordered input/output modality records | Normalize modality-aware input/output specs |
| Tooling/reasoning | Selected provider-specific capabilities | Tools, structured output, streaming, reasoning and parameter descriptors | Add explicit, typed capability descriptors |
| Pricing | Raw source shape for many providers; float classification; some extension adapters normalize rates numerically | Exact decimal strings and explicit units | Preserve exact decimal rates through every adapter |
| Entry failures | Invalid list shape or invalid model identity can fail a provider poll | Per-entry issue isolation | Quarantine malformed rows and retain valid siblings |
| Raw source | Source label and observation metadata | Raw payload cache with source endpoint and fetch time | Retain a content-addressed raw payload snapshot or artifact |
| Cache state | Atomic normalized output write | Fresh cache/network/stale-cache states | Add explicit last-known-good freshness states |
| Cross-language parity | Python canonical collector and provider-specific adapters | Shared Python/TypeScript golden fixtures | Establish one language-neutral adapter fixture contract |
| Lifecycle | Readiness/active fields vary by provider | Ready and deprecation metadata | Normalize lifecycle with explicit unknown state |

A precision detail: the core collector retains provider pricing objects for several native paths, while its classification helper parses prompt/completion values as floats. The extension adapter normalizer also converts some rates to numeric values. An exact-decimal contract should preserve original decimal text and use decimal-safe classification throughout, rather than relying on binary float representations.

A resilience detail: the collector writes its normalized output atomically. The current output document stores the normalized view; a complete raw provider response remains unavailable for later re-normalization. Its provider-level error list also needs a normalized per-model issue collection.

## 4. What to adopt — prioritized recommendations

### P0 — preserve exact pricing and provenance

1. Preserve every advertised price as an exact decimal string with explicit currency, unit, modality, price kind and any time window.
2. Perform free/paid classification with decimal-safe arithmetic. Keep unknown, malformed and incomplete price data distinct from zero.
3. Add source provenance to normalized records: provider endpoint, source contract/version, observation timestamp, payload digest, adapter/normalizer version and field evidence.
4. Keep price classification separate from account entitlement and remaining quota.

**Acceptance evidence:** provider fixtures for tiny non-zero prices, scientific notation, missing fields, booleans, invalid decimal strings, multi-tier pricing, request prices and modality-specific rates. Tests prove that non-zero prices remain non-zero through normalization.

### P1 — modality-aware capability contract

Add an additive, versioned projection for:
- input/output modality lists;
- supported input formats, sources, roles, size limits and length units;
- output streaming, output limits, parameters and passthrough parameters;
- tool calling and structured output descriptors;
- reasoning support and supported effort values;
- model lifecycle, readiness and deprecation metadata.

Use provider adapters to map each provider's documented wire shape into this projection. Keep the raw provider schema and provider-specific extensions accessible.

**Acceptance evidence:** source fixtures for text, embedding, rerank, image, audio/transcription, video and decision models; unknown modality and unknown parameter fixtures; explicit null/unknown semantics.

### P1 — tolerant model-level diagnostics

Retain provider-level failure for malformed envelopes, transport errors and unusable catalog documents. For an individual malformed model row, record a structured issue with source index, model identity when available, reason and adapter version, then continue with valid siblings.

**Acceptance evidence:** one fixture with valid, malformed and unknown-field model rows. Valid siblings survive; every excluded row has a diagnostic; a malformed top-level envelope remains a provider failure.

### P1 — raw snapshots and last-known-good state

Preserve a content-addressed raw response snapshot with endpoint identity, observation time, response status, safe headers and digest. Keep normalized output as a derived view so later normalizer versions can replay prior source data.

Expose `network`, `cache`, `stale-cache`, `error` and `unknown` as source/freshness states. A stale catalog remains visible as stale evidence; freshness policy controls eligibility separately.

**Acceptance evidence:** deterministic replay, same-endpoint cache validation, corrupt-cache rejection, empty-catalog handling, partial provider failure and stale-source classification.

### P2 — shared adapter fixtures and model-kind predicates

Use one language-neutral fixture format for each provider's wire response and canonical normalized output. Add predicates for task/model kinds (chat, agent, embedding, rerank, image, audio, video and decision) using explicit capability facts.

Keep task suitability separate from the broad model-kind predicate. For example, agent suitability requires separate tool capability, context and readiness evidence.

**Acceptance evidence:** identical normalized fixture output across any future Python/TypeScript adapters and regression tests for model-kind boundaries.

## 5. Adaptation rules for this monorepo

Vultr's implementation is a provider-specific catalog SDK for Vultr. Its Model Document 2.4 parser should inform the OpenRouter-compatible adapter path while other providers retain their own official wire schemas and protocol adapters.

Translate these details carefully:
- Vultr's `is_ready` defaults to true when absent. The monorepo should preserve unknown readiness when the provider omits the field.
- Vultr's public endpoint and optional API key are properties of Vultr's catalog. Credential handling remains provider-specific in the monorepo.
- A successful model-list request proves catalog reachability; inference health and entitlement require separate evidence.
- A model-level free price or `:free` suffix remains catalog pricing evidence; account quota and free inference authorization require separate evidence.
- Stale cache visibility must retain its stale state and freshness timestamp.
- Derive tool support and agent suitability from explicit capability facts rather than model names or marketing labels.

## 6. Proposed implementation sequence

| Order | Work | Result | Runtime impact |
|---|---|---|---|
| 1 | Design provider-model-catalog/v6 additive schema and v5 compatibility map | Reviewed schema and migration contract | None |
| 2 | Add exact-decimal pricing and field-provenance fixtures to existing adapters | Precision-safe normalized evidence | Catalog output only, behind its own item |
| 3 | Add modality/capability projection and per-model issue contract | Rich model description | Catalog output only, behind its own item |
| 4 | Add raw snapshot/cache replay and freshness states | Reproducible source history | Catalog collection behavior, separately gated |
| 5 | Add adapter parity and model-kind fixtures | Stable cross-provider semantics | Tests/evaluation only |

Each runtime slice needs its own accepted proposal item, test-first implementation, focused review and same-SHA dual-gate evidence. This RECON registers the references and records the design opportunity; runtime activation remains separately gated.

## 7. Loopy / feedback-cycle disposition

This task is a bounded one-shot reference capture and architecture comparison. The codebase already has two distinct observation surfaces:

- `.github/workflows/openrouter-free-catalog-sync.yml` runs daily at `17 12 * * *` and uploads immutable run-attempt artifacts with 14-day retention. Its contract is observation-only. The poller reads `/tmp/openrouter-free-catalog.json` before writing; each fresh runner starts without that file, and the missing-file path behaves as an empty prior snapshot. Consequently, the current run reports every current model ID as an addition rather than comparing with the preceding run. A durable prior-snapshot handoff is a prerequisite for meaningful cross-run deltas; artifact upload alone does not provide that handoff.
- `.github/workflows/provider-availability.yml` is `workflow_dispatch`-only in the inspected revision. Its cadence is owned by `quota-dispatch-tree.yml`; it records credential/catalog continuity and keeps routine inference disabled.
- `.github/workflows/provider-batch.yml` runs contract tests for relevant changes and exposes separate trusted manual observation inputs. Its inference smoke defaults off.

The strongest loop candidate is therefore an **observation-and-reconciliation loop** with a read-only source collector:

1. **Observe:** collect the scheduled public catalog snapshot and authorized provider-availability evidence with source, schema, observation time and digest.
2. **Choose:** compare the new snapshot with its predecessor; classify additions, removals, schema drift, stale cache and provider-level errors.
3. **Act:** create a scoped adapter/schema proposal only when the delta changes a documented capability or parser contract. The existing snapshot job remains read-only.
4. **Verify:** run provider fixtures, refTemplates inventory and provider-batch contracts against the exact candidate SHA.
5. **Record:** retain the source revision, payload digest, adapter version, run/attempt, test results and observed delta.
6. **Repeat or stop:** continue on the next existing observation cadence; finish each cycle as `success`, `clean no-op`, `blocked`, `approval-required`, `exhausted` or `stagnated`.

This is an adapted design grounded in the existing workflows. It reuses the existing cadence and keeps scheduler ownership, inference requests, publisher writes and routing authority unchanged.

## 8. Related repository sources

- [Provider capability registry](../schemas/provider-capabilities.md)
- [Provider batch implementation](PROVIDER-BATCH-IMPLEMENTATION.md)
- [Provider research compounding](PROVIDER-RESEARCH-COMPOUNDING.md)
- [Free LLM provider RECON](FREE-LLM-PROVIDER-RECON.md)
- [Provider dispatch capability](PROVIDER-DISPATCH-CAPABILITY.md)
- [Provider routing governance](../icm/objects/knowledge/provider-routing.md)
- [refTemplates workflow hooks](REFTEMPLATES-WORKFLOW-HOOKS.md)
- [MSM-025 design](../superpowers/specs/2026-11-21-vultr-inference-catalog-reference-design.md)
- [MSM-025 implementation plan](../superpowers/plans/2026-11-21-vultr-inference-catalog-reference.md)
