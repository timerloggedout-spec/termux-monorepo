# Provider batch: native adapters, not directory-based activation

**Current code coverage:** all 117 exact directory claims across 16 families have chat transports (101 explicitly gated native, 16 legacy OpenRouter); 13 families have documented catalog adapters. This is not proof of successful inference. Read [full direct transport completion](#full-direct-transport-completion) for the latest contracts and [HITL](PROVIDER-HITL.md) for actual missing accounts/access. Earlier sections below retain the initial batch and its production receipts.

The initial native batch added **Groq, Mistral and Gemini** through official APIs, covering **21 individual model claims**: 3 Groq, 7 Mistral and 11 Gemini. IDs are matched exactly, including qualified IDs such as `openai/gpt-oss-120b`. This was an implemented adapter batch, not a claim that 21 models were invoked or that every account was free.

The existing OpenRouter, Felo, Omni, and Hugging Face catalog defaults stay unchanged. Adding adapters does not expand existing continuous-evaluation cohorts, change model-router weights, or run the upstream proxy code.

## Official contracts

| Provider | Catalog API | Native hub route | Credential name | Primary reference |
|---|---|---|---|---|
| Groq | `https://api.groq.com/openai/v1/models` | `groq/<exact-model>` | `GROQ_API_KEY` | [Groq models](https://console.groq.com/docs/models) |
| Mistral | `https://api.mistral.ai/v1/models` | `mistral/<exact-model>` | `MISTRAL_API_KEY` | [Mistral model API](https://docs.mistral.ai/api/endpoint/models) |
| Gemini | `https://generativelanguage.googleapis.com/v1beta/models` | `gemini/<exact-model>` | `GEMINI_API_KEY`, alias `GOOGLE_API_KEY` | [Models and pagination](https://ai.google.dev/api/models), [OpenAI compatibility](https://ai.google.dev/gemini-api/docs/openai) |

Catalog requests are GET-only. Gemini uses its key in a header, never a URL, and follows page tokens only on its fixed API path. Authenticated requests reject redirects. Catalog metadata records context/output limits and available capability fields; missing prices remain unknown. A model-list response does not establish invocation health, accepted terms, account entitlement, remaining quota, or license suitability.

## Explicit account admission

New native inference routes are **disabled by default**, even when a key exists. An operator may point `LLM_API_HUB_PROVIDER_POLICY` at an external JSON policy after independently verifying the account, terms, model, and use case. The schema is `research-provider-admission/v1`; each entry requires an exact `provider` and `model`, literal `free_account_verified: true`, literal `terms_accepted: true`, `data_class: public`, and a future UTC `expires_at` ending in `Z`. Explicit paid/trial account status is rejected. No enabled policy is shipped in this change.

These policy fields are an operator assertion, **not machine verification of provider billing**. Do not assert them solely because a directory calls a service free or because an API key is present. If the provider cannot constrain an account to no-cost requests, leave it disabled. There is no paid fallback, provider/account hopping, automatic retry, or automatic production routing-weight change. New routes accept text-only messages; the caller remains responsible for supplying only public data. The hub cannot classify confidential prose by inspecting a string.

Policy is revalidated on each request, so revocation or expiry takes effect without a process restart. A denied native route must not fall through to OpenRouter. Error text excludes upstream bodies and credentials. The existing hub streaming shape remains the API contract; it does not imply native upstream token streaming.

## Every research claim gets a disposition

`provider_batch.py` reconciles **all 160 existing research candidates**, not just the implemented batch. It reuses pinned-source validation and explicit provider identity mappings. Supported identities are OpenRouter, Hugging Face, Groq, Mistral and Gemini. Felo and Omni remain native catalog sources but were not identities in the harvested snapshot.

The report distinguishes `observed_in_catalog`, `not_observed_in_catalog`, `catalog_unavailable`, `not_an_individual_model`, and `adapter_not_implemented`. Aggregate labels and static provider-class references never become invocable model IDs. Unimplemented provider families remain visible rather than being silently dropped or relabeled complete. Every report row retains `runtime_eligible: false`, null remaining quota, source provenance, and blocking reasons. An injected documented model-page record is not counted as a live model-list match.

```bash
python3 scripts/provider_model_catalog.py \
  --providers openrouter,felo,omni,huggingface,groq,mistral,gemini \
  --output /tmp/provider-batch/catalog.json
python3 -m scripts.model_selection_market.provider_batch \
  --catalog /tmp/provider-batch/catalog.json \
  --output /tmp/provider-batch/coverage.json
python3 -m pytest -q tests/test_provider_model_catalog.py \
  tests/test_provider_batch.py tests/test_research_provider_hub.py \
  tests/test_llm_api_hub_server.py tests/test_review_evidence.py
```

## Production validation without accidental activation

[Provider batch production contracts](../../.github/workflows/provider-batch.yml) runs real production entry-point regressions on relevant PRs and master pushes. Tests mock outbound network I/O, not admission or HTTP routing. They cover exact harvested identities, legacy hub compatibility, malformed/expired admission, pricing uncertainty, catalog transport, reconciliation, and review attribution.

A manual dispatch from the default branch additionally checks out trusted default-branch code, reads the seven named catalog credentials from Actions secrets, and stores catalog, coverage, and matrix-review observations in a run-attempt artifact. There is **no new schedule**, no inference step, and no write authority. PR runs receive no provider credentials. The read-only GitHub job token is scoped to the separate review-evidence step, not provider requests. Missing credentials and failed catalogs remain explicit evidence; a successful workflow does not mean every provider passed.

Actions secret values cannot be read back through GitHub's secret API. The session's secret-name listing still returns HTTP 403; that is distinct from the anonymous commit-metadata error fixed by #1298. The workflow can test configured names in place without extracting values, granting permissions, or confusing GitHub PATs with inference credentials.

The fresh production [research run 39377722728](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39377722728) passed contracts, collection, and publication on master `2b559f48fa14ee466baf2242355ca9e1f1950a78`. Its downloaded artifact contains two pinned sources, 160 research candidates, and 185 aggregate records. This verifies #1298's metadata authentication recovery; it does not verify free inference or deploy a hub server.

Review artifacts identify PR-history counts, not current-head approvals. Each formal review retains its commit ID. The production collector records UTC collection start and a separate normalization time, verifies an unchanged head before/after pagination, and requires that head in the collected commit list. This detects head drift without pretending independently retrieved API pages are an atomic event snapshot.

## Completion slice: MSM-012 / MSM-013 / MSM-014

Native exact-model admission now also covers **Hugging Face, Cerebras and NVIDIA**, using fixed official chat URLs: `https://router.huggingface.co/v1/chat/completions`, `https://api.cerebras.ai/v1/chat/completions`, and `https://integrate.api.nvidia.com/v1/chat/completions`. Cerebras and NVIDIA have matching native `/v1/models` adapters. Credentials are `CEREBRAS_API_KEY` and `NVIDIA_API_KEY` (alias `NVIDIA_NIM_API_KEY`); HF retains its four existing aliases. None is enabled merely by possessing a key.

Official references: [HF inference providers](https://huggingface.co/docs/inference-providers/en/index), [HF current pricing](https://huggingface.co/docs/inference-providers/en/pricing), [Cerebras compatibility](https://inference-docs.cerebras.ai/resources/openai), [Cerebras models](https://inference-docs.cerebras.ai/models/overview), [NVIDIA hosted APIs](https://docs.api.nvidia.com/nim/reference/llm-apis), and [NVIDIA catalog](https://integrate.api.nvidia.com/v1/models). NVIDIA's hosted API is distinct from downloadable NIM containers. Documentation establishes transport contracts, not this project's account entitlement.

### How many are implemented?

The pinned snapshot contains **160 research records**, not 160 invocable models:

| Source | Records | Exact model claims | Static/aggregate references | Exact claims covered by chat transports |
|---|---:|---:|---:|---:|
| `mnfst/awesome-free-llm-apis` | 123 | 117 | 6 | 48: 32 explicitly gated native + 16 legacy OpenRouter |
| `tashfeenahmed/freellmapi` | 37 | 0 | 37 provider-class references | 0 exact claims extracted by this parser |

The 32 gated claims comprise 3 Groq, 7 Mistral, 11 Gemini, 5 HF and 6 NVIDIA. This adds 11 exact claims over the earlier batch. Cerebras is implemented but has no exact claim in the pinned snapshot, so does not inflate the count. Six of the directory's 16 provider families have transport coverage. The second source's 37 references do **not** describe its complete upstream model inventory; upstream headline endpoint counts are not the implementation denominator. All records retain dispositions and zero automatic runtime admissions. `summary.by_source` exposes these denominators and labels legacy OpenRouter separately.

### Credential discovery and remaining decisions

The manual default-branch workflow now attempts **names-only** inventory with existing issue-184-authorized administration credentials, isolated from catalogs and read-only review collection. The fixed GitHub metadata endpoint cannot retrieve secret values. Missing authorization, 403 and bounded-pagination failures remain explicit observations. PR runs receive no credentials; no new schedule, permission grant or routing activation is created. The earlier description of a wholly read-only observation job applies to catalog/review calls: the new inventory step uses an existing administrative credential strictly for a metadata GET.

Availability monitoring is separately repaired for HF alias parity and Gemini header authentication; its existing health lane is not admission evidence for new providers. See the [Delphi/RFP matrix](../proposals/active/free-llm-provider-prioritization/DEBATE.md) for proposed priorities and uncast ballots, and the [HITL checklist](PROVIDER-HITL.md) for signup contact/verification, exact-model entitlement and Origin-device access. `DeepAgent.py --doctor` reports local readiness; a local doctor or Administrator title does not prove a remotely running administrator.

### Verified production receipt

[PR #1302](https://github.com/timerloggedout-spec/termux-monorepo/pull/1302) merged as `194f5678108befc4ab759523a5889cc511028d97` after current-head dual gates, provider production contracts, registry and vote hygiene succeeded; independent scoped review found no critical/high issue. [Trusted production run 39381048664](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39381048664) then passed contracts and observation. Its immutable `provider-batch-39381048664-1` artifact contains `credential-names.json`, `catalog.json`, `coverage.json` and `matrix-review.json`.

Names-only inventory succeeded with 30 repository secret names. No supported HF alias or identifiable misnamed HF credential was listed, and all four aliases were unavailable in the job. Groq/Mistral/Cerebras/NVIDIA/Omni credentials were likewise unavailable. This is evidence for the tested repository/runtime surface, not a claim that unrelated organization/environment stores contain no credentials.

Live catalogs returned **578 model rows: 470 OpenRouter, 45 Felo, 63 Gemini**. Exactly **22 research claims matched**: 11 Gemini and 11 OpenRouter. Five covered OpenRouter claims were not observed; 21 covered native claims had unavailable catalogs; 69 exact claims lack implemented adapters; 43 records are static/aggregate references. These categories total 160. No inference was performed by this observation and no model was automatically admitted. Implementation coverage (48 exact claims) and catalog matches (22) answer different questions.

## Full direct transport completion

The next completion slice implements the remaining ten directory families through fixed official APIs: Aion, LLM7, Z.ai, ModelScope, SiliconFlow, Kilo, OVHcloud, Cloudflare Workers AI, Cohere and Ollama Cloud. **All 117 exact directory claims now have chat transport coverage across all 16 families**: 101 gated native claims plus 16 legacy OpenRouter claims. This is wire-protocol coverage, not 117 successful inferences or account-entitled models. Endpoint/model compatibility and current availability still require live account evidence. Cerebras remains extra implemented functionality with no exact pinned claim, and is never added to the denominator.

Catalog support is deliberately narrower: **13/16 directory families**. No model-list route is guessed for Z.ai, ModelScope or OVHcloud (16 exact claims). Their report status is `catalog_adapter_not_implemented`, distinct from a missing credential, a disappeared model and a missing chat adapter. Cloudflare uses its documented account-scoped OpenAI Chat Completions endpoint with a strict 32-hex account ID, not model-specific raw-run schema guesses. Cohere v2 messages/response text are normalized explicitly. Cohere and Cloudflare catalog pagination is bounded and remains on the fixed official path. Ollama preserves cloud catalog IDs exactly, including colons; no `:cloud` suffix is fabricated.

| Native key | Fixed official chat contract | Credential / extra input | Official reference |
|---|---|---|---|
| `aion` | `https://api.aionlabs.ai/v1/chat/completions` | `AION_API_KEY` | [Aion quickstart](https://www.aionlabs.ai/docs/quickstart/), [models](https://www.aionlabs.ai/docs/models/) |
| `llm7` | `https://api.llm7.io/v1/chat/completions` | `LLM7_API_TOKEN` | [LLM7 quickstart](https://docs.llm7.io/quickstart), [models](https://docs.llm7.io/guides/models-api) |
| `zai` | `https://api.z.ai/api/paas/v4/chat/completions` | `ZAI_API_KEY` | [Z.ai OpenAI client](https://docs.z.ai/guides/develop/openai/python) |
| `modelscope` | `https://api-inference.modelscope.ai/v1/chat/completions` | `MODELSCOPE_TOKEN`; owner binding/real-name requirements | [ModelScope API](https://www.modelscope.ai/docs/model-service/API-Inference/intro), [limits](https://www.modelscope.ai/docs/model-service/API-Inference/limits) |
| `siliconflow` | `https://api.siliconflow.com/v1/chat/completions` | `SILICONFLOW_API_KEY`, global-platform key only | [Official models API](https://docs.siliconflow.com/en/api-reference/models/get-model-list), [compatibility](https://www.siliconflow.com/blog/openai-sdk-siliconflow-compatibility-checks) |
| `kilo` | `https://ai-gateway.kilo.ai/api/v1/chat/completions` | `KILO_API_KEY` | [Kilo gateway](https://kilo.ai/docs/gateway), [models](https://kilo.ai/docs/gateway/models-and-providers) |
| `ovhcloud` | `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/chat/completions` | `OVHCLOUD_API_KEY` | [OVH official shared base](https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-responses-api), [OpenAI compatibility](https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-getting-started) |
| `cloudflare` | `https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions` | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` | [Official Chat Completions](https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/), [catalog](https://developers.cloudflare.com/api/resources/ai/subresources/models/methods/list) |
| `cohere` | `https://api.cohere.com/v2/chat` | `COHERE_API_KEY` | [Cohere v2 Chat](https://docs.cohere.com/reference/chat), [v1 model list](https://docs.cohere.com/reference/list-models) |
| `ollama` | `https://ollama.com/v1/chat/completions` | `OLLAMA_API_KEY` | [Cloud](https://docs.ollama.com/cloud), [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility) |

The second source remains **37 static provider-class references, zero extracted exact model IDs**. Two class identities (Cohere and ModelScope) map to these reviewed transports. This is not adoption of its proxy, browser-cookie access, or every service advertised by its upstream README. These source distinctions are included in `summary.by_source.chat_transport_families` and `.catalog_adapter_families`.

The current remote endpoint was actually tested: [canary 39381490398](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39381490398) recorded HTTP `000`, curl exit `6` (DNS resolution failure). A fresh reachable Origin endpoint/approved bridge, a usable signup contact, missing provider credentials, and exact-model account evidence remain in [HITL](PROVIDER-HITL.md). No signup contact or real-name identity is fabricated, no credential is extracted, no free-account flag or independent vote is manufactured.

LLM7's official [Models API](https://docs.llm7.io/guides/models-api) explicitly documents an unauthenticated catalog GET. That single public endpoint may therefore be observed without a token; evidence labels `catalog_authentication: documented_public_get` and no resolved secret name. LLM7 inference still requires a token and the same exact-model account admission. Public catalog access never becomes an anonymous inference fallback.
