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

Each Puter Pool inference dispatch now emits a per-request EPS v1 event to
`agent_telemetry_stream.json`. The LLM Hub reads correlation headers
`x-task-or-entry-ref` (or `x-que-entry`), `x-doe-run-id`,
`x-workflow-run-id`, `x-run-attempt`, `x-temporal-workflow-id`,
`x-temporal-run-id`, and `x-request-id`. The Temporal observer separately emits
aggregate `provider.pool.observed` events. Both join existing identifiers:

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
3. Add the exact model to the existing explicit provider admission policy after the operator verifies the account and terms.
4. Dispatch through `puter_pool/<exact-model-id>` with QUE/DoE/Temporal correlation headers; the LLM Hub emits one sanitized outcome event per request.
5. Preserve response token counts and aggregate pool counters where supplied; keep provider quota fields null until authoritative quota evidence exists.
6. Append provenance and HindSight records, then regenerate the existing quota, usage, availability, and task-correlation feeds.
7. Validate the resulting SHE/Tribute projections against source hashes and workflow receipts.

The canonical catalog adapter, loopback inference transport, per-request EPS emitter,
aggregate runtime observer, and Temporal cadence are implemented. Exact model
admission remains explicit: the existing provider policy must contain the exact
catalog model with operator-verified free-account and terms assertions. The
Puter registry row keeps `runtime_eligible=false` until a real inference receipt
is observed. Catalog discovery and transport support alone do not activate a
model. Provider-authoritative quota remains unknown; the local CreditTracker
heuristic is excluded from quota calculations.


## Runtime observation and Temporal execution

The source repository is harvested separately from the local runtime. Run
`python3 scripts/puter_pool_repo_harvest.py --repo-root /path/to/puter-pool_fork`
to produce an allowlisted source manifest with commit identity, file hashes,
route names, SQLite table names, and event names. The manifest excludes
`.env`, SQLite files, browser storage, account credentials, and request bodies.

Run `python3 scripts/provider_model_catalog.py --providers puter_pool --output /tmp/provider-model-catalog/puter-pool.json` to harvest into the canonical provider model catalog; the `puter_pool` rows join `provider_id=g4f.puter` and `provider_family=g4f/Puter`. Run `python3 scripts/puter_pool_catalog.py` for the focused local model inventory and
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
Send the signal with `temporal workflow signal --workflow-id <workflow-id> --name stop --address localhost:7233`.
Each activity appends one EPS v1 event to `agent_telemetry_stream.json` and writes
the current aggregate snapshot to `apps/tribute-dashboard/data/puter-pool-runtime.json` with
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
