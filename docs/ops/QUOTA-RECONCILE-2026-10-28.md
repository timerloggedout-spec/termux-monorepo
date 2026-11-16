# Quota reconcile — 2026-10-28

Owner order: ALL Quota — our count + provider→reconcile. Produced by the Quota Specialist lane; all counts derived live from the files named, at landing time.

## The count

- `ops/quota/registry.json`: **155 records** (was 69 on master after the PR #2018 regression; 95 after restoration, +60 g4f = 155).
- Distinct provider strings in registry: **108**.
- Records with a documented numeric limit: **94**; limit null (status/unknown/not-established): **61**.
- `ops/quota/allocations.json`: **52 pools / 155 services / 0 excluded** (validator green; every registry service pooled).
- Coverage (`provider-quota-coverage.json`): 27 catalog families, actual_quota_service_mappings 27, missing 0.
- Delphi `ops/delphi/surfaces.json`: 18 surfaces; `g4f.vendors` aggregate retained (sourced=false) for the unresolved g4f set.
- Cadence `ops/cadence/provider-onboarding.json`: 33 entries (27 llm + 6 review) — all 27 llm families carry a registry model-lane record after the restoration.

## PR #2018 regression — repaired

PR #2018 (dfed00c5c508) published registry.json from a stale base: 90 → 69 records. Restored verbatim from its parent (0798e22d): 26 lost records (the #1875 expansion set + `huggingface.hub_api`, `huggingface.inference_providers`, `platform201.projects`) and the reverted texts of `openrouter.key`, `gemini.api_free`, `ollama.balance`. The 5 `pinecone.*` records from #2018 are kept; a `pinecone` allocations pool was added (they had none).

## g4f 60 — per-provider resolution

Primary sources only. ESTABLISHED = the vendor publishes a numeric limit for the surface the g4f provider wraps (limit on the record, with source + quote). Where the only published limit belongs to a *different* surface (e.g. an API product behind a web wrapper — Cerebras, Cloudflare, Qwen, You), the g4f record is NOT ESTABLISHED and the API figure is kept as a cross-reference note only. NOT ESTABLISHED records carry a **usage-log inference** (g4f tester harvest 2026-10-28: working models of catalogued models) — inference is labeled, never an entitlement; limit stays null.

| g4f provider | verdict | limit | working/catalogued models |
|---|---|---|---|
| AgentTools | ESTABLISHED | 250 units / per day | 1/1 |
| Airforce | ESTABLISHED | 1000 requests / per day | 0/783 |
| Antigravity | NOT ESTABLISHED (inference on record) | — | 0/22 |
| Arena | NOT ESTABLISHED (inference on record) | — | 0/154 |
| BingCreateImages | NOT ESTABLISHED (inference on record) | — | 0/1 |
| BlackForestLabs_Flux1Dev | ESTABLISHED | 2 minutes of GPU time / per day, resets exactly 24 hours after first GPU usage | 1/2 |
| BlackForestLabs_Flux1KontextDev | ESTABLISHED | 2 minutes of GPU time / per day, resets exactly 24 hours after first GPU usage | 0/1 |
| BlackboxPro | NOT ESTABLISHED (inference on record) | — | 0/0 |
| BraveSearch | NOT ESTABLISHED (inference on record) | — | 0/2 |
| CachedSearch | NOT ESTABLISHED (inference on record) | — | 0/0 |
| Cerebras | NOT ESTABLISHED (inference on record) | — | 0/4 |
| ChatGPT | NOT ESTABLISHED (inference on record) | — | 0/1 |
| Claude | NOT ESTABLISHED (inference on record) | — | 0/2 |
| Cloudflare | NOT ESTABLISHED (inference on record) | — | 38/54 |
| CohereForAI_C4AI_Command | NOT ESTABLISHED (inference on record) | — | 3/7 |
| Copilot | NOT ESTABLISHED (inference on record) | — | 0/4 |
| CopilotApp | NOT ESTABLISHED (inference on record) | — | 0/5 |
| DeepInfra | NOT ESTABLISHED (inference on record) | — | 0/25 |
| DeepSeek | NOT ESTABLISHED (inference on record) | — | 0/2 |
| ElevenLabs | ESTABLISHED | 10000 credits / per month | 0/1 |
| G4FSpace | NOT ESTABLISHED (inference on record) | — | 0/174 |
| GLM | NOT ESTABLISHED (inference on record) | — | 1/3 |
| Gemini | NOT ESTABLISHED (inference on record) | — | 1/1 |
| GeminiCLI | ESTABLISHED | 1000 requests / per user per day | 0/0 |
| GeminiPro | NOT ESTABLISHED (inference on record) | — | 0/58 |
| GithubCopilot | ESTABLISHED | 50 premium requests (all chat interactions count as premium requests) / per month | 0/0 |
| GoogleAiMode | NOT ESTABLISHED (inference on record) | — | 1/1 |
| GoogleSearch | NOT ESTABLISHED (inference on record) | — | 0/1 |
| Grok | NOT ESTABLISHED (inference on record) | — | 0/4 |
| Groq | ESTABLISHED | 1000 requests per day (RPD) for openai/gpt-oss-120b / per day | 0/11 |
| HailuoAI | NOT ESTABLISHED (inference on record) | — | 0/1 |
| HuggingChat | NOT ESTABLISHED (inference on record) | — | 0/131 |
| HuggingFace | NOT ESTABLISHED (inference on record) | — | 0/132 |
| HuggingFaceMedia | NOT ESTABLISHED (inference on record) | — | 0/361 |
| HuggingSpace | ESTABLISHED | 2 GPU-minutes (ZeroGPU) / per day | 5/13 |
| KiloCode | ESTABLISHED | 200 requests / per hour per IP | 8/400 |
| LLM7 | ESTABLISHED | 100000 tokens (input + output) / per day | 0/1 |
| MarkItDown | NOT ESTABLISHED (inference on record) | — | 0/0 |
| MetaAI | NOT ESTABLISHED (inference on record) | — | 0/1 |
| MetaAIAccount | NOT ESTABLISHED (inference on record) | — | 0/1 |
| MicrosoftDesigner | ESTABLISHED | 15 boosts (fast AI creations/edits) / per day | 0/4 |
| Nvidia | ESTABLISHED | 1000 API credits / on sign-up (one-time trial grant) | 0/85 |
| Ollama | NOT ESTABLISHED (inference on record) | — | 0/23 |
| OmniRoute | NOT ESTABLISHED (inference on record) | — | 0/1 |
| OpenAIFM | NOT ESTABLISHED (inference on record) | — | 17/17 |
| OpenRouterFree | ESTABLISHED | 50 requests / per day | 0/14 |
| OperaAria | ESTABLISHED | 5 images / per day | 0/2 |
| Perplexity | ESTABLISHED | 3 Pro Searches / per day | 20/46 |
| Pi | NOT ESTABLISHED (inference on record) | — | 0/1 |
| Pollinations | NOT ESTABLISHED (inference on record) | — | 1/175 |
| PollinationsAudio | NOT ESTABLISHED (inference on record) | — | 0/38 |
| PollinationsImage | NOT ESTABLISHED (inference on record) | — | 0/2 |
| Puter | NOT ESTABLISHED (inference on record) | — | 0/1022 |
| Qwen | NOT ESTABLISHED (inference on record) | — | 1/24 |
| RelayRouter | ESTABLISHED | 2000000 tokens / per account total, with daily sub-caps resetting 00:00 UTC | 0/420 |
| StabilityAI_SD35Large | NOT ESTABLISHED (inference on record) | — | 1/1 |
| TeachAnything | NOT ESTABLISHED (inference on record) | — | 0/1 |
| WhiteRabbitNeo | NOT ESTABLISHED (inference on record) | — | 0/0 |
| You | NOT ESTABLISHED (inference on record) | — | 0/0 |
| Yqcloud | NOT ESTABLISHED (inference on record) | — | 1/1 |

Totals: **17 ESTABLISHED / 43 NOT ESTABLISHED** of 60. Tester totals at harvest: 4,829 tested, 100 working entries, 15 providers with ≥1 working model.

## Catalog families (27) — reconcile

| family | registry service(s) | documented limit |
|---|---|---|
| aion | aion.free_tokens | — |
| cerebras | cerebras.free_tokens | — |
| cloudflare | cloudflare.workers_ai | — |
| cohere | cohere.trial_calls | — |
| felo | felo.api_credits | — |
| gemini | gemini.api_free | — |
| groq | groq.free_tier | — |
| huggingface | huggingface.inference_providers | — |
| kilo | kilo.free_models | — |
| llm7 | llm7.free_token | — |
| mistral | mistral.free_mode | — |
| modelscope | modelscope.api_inference | — |
| nvidia | nvidia.api_catalog | — |
| ollama | ollama.balance | — |
| omni | omni.gateway | — |
| openrouter | openrouter.free_models, openrouter.key | — |
| ovhcloud | ovhcloud.ai_endpoints | — |
| requesty | requesty.free_models | — |
| routeway | routeway.free_models | — |
| sambanova | sambanova.free_tier | — |
| sealion | sealion.api | — |
| siliconflow | siliconflow.free_models | — |
| typhoon | typhoon.api | — |
| unorouter | unorouter.free_models | — |
| xfyun | xfyun.spark | — |
| xkiro | xkiro.free_models | — |
| zai | zai.free_models | — |
