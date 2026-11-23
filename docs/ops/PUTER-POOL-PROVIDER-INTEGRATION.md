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


## Runtime observation and Temporal execution

The source repository is harvested separately from the local runtime. Run
`python3 scripts/puter_pool_repo_harvest.py --repo-root /path/to/puter-pool_fork`
to produce an allowlisted source manifest with commit identity, file hashes,
route names, SQLite table names, and event names. The manifest excludes
`.env`, SQLite files, browser storage, account credentials, and request bodies.

Run `python3 scripts/puter_pool_catalog.py` for model discovery and
`python3 scripts/puter_pool_observation.py` for a privacy-minimized runtime
snapshot. Configure `PUTER_POOL_BASE_URL` to a loopback origin and
`PUTER_POOL_API_KEY` in the worker environment. The observer reads only
`/v1/models`, `/api/stats`, `/api/queue`, `/healthz`, and `/readyz`.
It excludes account inventories, account balances, history rows, prompts,
completions, browser storage, and credentials from all outputs.

### Temporal loop

Install the existing Temporal SDK dependency with `python3 -m pip install 'temporalio>=1.7.0'`.
Start the worker with
`python3 -m scripts.temporal.puter_pool_observation.worker --address localhost:7233`.
Start the durable workflow with
`python3 -m scripts.temporal.puter_pool_observation.start --task-or-entry-ref QUE-<entry> --doe-run-id <doe-run> --workflow-run-id <workflow-run> --run-attempt 1 --interval-seconds 300`.
The workflow runs every 300 seconds by default and accepts a Temporal `stop` signal.
Each activity appends one EPS v1 event to `agent_telemetry_stream.json` with
provider identity, task/entry, DoE run, Temporal workflow/run, workflow-run
attempt, model count, aggregate request outcomes, queue depth, latency, and
readiness. Event attributes contain aggregate operational metadata only.

### Downstream feed contract

`agent_telemetry_stream.json` is the existing source consumed by
`scripts/telemetry_ingest/ingest.py`. Its provider field normalizes to
`g4f-puter`, joining the existing `g4f.puter` quota registry row and
Provenance/HindSight payload generation. Witness consumes the provenance
evidence spine; Temporal owns durable cadence and correlation; HindSight
receives sanitized retention payloads; Bifrost, n8n, Platform201, and the
SHE/Tribute interfaces consume the normalized telemetry/quota projections.
The dashboard quota record retains `used=null`, `limit=null`, and
`reset=null` until provider-authoritative quota data is observed. Puter Pool's
local `CreditTracker` is an account-count heuristic and remains excluded from
provider quota calculations.

The workflow writes to the operator's local checkout. The existing
telemetry-ingest pipeline then folds the appended events into the provenance
ledger, HindSight payloads, and downstream projections; operator deployment
must keep the Temporal worker and Puter Pool service on the same host or
network namespace so the loopback endpoint resolves locally.
