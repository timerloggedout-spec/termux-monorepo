# Swarms: what runs and what is still missing

## The short answer

The Python and Rust Swarms entry points can explicitly execute agent workflows through the existing model hub. Neither is an automatically deployed service. **AdvancedResearch is registered for investigation, not integrated or running. Quota Management and 3L0 do not yet receive correlated Swarms execution evidence through these adapters.** Paper wallets are CSV projections of MSM-005, not blockchain wallets.

This audit traces the PR #1470 base `ad5d100d`, its adapters, the hub client/server and the existing quota/telemetry contracts. It is code evidence, not a live provider or deployment receipt.

## How agents are called

```sh
# Offline: no SDK import, model request, or agent execution.
python3 scripts/swarms/run.py --task 'Analyze supplied evidence'
python3 scripts/swarms/run-rust.py --task 'Analyze supplied evidence'

# Explicit execution, after installing/configuring the selected backend and hub.
python3 scripts/swarms/run.py --task 'Analyze supplied evidence' \
  --model 'your-configured-hub-route' --execute
python3 scripts/swarms/run-rust.py --task 'Analyze supplied evidence' \
  --model 'your-configured-hub-route' --execute
```

The [Python adapter](../../src/swarms_adapter.py) creates Swarms `Agent` instances in a `SequentialWorkflow`: researcher then reviewer, with one or two agents and one to three workflow passes. `_HubLLM.run()` delegates to [the OpenAI-compatible hub client](../../llm_api_hub/clients/openai_compat.py). The [Rust adapter](../../src/swarms_rust_adapter.py) launches the separately built pinned worker against that hub. These are parallel implementations, not demonstrated behavioral parity.

No shell, filesystem tools, MCP tools or autonomous browsing are supplied. The word “researcher” is a role name, not proof that the AdvancedResearch package or its search tools are running. Upstream Python telemetry is deliberately disabled and temporary SDK state is cleaned up; disabling upstream telemetry does not enable local telemetry instead.

## Quota and 3L0: separate lanes, not connected execution

| Boundary | Current behavior | Missing evidence |
|---|---|---|
| Adapter → hub | Explicit model and chat messages; Python extracts assistant text | No per-run/agent/attempt correlation, admission receipt, token/cost accounting or cooldown receipt |
| Hub → provider | [`chat_completions`](../../llm_api_hub/server/app.py) selects configured wrappers/upstreams or explicitly admitted native research providers | Native provider eligibility is not quota reservation. No shared quota admission hook for these swarm requests is established by this slice |
| Quota observation | [`quota_poll.py`](../../scripts/quota_poll.py) writes quota records and `3l0.quota-weights.v1` routing multipliers | These adapters do not consume those records or enforce their freshness/reset/cooldown policy |
| Local telemetry | [`TermuxTelemetryLogger`](../../src/telemetry.py) writes the existing event shape | Neither swarm adapter emits correlated events to it |
| 3L0 export | [`hex_moneyball_export.py`](../../scripts/hex_moneyball_export.py) sanitizes supplied NDJSON into `3l0.moneyball.v1` | No connected Swarms event stream; the current export also does not carry token, cost or quota fields |

A configured hub might have deployment-specific controls, but this code does not prove them. Loop counts, deadlines and token limits are not equivalent to quota admission. A successful model response is not a correctness or learning outcome. No routing weights or performance-ledger outcomes are changed by the paper CSV export.

## Research frameworks remain assigned work

[`research-plan.py`](../../scripts/swarms/research-plan.py) emits `status: planned` and `execution: not_performed`. It does not execute AdvancedResearch. The pinned [AdvancedResearch source](https://github.com/The-Swarm-Corporation/AdvancedResearch/blob/a262cb9d9703681c5a5066f03eb9fb89ad4d9cae/advanced_research/main.py) constructs director/worker agents with provider defaults, loads dotenv at import, supplies Exa tools, and collects concurrent workers in completion order. Importing it unmodified would bypass the existing adapter's explicit-model and state-isolation assumptions.

THUB-017 keeps that integration open. Completion requires an explicit framework boundary, hub-routed director/worker requests, controlled search/tool authority and environment loading, request-level quota admission, correlated outcome/usage receipts, and tests through the existing 3L0 ingestion path. It must not be reported complete because sources were pinned, an offline plan was printed, or a sequential agent was named “researcher.” Paper wallets are not a prerequisite or substitute for this work.

## Paper CSV accounting

MSM-012 derives stake/card/offer rows from an MSM-005 `MarketGraph` snapshot. It adds no chain adapter, signer, RPC, real payment, funded account or second canonical ledger. It does not yet implement a balance-based paper trading engine, reservation or settlement system.

```sh
python3 -m scripts.model_selection_market.market --demo > /tmp/market-snapshot.json
python3 -m scripts.model_selection_market.paper_wallet export \
  /tmp/market-snapshot.json /tmp/paper-wallet.csv
```

The export labels every row paper-only and neutralizes spreadsheet formula-leading strings. Preserve the original snapshot as authority; editing CSV does not mutate the market or change model routing.

## Validation of the paper-scope correction

Local checks: 75 focused pytest tests passed, eight optional SDK/Rust-worker tests skipped because their runtimes are absent; nine existing market unittests passed. The paper snapshot → CSV → view CLI ran successfully. Both repository gates passed locally. These checks do not validate Research execution, live provider requests, quota enforcement or deployment.
