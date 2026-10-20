# More provider and research-service integrations

The direct provider layer now covers all **117 exact pinned directory claims across 16 families**. Additional integrations below are tracked separately so adding another service does not inflate that model count. All model inference still requires verified account entitlement and exact-model admission; no credentials or independent votes are fabricated.

## Implemented in the continued batch

**SambaNova** adds a separate native chat transport at `https://api.sambanova.ai/v1/chat/completions` and catalog at `https://api.sambanova.ai/v1/models`, using only `SAMBANOVA_API_KEY`. [Official API keys/URLs](https://docs.sambanova.ai/docs/en/get-started/api-keys-urls), [OpenAI compatibility](https://docs.sambanova.ai/docs/en/features/openai-compatibility), and the provider's [OpenAPI specification](https://raw.githubusercontent.com/sambanova/sambanova-inference-api-spec/refs/heads/main/openapi.documented.json) establish endpoint, bearer auth and model-list schema. Its [current limits](https://docs.sambanova.ai/docs/en/models/rate-limits) distinguish free accounts with no payment method from Developer accounts. The listed production free-tier models are `DeepSeek-V3.1`, `Meta-Llama-3.3-70B-Instruct` and `gpt-oss-120b`, with 20 requests/minute, 20/day and 200,000 tokens/day listed per model. These are public plan claims, not this user's remaining balance. Preview models are explicitly not production models. No usable SambaNova key/account is established here.

**OVHcloud public discovery** uses `https://catalog.endpoints.ai.ovh.net/rest/v1/models_v2`, a separate, unauthenticated full-array API. The [official catalog documentation](https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-catalog-api) explicitly says no key, no parameters and one whole-catalog response. The implementation never forwards the inference key to this catalog host, preserves exact IDs and `available:false`, and ignores metadata-provided URLs for routing. A live public read returned 22 catalog entries, 20 marked available; this includes more than just text models. Discovery is not free inference entitlement.

**ModelScope public discovery** uses `https://api-inference.modelscope.ai/v1/models`. A direct provider-host request returned HTTP 200, 35 model entries in an OpenAI-shaped `object:list/data` response, no auth and no pagination fields/Link header. This route is recorded as a **provider runtime observation**, not falsely attributed to a published catalog specification. The [official inference introduction](https://www.modelscope.ai/docs/model-service/API-Inference/intro) still requires account binding/real-name verification for inference. The adapter neither performs that verification nor sends a credential to public discovery.

Those two catalog additions raise pinned-directory catalog adapter coverage to **15/16 families**: 14 with published catalog contracts, plus runtime-observed ModelScope. Z.ai's 3 exact claims retain `catalog_adapter_not_implemented`; an unauthenticated `/models` returning 401 does not prove its schema or support. The [Z.ai introduction](https://docs.z.ai/api-reference/introduction) documents the inference base and bearer auth, not a verified list-models route.

**GitHub proposal feedback** now has a diagnosed and tested API path, distinct from model access. See [the exact failed request, token context, rate headers, working administrator-capable connector and repair](GITHUB-FEEDBACK-API-DIAGNOSTICS.md). Full access does not turn discussion comments into authenticated ballots.

## Expanded provider continuity and evidence semantics

The six-hour [provider availability workflow](../../.github/workflows/provider-availability.yml) now enumerates the canonical provider catalog adapter registry instead of hard-coding only Gemini, OpenRouter, Felo and Hugging Face. Configured provider credentials trigger bounded catalog GETs; explicitly public catalog sources (LLM7, OVHcloud and ModelScope) are observed without a credential. Unconfigured credentialed providers are not contacted. Cloudflare discovery requires its configured account identifier and token.

Only the existing OpenRouter and Gemini lanes issue minimal inference probes. Newly expanded native providers are **catalog-only** in this workflow; this does not add them to evaluation cohorts, enable native routing, or spend inference quota. Strict mode checks configured providers' required probes and the explicitly public catalogs. The evidence distinguishes `credential_present`, `auth_mode`, `catalog_probe_required`, `catalog_ok`, and `inference_ok`; public discovery does not imply account entitlement, and an unconfigured secret is not a provider failure.

The workflow uses the canonical `provider_model_catalog.poll()` adapter so catalog pagination and provider-specific response normalization stay aligned with the batch/catalog implementation. It emits only normalized model IDs/counts, safe error classes, timestamps and boolean state; it never serializes credential values, authorization headers or upstream response bodies. The expanded offline tests mock catalog requests and assert that unconfigured providers cause no request and newly added providers never trigger inference.

The health receipt also records `credential_env_resolved` (the exact environment-variable name that resolved) or `credential_env_expected` (the canonical expected name when absent). These are names-only diagnostics: secret values never enter the receipt. Hugging Face aliases are mapped independently in Actions so an `HF_TOKEN` observation is not mislabeled as `HUGGINGFACE_TOKEN` merely because the workflow copied the value into a fallback variable.

## Public research service

**Firecrawl keyless scrape is working in the merged trusted-production workflow.** [Run 39396483576](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39396483576), on merged commit `9ce48a5c5d80da703cef6f7fe7c4f473ebcd0fe3`, returned `status: observed`, `reason: ok`, `authentication: none` and **78,335 Markdown characters** from the fixed public awesome-free-llm-apis repository source. The earlier Sandbox request returned HTTP 403; that remains a local failure, not a diagnosed quota error or a universal outage. No account, key, signup or paid fallback was used in the successful production request. Its [official introduction](https://docs.firecrawl.dev/introduction) explicitly demonstrates the keyless `POST https://api.firecrawl.dev/v2/scrape`, and [billing documentation](https://docs.firecrawl.dev/billing) distinguishes per-IP/day keyless limits from account plans. The adapter only accepts the two fixed public upstream URLs, requests one Markdown page, blocks redirects and never reads/sends credentials. The trusted-manual workflow's `observe_public_research` option remains default-off, and actual service outcomes are preserved separately from catalog success.

```bash
python3 scripts/services/firecrawl_public_research.py \
  --source awesome-free-llm-apis --output /tmp/public-research.json
```

The separate account Free plan currently advertises 1,000 monthly credits and HTTP 402 at exhaustion, with no pay-as-you-go on Free. That claim is not assigned to keyless mode and is not reported as an existing account balance. Higher-rate account signup remains a human-input edge only if an appropriate Agent-owned contact and verification are missing.

## Next candidates, not yet integrated

| Candidate | Official evidence and useful next step | Remaining condition |
|---|---|---|
| Linkup | [Quickstart/auth](https://docs.linkup.so/pages/documentation/get-started/quickstart), [pricing](https://docs.linkup.so/pages/documentation/platform/pricing): bearer-auth `https://api.linkup.so/v1/search`, prepaid balance, exhaustion returns 429 | Professional-email eligibility governs $20 monthly replenishment. Verify eligibility and contact before claiming a permanent free account. |
| Exa | [Pricing](https://exa.ai/docs/admin/pricing), [billing](https://exa.ai/docs/admin/billing): recurring $10 monthly for the first team, no-card Free, exhaustion 402 | Verify first-team eligibility, API-key budget and auto-recharge disabled. One-time onboarding bonus is not recurring quota. |
| Tavily | [Credits/pricing](https://docs.tavily.com/documentation/api-credits), [Search API](https://docs.tavily.com/api-reference/endpoint/search): 1,000 free monthly credits and bearer-auth search | Verify the actual account's paid-overflow configuration; no hard no-spend assertion is made from incomplete documentation. |

## Rejected rather than implemented

**GitHub Models is retired.** The [current official notice](https://docs.github.com/en/github-models) says playground, catalog, inference and BYOK were fully retired July 30, 2026. Old posts advertising free model access are stale; no dead GitHub Models adapter or reuse of an administrator token for inference is added.

The upstream FreeLLMAPI proxy and cookie-backed/browser-wrapped services are not executed. Its 37 harvested rows are service-class leads, not extracted exact model IDs or proof of usable APIs. Current native family mappings are Cloudflare, Cohere and ModelScope; direct official integrations remain separate from adopting that proxy's implementation.
