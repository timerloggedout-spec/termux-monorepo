# Puter Pool provider harvesting and telemetry

## Source and role

Source repository: https://github.com/timerloggedout-spec/puter-pool_fork

Puter Pool is an operator-hosted OpenAI/Anthropic-compatible facade over Puter accounts. The monorepo integration treats it as a source-backed transport under the existing `g4f/Puter` provider identity. It does not create a second provider family, quota manager, account ledger, task ledger, or dashboard.

## Implemented harvest path

`scripts/puter_pool_catalog.py` reads the Pool's documented `GET /v1/models` endpoint. The reader defaults to `http://127.0.0.1:3000`, accepts only loopback origins, caps response size and timeout, validates model IDs, deduplicates records, and emits the existing `provider-model-catalog/v5` shape.

Run on the host where the operator-managed Pool is listening:

```bash
python3 scripts/puter_pool_catalog.py --output /tmp/provider-catalog/puter-pool.json
# or
PUTER_POOL_BASE_URL=http://127.0.0.1:3000 python3 scripts/puter_pool_catalog.py
```

The reader performs catalog-only GET. It does not read Depot account inventory, auth tokens, credits, usage history, request bodies, or completions. Catalog metadata remains `catalog_only`; pricing, entitlement, quota, and reset remain unknown until provider-authoritative evidence is separately captured.

## Correlation and telemetry contract

Every later inference adapter event joins existing identifiers rather than inventing new ledgers:

- `task_or_entry_ref` / `entry`: QUE task identity
- `provider_family`: `g4f/Puter`
- `exact_model_id`: exact model returned by `/v1/models`
- `endpoint_or_route_id`: `puter-pool-local`
- `workflow_run_id` + `run_attempt`: GitHub Actions execution identity
- `observed_at` / `ts`: UTC observation time
- `request_id`: opaque upstream request ID where available
- `outcome`, `latency_ms`, `input_tokens`, `output_tokens`: sanitized request metrics where supplied by the service

Telemetry policy: emit allowlisted metadata only. Keep account tokens, account names, raw prompts, completions, and provider session data outside repository artifacts. Witness/Provenance receive immutable evidence references and hashes; Temporal owns workflow state; HindSight receives compact sanitized summaries; Bifrost/n8n/Platform201 consume existing normalized feeds according to their registered roles. The existing SHE/Tribute interfaces consume the current quota and task-correlation projections.

## Runtime integration sequence

1. Harvest the live model list from the operator's local Pool.
2. Merge catalog rows into the canonical provider-model catalog using the `g4f/Puter` identity.
3. Add the exact model to the existing explicit provider admission policy only after the operator verifies the account and terms.
4. Dispatch through the existing QUE task identity and record one request outcome per dispatch.
5. Normalize usage/quota headers or provider-returned account-independent counters; preserve null for absent values.
6. Append provenance and HindSight records, then regenerate the existing quota, usage, availability, and task-correlation feeds.
7. Validate the resulting SHE/Tribute projections against source hashes and workflow receipts.

The catalog harvester is implemented as a bounded read-only source adapter. The inference request path and live usage/quota counters remain separate integration work; model discovery alone does not assert that either has executed.
