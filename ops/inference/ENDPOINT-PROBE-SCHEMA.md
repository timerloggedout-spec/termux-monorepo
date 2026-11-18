# Endpoint probe schema — `inference-endpoint-availability/v1`

Producer: `scripts/inference/endpoint_probe.py` via `.github/workflows/inference-endpoint-probe.yml`
(workflow_dispatch ∨ every 6h at :23 UTC). Live copies land on branch `inference-ledger`;
this master copy = seed.

## Files

| Path | Shape | Write mode |
|---|---|---|
| `ops/inference/endpoint-availability.json` | one document (below) | replace per run |
| `ops/inference/endpoint-probe-log.jsonl` | one line per endpoint per run | append-only |

## Document

| Field | Meaning |
|---|---|
| `schema` | `inference-endpoint-availability/v1` |
| `generated_at` | UTC ISO-8601 |
| `safety_factor` | 0.5 |
| `doe_calls_per_slot_day` | expected DoE calls one slot consumes per day (default 50) |
| `max_completion_calls_per_endpoint` | hard cap = 1 |
| `total_safe_parallel_slots` | Σ `slots.safe_parallel_slots` over endpoints with `check.status == ok` |
| `counts` | `{ok, skipped, failed}` endpoint counts |
| `top_endpoints` | top 5 `{endpoint, slots}` |
| `missing_secrets` | secret NAMES absent from Actions (names only) |
| `actions_cache` | `{catalog_hit, catalog_miss, pip_hit, jobs[{endpoint, catalog_cache_hit, pip_cache_hit, job_duration_s}], job_duration_s_max, job_duration_s_sum}` |
| `run` | `{github_run_id, github_sha}` |
| `endpoints[]` | per-endpoint record (below) |

## Endpoint record

| Field | Meaning |
|---|---|
| `endpoint` | key in `provider_model_catalog.ENDPOINTS` |
| `route_class` | `openai-compat:/v1/chat/completions` ∨ `native:gemini.generateContent` ∨ `catalog_only` |
| `secret_present` / `public_catalog` | booleans only |
| `secret_env` | primary secret NAME (value ∅) |
| `catalog` | `{status, cache: hit∨miss, model_count, free_model_count, free_models[≤25]{id, context_length, max_output_tokens, pricing_classification, free_basis}, headers}` |
| `check` | `{status, model, free_basis, http_status, latency_ms, calls, headers, error}`; `status` ∈ `ok`, `failed`, `skipped:no_secret`, `skipped:no_free_model`, `skipped:no_completion_route`, `skipped:call_cap` |
| `theirs` | provider-declared limits: `{rpm, rpd, remaining_minute, remaining_day, retry_after_s, source: response_headers ∨ docs_snapshot ∨ response_headers+docs, docs_source, docs_scope}` |
| `ours` | `{calls_24h, source: inference-ledger ∨ probe-log}` — consumed calls incl. this probe |
| `slots` | `{safe_parallel_slots, basis, rpm_headroom, remaining_day, day_slots}` |

## Rules

- Free gate: completion runs only on a model classified free — OpenRouter `:free` suffix, catalog zero price,
  documented free trial, ∨ documented free-tier provider (`groq`, `cerebras`, `llm7`). Request = `max_tokens=1`.
- Slot math: `floor(min(rpm_headroom, remaining_day / doe_calls_per_slot) × 0.5)`;
  `remaining_day` = header value ∨ `rpd − ours.calls_24h`. ∅ limits ⇒ 0 slots (`no_declared_limits`).
- Headers kept: `pmc.HEADER_PREFIXES` (`x-ratelimit-*`, `x-credit-*`, `x-quota-*`, `x-remaining-*`, `x-usage-*`) ∧ `retry-after`, `x-request-id`.
- Keep values secret-free: presence booleans ∧ secret names only; errors map to a fixed safe vocabulary.

## Log line (`endpoint-probe-log.jsonl`)

`{observed_at, endpoint, check, model, calls, slots}` — feeds `ours` when the inference ledger is absent.
