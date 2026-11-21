# Vultr Inference Catalog Reference — Design

**Date:** 2026-11-21  
**Status:** scoped design for MSM-025  
**Owner surface:** `timerloggedout-spec/termux-monorepo`

## Goal

Register Vultr's Python and TypeScript model-catalog repositories as pinned, metadata-only references and derive an evidence-backed improvement specification for the monorepo's existing provider Inference catalogue.

## Evidence and source identity

| Reference | Default branch | Inspected commit | License |
|---|---|---|---|
| [vultr/model-catalog-python](https://github.com/vultr/model-catalog-python) | `main` | `4a414ab26e1f596cb98b3974a7d12182bf62dab3` | MIT; verified from `LICENSE` |
| [vultr/model-catalog-typescript](https://github.com/vultr/model-catalog-typescript) | `main` | `6e55057cb718213937c4c118271f5a2ca1779d0d` | MIT; verified from `LICENSE` |

The repositories describe matching Python and TypeScript libraries for Vultr Inference's public `GET /v1/models` endpoint. Their shared input is an OpenRouter Provider Model Document 2.4. The Python project targets Python 3.11+; the TypeScript project targets Node 20+ or Bun. Both declare zero runtime dependencies and share normalized fixtures.

## Current monorepo baseline

The canonical collector is `scripts/provider_model_catalog.py`, schema `provider-model-catalog/v5`. It already separates provider catalog observations, pricing classification, access classification, documented entitlements, credential presence, quota evidence and inference outcomes. Provider-specific wire adapters live in `scripts/provider_catalog_protocols.py` and `scripts/provider_extension_catalogs.py`.

The current normalized model record emphasizes provider/model identity, pricing, access evidence, cadence, context length, output limit, selected capabilities, active state and source label. The collector records provider observation time, selected response headers, credential environment-variable name, contract-source classification and quota-manager status. The existing catalog is multi-provider and policy-aware; Vultr's libraries are single-provider SDKs for one documented model-document shape.

## Design decisions

1. Register both repositories under `refTemplates/19_Provider_Inference_Catalogs/`. Slot 18 is reserved by the active Vector Databases reference work in PR #5753.
2. Pin each reference to the inspected full commit SHA and record the verified MIT license.
3. Keep the references metadata-only. Add no submodule, fork, package dependency, installer, runtime call, inference request, secret mapping, schedule or routing/admission mutation.
4. Preserve provider-specific adapters and the existing v5 evidence distinctions. Treat Vultr's document as a valuable schema reference, not as a universal provider wire contract.
5. Record the comparison in `docs/ops/VULTR-INFERENCE-CATALOG-REFERENCE-RECON.md`.
6. Extend the existing refTemplates inventory contract to validate metadata child directories for the managed reference slots, including slots 18 and 19.
7. Keep any v6 catalog schema or runtime normalization implementation as a separately scoped follow-on.

## Lessons to evaluate

- Lossless input/output modality records with source descriptors and per-modality limits.
- Exact decimal pricing strings and explicit units, including request, cached-input, cache-write and reasoning prices.
- Tool, structured-output, streaming, reasoning-effort and parameter descriptors.
- Model lifecycle and deprecation metadata.
- Per-entry issues and tolerant parsing for malformed individual records.
- Raw-payload cache with endpoint identity and fetch timestamp; visible `network`, `cache` and `stale-cache` source states.
- Shared language-neutral golden fixtures for cross-language normalization parity.
- Model-kind predicates that distinguish chat, agent, embedding, rerank, image, audio, video and decision models.

## Adaptation constraints

- Preserve unknown values as unknown; record evidence source and freshness.
- Keep catalog presence, credential state, entitlement, quota, health and inference success as separate facts.
- Keep provider-specific wire payloads behind adapters and normalize into a versioned monorepo contract.
- Treat a model-list response as catalog evidence, not an inference-health result.
- Preserve exact source and observation provenance for every imported capability and price.
- Translate Vultr's provider-specific assumptions into explicit monorepo policy. For example, the reference library defaults missing `is_ready` to true; the monorepo's admission evidence must retain unknown where readiness is unreported.

## Acceptance criteria

- Both reference repositories appear in the new refTemplates slot with exact source URLs, immutable commit pins and MIT license evidence.
- The top-level refTemplates index, source map, ICM reference-input card and workflow integrity guidance point to the new slot.
- The inventory validator enforces `README.md` and `SOURCE.txt` for reference child directories in slots 15, 18 and 19.
- Focused inventory tests pass.
- The comparative RECON distinguishes source facts, current monorepo facts and recommendations.
- Repo gate and Termux smoke run on the final PR head; workflow results are inspected on that same SHA.
- Runtime catalog behavior, credentials, inference, quotas, provider admission and routing remain unchanged.

## Deferred work

A provider-model-catalog v6 schema proposal may follow with a compatibility matrix and migration plan. Its implementation requires a separate accepted item, test-first design, v5 compatibility analysis, and explicit evidence requirements.