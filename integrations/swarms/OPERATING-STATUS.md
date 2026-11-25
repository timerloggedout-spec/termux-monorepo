# Swarms: what runs and what is still missing

## THUB-017 / MSM-005 implementation continuation (unmerged, undeployed)

The candidate now implements the gaps described in the historical snapshot below: genuine hash-verified AdvancedResearch orchestration with bounded injected dependencies, shared durable hub quota admission/reservation/reconciliation, correlated Python/Rust child requests and existing 3L0 evidence ingestion, and integer paper accounting in the existing MarketGraph event journal. See [the implemented runtime](ADVANCED-RESEARCH.md) and [shared hub contract](../../llm_api_hub/RESEARCH-CORRELATION-CONTRACT.md). The offline planner remains a planner. Deterministic tests use fake inference/search only. Linux validation is not native Android evidence; no live provider, paid fallback, merge or deployment is claimed. Exact-candidate Actions receipts are the remote evidence surface, not this status text.

GitHub API snapshot checked 2026-11-25 19:31Z: PR #1470 is open/unmerged at head `5e57dcd3d1e8d2a417ad213cdf96622d126df7cf`; its API reports base SHA `5e9e5d0fa8c83f1c250cf7675e900348b85f81e4` and unknown mergeability, while the live `master` ref is `ecf3e59f9214d6403ad2d769af1ecad8c820d065`. A fresh #1540 API recheck at 19:32Z reports `merged=true`, merge commit `2791d2aacddd01d253e772715a1b07aeebdee351`, merged at `2026-11-13T16:57:36Z`; that commit is an ancestor of #1470. PR #1541 is open/unmerged and dirty/non-mergeable at head `e9fb8f1d813f9ca8e89f5df7de29a329afdba034`; its API reports base SHA `d2778bcc25966533ccd2f5bc1991aab672fb9cbe`, while its named base branch ref is at #1470's `5e57dcd3d1e8d2a417ad213cdf96622d126df7cf` head. The local candidate then had a non-committing merge of that exact #1470 head; this does not establish that the remote PR head already contains it. No merge or deployment is claimed. #1531 records proposals. Native tracking is #1520/#1522–#1525 and #1521/#1526–#1529. The MSM-005 journal stores existing market events plus paper issuance/reserve/settle/release/void/expiry; MSM-012 remains a rebuildable CSV, never authority. Restart, contention, idempotency, conservation, four wager/offer scopes and stale/edited CSV are tested. CSV cannot authorize settlement or create points.

## Existing registries and adjacent subsystem map

This is a source map, not a new registry, ledger, or owner assignment. Kye Gomez remains the Swarms behavioral origin. The repository evidence reviewed does not verify the estimate of 130+ provider mappings or thousands of inference endpoints; keep unknown owners and runtime status explicit.

| Surface | Existing source and verified boundary | Owner / status |
|---|---|---|
| Runtime quota and provider index | [`ops/quota/registry.json`](../../ops/quota/registry.json) is the runtime quota/service registry used with [shared hub admission](../../llm_api_hub/RESEARCH-CORRELATION-CONTRACT.md). [`docs/icm/routing/providers/registry.md`](../../docs/icm/routing/providers/registry.md) is a governance index, not runtime provider configuration. | No runtime registry owner is explicitly named in these sources; inventory completeness is unverified. |
| Resource catalog | [`docs/research/resource-registry.yaml`](../../docs/research/resource-registry.yaml) and `data/foresight/resource-registry.jsonl` catalog research resources/evidence; they are not quota authorities or participant rosters. | No roster owner found. |
| DoE participant pools | [`dspy_doe.py`](../../scripts/model_selection_market/dspy_doe.py) records caller-supplied tasks, arms, factors, and outcomes; it does not select or enroll a participant pool. MSM-005 cull/pool events in [`MarketGraph`](../../scripts/model_selection_market/market.py) are paper-account lifecycle, not experimental cohorts. | No DoE participant roster or explicit owner found. |
| ATES | [`ATES-ORCHESTRATOR-DOE-MVT.md`](../../docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md) and the [`ATES reducer`](../../she/metrics/ates_orchestrator.py) describe observational evidence/reduction, not provider inventory or quota control. Production cohort-to-receipt linkage is unverified. | No explicit individual owner found. |
| Temporal / Hindsight | [`_v1_hindsight.py`](../../deepcli/_v1_hindsight.py) implements retain/recall/reflect memory; no Temporal workflow-engine integration was found. The server references `deepcli/_v1_hindsight_router.py`, which is absent; finish-path retain and shared quota admission are unverified. | No explicit owner or deployed runtime found. |
| Bifrost | [`mcp-hub/catalog.json`](../../mcp-hub/catalog.json), the Bifrost proposal, and the [routing orchestration map](../../docs/ops/ROUTING-ORCHESTRATION-MAP.md) document a catalog/evaluation lane; no in-repository Bifrost runtime was found. A mocker smoke is not a Bifrost run. | Proposal metadata names Grok as author/executor, not the runtime owner; production use is unverified. |
| Telemetry | [`TermuxTelemetryLogger`](../../src/telemetry.py), [`research_evidence.py`](../../scripts/telemetry/research_evidence.py), and the [`OTel-shaped projection`](../../she/telemetry/otel_projection.py) feed/map existing evidence; the projection is not an external exporter. Local fixture evidence is not live-provider or deployed end-to-end proof. | No explicit subsystem owner, external exporter, or deployment found. |
| Paper wallet | [`MarketGraph`](../../scripts/model_selection_market/market.py) is the canonical MSM-005 event journal; [`paper_wallet.py`](../../scripts/model_selection_market/paper_wallet.py) is a rebuildable CSV view (MSM-012), not a second ledger. | Canonical ownership remains the MSM-005 proposal lane; no separate wallet authority is introduced. |

## Historical foundation snapshot


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
