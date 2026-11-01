# Quota readings gaps — refresh against the 155-record registry (2026-10-29)

[MUSEai]@{role:{quota-gaps}} Refresh of `docs/ops/QUOTA-READINGS-GAPS-2026-10-27.md` (written against the 64-record registry; superseded by this document for coverage purposes). Method: registry `ops/quota/registry.json` and committed readings snapshot `docs/ops/generated/quota-status.json` read from master 2026-10-29 ~18:47 PT; classification computed per record, not sampled.

## State of record

- Registry: **155 records** (94 with a documented limit, 61 limit null).
- Committed readings snapshot at computation time: generated **2026-10-28T13:16:27Z, 8 rows**.
- **Update (2026-10-29 ~18:50 PT, verified on master): the converted 155-row snapshot LANDED — PR #2362 merged `49089ee5c010`** (snapshot pair byte-identical, blob `5d5238c9`, 155 rows, generated 2026-10-28T23:36:07Z). Post-landing classes: **A = 6** H0/confirmed (github.actions.cache · github.api.github_token · huggingface.hub_api · openrouter.free_models · openrouter.key · vercel.deployments), **4** H1/early_signal, **145** H1/attributed_claim unobserved rows. The per-record table below preserves the pre-landing committed state it was computed from; the landing changed structure (every record now has a row), not signal — burn observability remains confined to class A, as the strategy input states. Per the documented converter procedure the hand-promoted github.api.user_token H0 row and the github.actions.minutes attributed note were superseded by unobserved rows.
- Burn-signal classes: **A** probe-observed (H0/confirmed reading on master) · **B** row present, unobserved/attributed only · **C** entitlement only (limit documented, zero readings of any kind) · **D** fully dark (limit null, no row).

## Counts

| class | count | meaning for the allocation planner |
|---|---|---|
| A probe-observed | 7 | burn signal exists (status-level; numeric only where the reading carries numbers) |
| B row, unobserved | 1 | attributed note only |
| C entitlement only | 90 | planner knows the ceiling, has never seen burn |
| D fully dark | 57 | no ceiling, no burn — pacing/stranded uncomputable |

**147 of 155 records have no burn signal of any kind on master.** Strategy consequence (quota-gaps lane input to the 2026-10-29 STRATEGIZE): observability before optimization — no throttling or pacing decision is evidence-based outside class A; expanding probe readers is the only move that shrinks C/D, and the pending converted-snapshot promotion is structure, not signal.

## Per-record table

| service | limit | unit | class | reading on master |
|---|---|---|---|---|
| aion.free_tokens | 20000 | tokens/day | C | — |
| aws.account_credits | 200 | USD | C | — |
| aws.dynamodb_storage | 25 | GB | C | — |
| aws.lambda_compute | 400000 | GB-seconds/month | C | — |
| aws.lambda_requests | 1000000 | requests/month | C | — |
| azure.account_credit | 200 | USD | C | — |
| azure.functions_executions | 1000000 | executions/month | C | — |
| cerebras.free_tokens | 1000000 | tokens/day | C | — |
| cloudflare.d1_rows_read | 5000000 | rows/day | C | — |
| cloudflare.d1_rows_written | 100000 | rows/day | C | — |
| cloudflare.d1_storage | 5 | GB | C | — |
| cloudflare.kv_writes | 1000 | writes/day | C | — |
| cloudflare.queues_ops | 10000 | operations/day | C | — |
| cloudflare.r2_storage | 10 | GB-month | C | — |
| cloudflare.workers_ai | 10000 | Neurons/day | C | — |
| cloudflare.workers_requests | 100000 | requests/day | C | — |
| cohere.trial_calls | 1000 | API calls/month | C | — |
| deno.deploy_requests | 1000000 | requests/month | C | — |
| digitalocean.app_platform_static | 3 | apps | C | — |
| digitalocean.trial_credit | 200 | USD | C | — |
| felo.api_credits | 200 | credits/day | C | — |
| fly.free_tier | 0 | USD/month | C | — |
| g4f.agenttools | 250 | units | C | — |
| g4f.airforce | 1000 | requests | C | — |
| g4f.antigravity | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.arena | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.bingcreateimages | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.blackboxpro | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.blackforestlabs_flux1dev | 2 | minutes of GPU time | C | — |
| g4f.blackforestlabs_flux1kontextdev | 2 | minutes of GPU time | C | — |
| g4f.bravesearch | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.cachedsearch | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.cerebras | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.chatgpt | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.claude | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.cloudflare | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.cohereforai_c4ai_command | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.copilot | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.copilotapp | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.deepinfra | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.deepseek | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.elevenlabs | 10000 | credits | C | — |
| g4f.g4fspace | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.gemini | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.geminicli | 1000 | requests | C | — |
| g4f.geminipro | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.githubcopilot | 50 | premium requests (all chat interactions count as premium requests) | C | — |
| g4f.glm | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.googleaimode | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.googlesearch | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.grok | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.groq | 1000 | requests per day (RPD) for openai/gpt-oss-120b | C | — |
| g4f.hailuoai | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.huggingchat | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.huggingface | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.huggingfacemedia | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.huggingspace | 2 | GPU-minutes (ZeroGPU) | C | — |
| g4f.kilocode | 200 | requests | C | — |
| g4f.llm7 | 100000 | tokens (input + output) | C | — |
| g4f.markitdown | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.metaai | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.metaaiaccount | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.microsoftdesigner | 15 | boosts (fast AI creations/edits) | C | — |
| g4f.nvidia | 1000 | API credits | C | — |
| g4f.ollama | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.omniroute | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.openaifm | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.openrouterfree | 50 | requests | C | — |
| g4f.operaaria | 5 | images | C | — |
| g4f.perplexity | 3 | Pro Searches | C | — |
| g4f.pi | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.pollinations | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.pollinationsaudio | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.pollinationsimage | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.puter | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.qwen | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.relayrouter | 2000000 | tokens | C | — |
| g4f.stabilityai_sd35large | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.teachanything | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.vendors | null | unmetered / unknown | D | — |
| g4f.whiterabbitneo | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.you | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| g4f.yqcloud | null | unmetered / unknown (NOT ESTABLISHED) | D | — |
| gcp.cloud_functions_invocations | 2000000 | invocations/month | C | — |
| gcp.cloud_run_requests | 2000000 | requests/month | C | — |
| gcp.compute_e2micro | 1 | instance/month | C | — |
| gemini.api_free | null | per-model | D | — |
| github.actions.cache | 10 | GB | A | H0/confirmed ok |
| github.actions.minutes | null | minutes | B | H1/attributed_claim watch |
| github.api.github_token | 1000 | requests/hour/repo | A | H0/confirmed exhausted |
| github.api.user_token | 5000 | requests/hour | A | H0/confirmed ok |
| github.artifacts.retention | 90 | days | C | — |
| github.codespaces.core_hours | 120 | core-hours/month | C | — |
| github.codespaces.storage | 15 | GB-month | C | — |
| github.copilot.free | null | requests/month | D | — |
| grafana.cloud_free | 10000 | samples/s | C | — |
| groq.free_tier | null | per-model requests/tokens | D | — |
| huggingface.hub_api | null | requests per 5-minute fixed window (account-dynamic) | A | H0/confirmed unknown |
| huggingface.inference_providers | null | monthly credits | D | — |
| kilo.free_models | 200 | requests/hour | C | — |
| koyeb.free_instance | 1 | instance | C | — |
| llm7.free_token | 100000 | tokens/day | C | — |
| mistral.free_mode | null | included usage (per model, in-account) | D | — |
| modelscope.api_inference | 2000 | requests/day | C | — |
| neon.compute | 100 | CU-hours/project/month | C | — |
| neon.egress | 5 | GB/month | C | — |
| neon.realtime | null | free during beta | D | — |
| neon.storage | 1 | GB/project (20 GB total) | C | — |
| netlify.credits | 300 | credits/month | C | — |
| nvidia.api_catalog | null | per-model credits/limits (in-account) | D | — |
| ollama.balance | null | variant-specific USD or percent; never requests/tokens | D | — |
| omni.gateway | null | n/a (aggregates upstream free tiers) | D | — |
| openrouter.free_models | null | requests/day (dynamic tier; endpoint supplies limit) | A | H0/confirmed unknown |
| openrouter.key | null | signal-specific requests or monetary credits; tier is not model price | A | H0/confirmed unknown |
| oracle.ampere_gb_hours | 9000 | GB-hours/month | C | — |
| oracle.ampere_ocpu_hours | 1500 | OCPU-hours/month | C | — |
| oracle.block_storage | 200 | GB | C | — |
| ovhcloud.ai_endpoints | 2 | requests/minute | C | — |
| partners.credits | null | one-time credits | D | — |
| pinecone.egress | 1 | GB/month | C | — |
| pinecone.indexes | 5 | indexes (100 namespaces each) | C | — |
| pinecone.read_units | 1000000 | RU/month | C | — |
| pinecone.storage | 2 | GB | C | — |
| pinecone.write_units | 2000000 | WU/month | C | — |
| platform201.projects | 3 | projects | C | — |
| render.bandwidth | 5 | GB/month | C | — |
| render.instance_hours | 750 | hours/month | C | — |
| render.keyvalue_free | 1 | instance/workspace (in-memory only) | C | — |
| render.pipeline_minutes | 500 | minutes/month | C | — |
| render.postgres_free | 1 | GB (1 instance/workspace) | C | — |
| requesty.free_models | 200 | requests/day | C | — |
| routeway.free_models | 200 | requests/day | C | — |
| sambanova.free_tier | 20 | requests/day per model | C | — |
| sealion.api | 10 | requests/minute per user | C | — |
| siliconflow.free_models | null | requests/minute + tokens/minute (per model) | D | — |
| supabase.db_storage | 500 | MB | C | — |
| supabase.edge_functions | 500000 | invocations/month | C | — |
| supabase.egress | 5 | GB/month | C | — |
| supabase.file_storage | 1 | GB | C | — |
| supabase.projects | 2 | projects | C | — |
| turso.databases | 100 | databases | C | — |
| turso.rows_read | 500000000 | rows/month | C | — |
| turso.rows_written | 10000000 | rows/month | C | — |
| turso.storage | 5 | GB | C | — |
| typhoon.api | 200 | requests/minute | C | — |
| unorouter.free_models | 1 | requests/minute per free model per user | C | — |
| upstash.qstash_messages | 1000 | messages/day | C | — |
| upstash.redis_bandwidth | 10 | GB/month | C | — |
| upstash.redis_commands | 500000 | commands/month | C | — |
| upstash.redis_storage | 250 | MB | C | — |
| vercel.build_time | 45 | minutes | C | — |
| vercel.deployments | 100 | deployments/day | A | H0/confirmed ok |
| xfyun.spark | null | unknown | D | — |
| xkiro.free_models | 500000 | tokens/day | C | — |
| zai.free_models | null | per-account (unpublished) | D | — |

Class A detail: github.actions.cache · github.api.github_token · github.api.user_token · huggingface.hub_api · openrouter.free_models · openrouter.key · vercel.deployments (all H0/confirmed in the committed snapshot). Class B: github.actions.minutes (H1, attributed, observed_at null).
