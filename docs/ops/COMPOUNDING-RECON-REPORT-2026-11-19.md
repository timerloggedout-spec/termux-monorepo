# Compounding Systems RECON — detailed report and implementation proposal

**Repository:** `timerloggedout-spec/termux-monorepo`  
**Snapshot:** 2026-11-19, GitHub repository head observed at `c655993c7538f629f8d596c988187ca6e9a23ec1`  
**Scope:** DoE, benchmarks, DeepSeek/Termux provenance, Muse/Hark execution, Temporal, HindSight, ML Ops, refTemplates/smods, MergeEarn, quota attribution, and compounding optimization.

## 1. Executive decision

The repository already contains a substantial operating system for agentic development. The highest-return move is **integration and evidence continuity**, not another parallel scheduler, score plane, telemetry database, or generic benchmark framework.

The recommended programme is:

1. Preserve the existing canonical authorities: AEF for evaluation contracts, DoE for experiment assignment, QUE for admission/leases, Temporal for durable workflow execution where deployed, compute mesh for placement, chat/session provenance for attribution, 3L0 for agent/provider suitability, MoneyBall for economic valuation, ForeSight/HindSight for evidence and memory projections, and WagerTome for the private wagering ledger.
2. Make benchmark coverage multi-domain. SWE-bench remains essential, but Terminal-Bench 4.1 is the immediate terminal complement; BFCL/ToolSandbox cover tool use; BrowserGym/WebArena and OSWorld cover browser/desktop execution; τ²-bench covers policy-constrained tool-agent-user interaction; LongMemEval covers memory; AndroidWorld covers mobile; MLE-bench covers ML engineering; AgentDojo covers adversarial tool security.
3. Join existing DeepSeek/Termux session lineage to the canonical `chat-provenance/v1` feed using stable session/message/dispatch IDs and commit/run evidence. Preserve the distinction between a proven session store and a cohort-specific outcome.
4. Treat Muse's existing Temporal, HindSight, and ML Ops work as live operating context, with the repo's current daily ML Ops receipts as supporting evidence. Capture the exact VM port, process health, cron invocation, and output receipt in a common runtime manifest when a host-side probe is available.
5. Register MergeEarn in the existing agentic-wallet reference-template lineage as an external comparator, while preserving the fleet wallet ledger as the only internal balance/event authority.
6. Reuse the current wait/watch/re-fetch/compare/record discipline and automated QUE machinery. Add only the missing evidence adapters and crosswalks.

**Implementation in this branch:** a cross-domain benchmark family registry and this report are being added. The existing open Agentic Wallet template PR #4737 is being extended with MergeEarn source registration. No PR is merged and no production VM, schedule, credential, or runtime configuration is changed by this documentation pass.

## 2. Evidence model and collection boundaries

This report uses the following state labels:

| Label | Meaning |
|---|---|
| **VERIFIED** | Direct repository file, commit, PR, or run receipt supports the statement. |
| **OWNER-REPORTED** | Explicit operating fact supplied by the repository owner; accepted as current context but still awaiting a host-side receipt where one is needed. |
| **WIRED** | Automation or contract exists; execution must be proven separately. |
| **EXECUTED** | A specific run receipt or commit proves an execution. |
| **CANDIDATE** | Identified as useful; no production adapter/execution claim. |
| **GAP** | Evidence or integration needed to close the loop. |
| **STALE / CONFLICTED** | Existing sources disagree or a timestamp/lease requires a fresh observation. |

The inspected repository snapshot is `c655993c7538f629f8d596c988187ca6e9a23ec1`. The latest accountability receipt added at that head records a successful sweep for the checked-out `master` ref, with 26,269 reachable commits and complete Git-history coverage for that ref. Its `expected` count is null and its scope explicitly distinguishes repository history from external-source census; it is not a claim that every external system or private VM history is complete.

GitHub search and fetch were used for the paths and PRs cited below. External benchmark release details were checked against the linked benchmark owners and publishers on 2026-11-19. A connected Termux device MCP and a direct Muse VM shell/health connector were not available in this session, so device memory pressure, live listener port, process tree, VM cron daemon state, and current Hark/Muse host telemetry were not independently probed here.

## 3. Verified existing architecture

### 3.1 Evaluation and experiment planes

**VERIFIED — AEF is already the broad evaluation taxonomy.**  
`docs/architecture/AGENT-EVALUATION-FRAMEWORK.md` defines SWE-agent treatments, SWE-bench, repository-history replay, custom environments, deterministic regression, trajectory validation, tool/API boundaries, cognitive regression, oversight/security, patch quality, long-horizon stability, adversarial robustness, orchestration, provider/model, manager/team policies, and scout selection.

**VERIFIED — the SWE cohort registry is more than a single benchmark.**  
`docs/evaluations/swe-performance/COHORTS.md` names Full, Lite, Verified, Multimodal, Multilingual, and Live cohorts; it separates external SWE treatment signals from repository-local development performance. The mini-SWE fork is a bounded reference adapter with a pinned revision. The full SWE-agent fork is a reference treatment candidate. A task execution and a benchmark-resolved result remain distinct states.

**VERIFIED — DoE has a broader family model.**  
`docs/ops/DOE-FAMILY.md` defines one experiment record per dispatched run, with configured instance fields for provider, model version, prompt/tool references and hashes, role, moniker, context, and instance key. MVT is one member of the DoE family, not the entire experiment system. The registered Delphi research population and broader provider/model/endpoint/agent/orchestrator cohorts must remain distinct populations.

**VERIFIED — 3L0 and MoneyBall remain separate.**  
`docs/ops/3L0-PLANE.md` defines the scoring plane for agents/models/providers/scouts/orchestrators/collaborators and consumes committed telemetry. `docs/ops/MONEYBALL-PLANE.md` defines a separate economic valuation plane. The documented 3L0 weighting relationship may consume MoneyBall-derived quota multipliers, but the two records and authorities are not merged.

### 3.2 Session and execution provenance

**VERIFIED — canonical chat provenance is implemented.**  
The emitter `scripts/telemetry_ingest/session_history.py` transforms per-surface rows into `chat-provenance/v1`, appending emit-once records to `ops/telemetry/session-history.jsonl`. The schema uses stable `sess:<chat_id>:<message_id>` dispatch IDs, scrubs credential-shaped values before hashing/writing, records route limitations, and keeps missing outcomes observational.

**VERIFIED — the initial population is 614 records.**  
`ops/telemetry/session-history-receipt.json` records 15 Muse DB export rows plus 599 PR-artifact backfill rows, 614 total, 52 null actors, two redactions, and 599 mappings into 3L0 as observational. The receipt names the session store origin as DeepCLI `core.py` webWrapper machinery. This count is not 614 confirmed DeepSeek API sessions or 614 successful dispatches.

**VERIFIED — DeepSeek session machinery has earlier history.**  
Commit `40683687b1bf50d70c74d6eb2426767f1f8836f8` (PR #174, 2026-08-13) wired the DeepSeek web-wrapper into GitHub Actions with session caching, account-aware session management, and chat-session IDs. Commit `3ebfbd4130e16fb32ff691bbbc50af9fe7665082` (PR #216, 2026-08-14) extended persistent session fidelity. The canonical provenance pipeline landed in PR #3453 / commit `6050e1975ae5dabdb3b5751af7a8ad6ac016b5de` on 2026-11-01; the session-store origin was recorded by PR #3625 / commit `1e898b4606cbe1de01fa6f848e2ad6a3f10e4309`.

**GAP — exact Termux Origin / DeepSeek cohort join.**  
The repo proves DeepSeek web-wrapper session machinery and a general canonical session-history pipeline. The inspected receipt explicitly names the DeepCLI webWrapper store but does not separately enumerate DeepSeek-origin rows, Termux Origin device IDs, or a provider-specific successful-outcome cohort. The next join should search historical commits/branches and Termux-origin exports for session IDs, message IDs, commit SHAs, workflow IDs, and event timestamps; map eligible records into the canonical feed without re-emitting existing dispatch IDs. Keep source lineage and uncertainty attached. This is a continuity/reconciliation task, not a rebuild of provenance telemetry.

**VERIFIED — shared PAT attribution has a known limit.**  
`docs/ops/QUOTA-ATTRIBUTION.md` states that GitHub's shared user-principal quota bucket cannot identify which agent/lane consumed a call. A consumer key must be attached at requisition time. GitHub actor identity is not proof of agent identity.

### 3.3 Muse, Hark, Temporal, HindSight, and ML Ops

**VERIFIED — the compute allocation is explicit.**  
`ops/compute/ALLOCATION.md` (2026-11-18) assigns:
- Muse VM to Temporal/staging/registry cadence, MiroFish/OASIS pilot orchestration, BRR, pool refresh, endpoints DB rebuild, weekly Linguist corpus runs, classifier replication, daily HindSight + ML Ops, and chunked Jules publish/harvest work.
- Hark VM to bounded export cadence and isolated compute.
- GitHub Actions to QUE machinery, bounded dispatch, and gates.
- Workers/Deno/Lambda/Cloud Run to request-shaped slices.
- The inference pool to model inference.

**VERIFIED — daily ML Ops receipts exist through November 19.**  
`ops/ml/local-runs.jsonl` contains:
- `vm-mlops-daily-20261117-055414`: `ml-ops-smoke` result `pass`.
- `vm-mlops-daily-20261118-055414`: `unchanged`.
- `vm-mlops-daily-20261119-055414`: `unchanged`.

`ops/compute/BACKLOG.md` records `vm-mlops-daily` as running daily and places the hourly mesh probe on VM cron + Actions. An `unchanged` result is a valid idempotent outcome, not evidence of failure or a new model-quality pass.

**OWNER-REPORTED — Temporal, HindSight, and ML Ops have executed on Muse.**  
The owner confirms that these workloads have run on Muse; one earlier test consumed GitHub compute quota. The current allocation and daily receipts corroborate the continuing Muse workload context. This report treats those workloads as existing operations, not greenfield proposals.

**OWNER-REPORTED — HindSight runs on a Muse VM port with cron export.**  
The exact port, listener health, cron command, last successful export timestamp, and output digest require a live Muse-side receipt. The repository documents the daily job and telemetry payloads, but the inspected material does not establish the current port number or current process health.

**GAP — runtime receipt unification.**  
Use a common run envelope across Muse cron, Temporal workflow history, Actions runs, and HindSight export. Each daily job should emit a small receipt with `job_id`, `run_id`, `started_at`, `ended_at`, `host_id`, `source_sha`, `workflow_id`, `status`, `input_digest`, `output_digest`, `export_uri`, and `health_probe`. Keep host secrets and raw private session content outside the public repo.

**STALE / CONFLICTED — Hark capacity card.**  
The current `ops/compute/ALLOCATION.md` describes Hark as the same class as Muse (4 vCPU EPYC / ~8 GB RAM), while the previously inspected Hark node evidence described a 2 vCPU ARM64 host with approximately 7.8 GiB RAM. A current node probe should resolve host identity and capacity before allocation. The allocation file also carries a Hark seat cap ending 2026-11-19 00:46 PT; current lease status needs a fresh receipt.

**VERIFIED — Temporal adoption has several parallel proposal artifacts.**  
`docs/rfps/temporal-durable-execution/RECON.md` and the active Temporal proposal packs describe Temporal as the durable time plane, with P1 smoke / proposal maturity in the cited snapshots. Current Muse workload allocation and owner-reported execution are compatible with this; they establish runtime use, while the Temporal platform integration maturity and durable worker-kill/resume proof remain separate gates. The RFP's own exit criteria require a kill-resume harness and exactly one receipt after a mid-activity worker kill.

**VERIFIED — current compute backlog has real queued work.**  
`ops/compute/BACKLOG.md` records the first provider stress-test wave fired across eight providers, clf-lab Tier 1 replicated on Muse at 12/12 cells, 3,443 unmapped endpoint DB rows measured, daily ML Ops/HindSight census, and probe-watch cadence. Other items remain queued, stalled, or unbuilt. This is an active portfolio, not an empty architecture diagram.

### 3.4 Reference templates and MergeEarn

**VERIFIED — PR #4737 already contains the fleet-native Agentic Wallet template.**  
PR #4737, `feat/agentic-wallet-template`, is open, not merged, and mergeable at the inspected snapshot. It adds:
- `refTemplates/00_Index/README.md` registration,
- `refTemplates/01_Agent_Runtime/README.md` family registration,
- `refTemplates/01_Agent_Runtime/agentic-wallet/README.md`,
- `SPEC.md`, and
- `SOURCE.txt`.

The spec uses the existing hash-chained wallet ledger, provisioning set, and `scripts/moneyball/wallet_ledger.py` fold/verify/sweep tooling. It specifies `soft_quota_token` as observational and explicitly excludes chain/mainnet legs, key custody, and real-money authority.

**OWNER-REPORTED — MergeEarn has already informed wallet-template use.**  
This is recorded as owner-reported prior use. The upstream MergeEarn repository and PR #76 provide external product/contribution and bounty-flow context; PR #76 itself is open and unmerged at the inspected snapshot. Its existence does not establish external payout correctness or fleet code adoption.

**IMPLEMENTED ON PR BRANCH — MergeEarn source registration.**  
This session adds MergeEarn to the Agentic Wallet `SOURCE.txt`, README, and `refTemplates/00_Index/SOURCE-MAP.md` on the existing PR #4737 branch. The wording registers it as an external bounty/work-funding/payout-flow comparator and explicitly preserves the fleet wallet ledger as the internal source of record. The PR branch remains unmerged; registration becomes part of master only after review and merge.

### 3.5 Compute and automation operating model

**VERIFIED — system-managed work already exists.**  
The repository has QUE intake/admission machinery, Temporal proposal and staging references, Muse VM daily jobs, Hark request/receipt stores, Actions orchestration, scheduled telemetry ingest, and the `adaptive-wait` / `production-reconciliation` skill discipline. The proper lifecycle is system-managed scheduling, admission, dispatch, placement, retry, checkpointing, export, and recovery. Manual dispatch is an entry mechanism.

**GAP — cross-surface scheduler/receipt join.**  
The repository has multiple schedules and stores. The highest-value missing layer is a common job/attempt identity and one status projection across QUE, Temporal, Muse/Hark cron, Actions, and output exports. This should be implemented as adapters into existing machinery, not as a new scheduler.

**GAP — retry/recovery semantics must remain side-effect aware.**  
The Temporal proposal explicitly calls out worker death and unknown side effects. A started-but-unrecorded side effect must be reconciled before retry. Every retry must link to its parent attempt, and a terminal success must have a verifier or business receipt.

## 4. What exists beyond SWE

SWE-bench measures software issue-to-patch resolution. It cannot stand in for all agent capability. The new `docs/evaluations/BENCHMARK-FAMILY-REGISTRY.md` registers the broader portfolio and native score semantics.

The highest-leverage additions are:

- **Terminal-Bench 4.1:** terminal-native work and systems tasks; immediate next adapter. The 4.1 release is verifier-focused: it re-grades stored 4.0 trials with more robust reward-hack resistance and correctness. Preserve 4.0 observations and 4.1 regrades as linked records.
- **BFCL v4 + ToolSandbox:** function-call accuracy, schema/argument correctness, multi-turn stateful tools, and intermediate/final state validation.
- **BrowserGym + WebArena / WebArena-Verified / WorkArena:** browser and web-app workflows with self-hosted task state.
- **OSWorld:** desktop and cross-application computer-use tasks; separate VM/GUI environment required.
- **τ²-bench:** user-agent-tool interactions under policy and changing backend state, with text and voice variants.
- **LongMemEval / V2:** memory retrieval, temporal reasoning, knowledge updates, abstention, and query latency; especially relevant to HindSight and ForeSight.
- **AndroidWorld:** mobile workflows on an Android emulator; relevant to Termux and device-agent work.
- **MLE-bench:** ML engineering competitions; relevant to ML Ops, but resource-intensive and with upstream leaderboard submissions paused in the cited April 2026 update.
- **AgentDojo:** prompt-injection and defense evaluations; security-isolated.
- **GAIA / AgentBench / Terminal-Bench-Science:** broad assistant, multi-environment, and scientific workflow coverage.

These families should enter the registry as **CANDIDATE** or **RESEARCH**, then graduate to **WIRED** and **EXECUTED** only with pinned environments, adapter tests, and receipts. The registry explicitly records score semantics and version/regrade constraints.

## 5. Compounding architecture

### 5.1 One evidence unit, many consumers

The central optimization is to make one verified execution useful across many downstream systems without copying its authority or duplicating its raw data.

```text
Task / seed registry
      │
      ▼
DoE preregistration ── arm / cohort / seed / stop rule
      │
      ▼
QUE admission + lease
      │
      ▼
Temporal workflow / bounded worker
      │
      ├── Muse VM: durable and scheduled workloads
      ├── Hark VM: bounded isolated slices and exports
      ├── Actions: triggers, gates, and orchestration
      └── inference pool: model calls
      │
      ▼
Canonical run receipt + chat/session provenance
      │
      ├── benchmark-native result
      ├── ForeSight / HindSight evidence projection
      ├── 3L0 confirmed outcome and suitability
      ├── MoneyBall valuation and quota economics
      ├── WagerTome expectation / settlement references
      ├── failure and regression corpus
      └── refTemplates / skill evolution candidate
      │
      ▼
Blind review → replicated winner → promote / retain / cull
      │
      └── next DoE cohort
```

This is a projection architecture: each consumer reads a shared evidence identity and applies its own authority rules. The canonical run receipt and source artifacts remain the record; dashboards and score planes are derived views.

### 5.2 Highest-value compounding multipliers

| Multiplier | Reuse mechanism | Compounding effect |
|---|---|---|
| Task identity | One task fingerprint across SWE, terminal, tool, browser, and internal tasks | Reuse fixtures, regression history, environment setup, and failure diagnosis |
| Provenance | One dispatch/session/attempt lineage with source commit and model/tool hashes | Attribution supports DoE, 3L0, quota, benchmark replay, and audit |
| Compute admission | One QUE admission/lease and common placement receipt | Less duplicate scheduling, clearer capacity, safer reallocation |
| Durable execution | Temporal history + checkpoints + idempotent attempts | Long jobs survive worker loss and avoid duplicate side effects |
| Failure corpus | One classified failure artifact linked to task/version/agent | Fixes become regression tests and future task seeds |
| Template promotion | Verified winning treatment becomes a refTemplate/skill candidate | Repeatable improvements propagate to future lanes |
| Memory evidence | HindSight/ForeSight consume redacted, provenance-backed records | Research and operations benefit from existing work history |
| Quota economics | Requisition-time consumer IDs and usage receipts | Routing decisions account for true cost without guessing from shared PAT usage |
| Research/Delphi | Independent hypotheses, seeds, replications, and evidence | Decisions become more robust and reduce one-off optimization |
| Exports and restore | Content-addressed export manifest + restore receipt | Compute and telemetry state becomes portable across hosts |

### 5.3 Efficiency levers

1. **Use cache-stable prompts.** Keep stable instructions/context first and variable task data last to improve provider-side prefix caching where supported. Record cached and uncached token counts separately.
2. **Match workload to substrate.** Run durable, recurring, CPU-bound jobs on Muse; use Hark for bounded isolated work only after current capacity/lease verification; use Actions for orchestration and short CI slices; use inference endpoints for inference rather than orchestration.
3. **Batch independent units.** Group by task family, provider, environment image, and resource profile; cap concurrency against host memory and provider quota. Retain one result per task/attempt.
4. **Checkpoint long work.** Persist progress at bounded intervals and resume from immutable checkpoint references. Treat side-effect uncertainty as a reconciliation state.
5. **Avoid duplicate evaluation.** Reuse an artifact for a verifier-only regrade when the benchmark allows it; record the regrade as a new observation linked to the original run. Terminal-Bench 4.1 is a current example.
6. **Keep native metrics.** Optimize a Pareto set across success, latency, tokens, cost, retries, interventions, and long-horizon reliability. Do not hide trade-offs inside an opaque composite.
7. **Promote only replicated gains.** Require preregistration, multiple seeds/replicates, blinded evaluation where practical, independent verification, and no regressions on deterministic internal controls.
8. **Make schedules idempotent.** Stable job keys, leases, run IDs, output digests, and unchanged receipts reduce redundant work and make recurring systems self-maintaining.

## 6. Recommended execution roadmap

### P0 — continuity and integrity

- Reconcile DeepSeek/Termux Origin history with the existing DeepCLI session-store and `chat-provenance/v1` pipeline.
- Join `session-history`, 3L0 mappings, workflow run IDs, provider/model identity, and confirmed outcomes using immutable IDs.
- Capture Muse HindSight listener/cron/health/export receipts through the existing VM mechanism.
- Resolve Hark capacity and lease conflicts with a live node probe.
- Standardize the run envelope across Muse cron, Temporal, Actions, and Hark exports.

### P1 — high-return benchmark coverage

- Implement a pinned Terminal-Bench 4.1 adapter using Harbor/RewardKit and isolated verifier execution.
- Add BFCL v4 and ToolSandbox tool-use tracks with task-level quality annotations.
- Build a BrowserGym adapter for WebArena / WebArena-Verified before adding separate browser harnesses.
- Preserve SWE-bench as its own coding-resolution track; do not conflate scores.

### P2 — memory, GUI, mobile, and policy

- Add LongMemEval/V2 memory tests against HindSight/ForeSight projections.
- Add OSWorld and AndroidWorld only after dedicated environment, reset, and resource gates.
- Add τ²-bench policy-constrained tool-agent tests.
- Add AgentDojo in isolated security test environments.

### P3 — learning and promotion

- Use DoE to compare agent/provider/tool/manager treatments on matched task fingerprints.
- Feed only confirmed outcomes to 3L0; feed verified cost/benefit evidence to MoneyBall.
- Turn repeatable failure classes into regression tests and new task seeds.
- Promote verified winners into refTemplates and reusable skills with source lineage and version pins.
- Cull treatments only after the registered stopping rule and evidence review.

## 7. Acceptance criteria for the programme

The programme is complete when:

- Every scheduled job has a stable identity, owner, cadence, lease, and terminal receipt.
- Every dispatched evaluation has one DoE record, task fingerprint, treatment identity, and immutable artifact references.
- Every result states its benchmark version and native metric semantics.
- DeepSeek/Termux session provenance joins are idempotent and preserve source identity, attribution evidence, and confirmed-outcome boundaries.
- Muse HindSight and ML Ops daily runs emit comparable health and export receipts.
- Temporal worker-loss/resume and unknown-side-effect cases have a tested durable-execution contract.
- Hark and Muse capacity cards reconcile with current node receipts.
- MergeEarn is registered in the agentic-wallet source lineage and remains a comparator rather than an internal ledger authority.
- Benchmark adapters pass fixture, isolation, verifier, retry, resume, and redaction tests before admission.
- 3L0, MoneyBall, ForeSight/HindSight, WagerTome, and benchmark-native results remain separate authorities joined by evidence references.
- Promotion records show replication, independent verification, and regression status.

## 8. Current implementation and outstanding work

| Work item | State in this pass | Evidence / next step |
|---|---|---|
| Benchmark family registry | **IMPLEMENTED on this branch** | `docs/evaluations/BENCHMARK-FAMILY-REGISTRY.md`; PR CI and review remain |
| Detailed compounding RECON report | **IMPLEMENTED on this branch** | This document; refresh after runtime probes |
| MergeEarn refTemplates lineage | **IMPLEMENTED on PR #4737 branch** | SOURCE.txt, wallet README, SOURCE-MAP updated; PR remains unmerged |
| DeepSeek Termux-origin join | **GAP / planned** | Recover historical branch/commit/session records and map eligible records |
| Muse port + cron receipt | **OWNER-REPORTED + partially corroborated** | Daily ML Ops receipts exist; exact listener/cron health receipt remains |
| Hark capacity reconciliation | **STALE / CONFLICTED** | Current node probe required |
| Terminal-Bench 4.1 adapter | **CANDIDATE** | Add adapter and isolated verifier harness |
| Tool/browser/GUI/memory/mobile adapters | **CANDIDATE** | Sequence by P1/P2 roadmap |
| Unified runtime scheduler identity | **GAP** | Extend QUE/Temporal receipts; do not add a parallel scheduler |

## 9. Evidence references

Repository:
- [AEF](../architecture/AGENT-EVALUATION-FRAMEWORK.md)
- [SWE cohort registry](../evaluations/swe-performance/COHORTS.md)
- [DoE family](DOE-FAMILY.md)
- [3L0 plane](3L0-PLANE.md)
- [MoneyBall plane](MONEYBALL-PLANE.md)
- [Chat provenance](CHAT-PROVENANCE.md)
- [Compute allocation](../../ops/compute/ALLOCATION.md)
- [Compute backlog](../../ops/compute/BACKLOG.md)
- [ML Ops local receipts](../../ops/ml/local-runs.jsonl)
- [Temporal durable execution RECON](../rfps/temporal-durable-execution/RECON.md)
- [Reference template consolidation](REFTEMPLATES-CONSOLIDATION.md)
- [Agentic Wallet template PR #4737](https://github.com/timerloggedout-spec/termux-monorepo/pull/4737)
- [DeepSeek web-wrapper session commit / PR #174](https://github.com/timerloggedout-spec/termux-monorepo/commit/40683687b1bf50d70c74d6eb2426767f1f8836f8)
- [Canonical session provenance commit / PR #3453](https://github.com/timerloggedout-spec/termux-monorepo/commit/6050e1975ae5dabdb3b5751af7a8ad6ac016b5de)
- [DeepCLI session-store origin commit / PR #3625](https://github.com/timerloggedout-spec/termux-monorepo/commit/1e898b4606cbe1de01fa6f848e2ad6a3f10e4309)
- [MergeEarn upstream](https://github.com/Saidur-droid/MergeEarn)

External benchmark sources are collected in [BENCHMARK-FAMILY-REGISTRY.md](../evaluations/BENCHMARK-FAMILY-REGISTRY.md).

## 10. Decision summary

The best compounding path is to turn the repository's existing work into one evidence-linked lifecycle. The first concrete additions are the benchmark-family registry, the detailed operating report, and MergeEarn's explicit source registration in the existing Agentic Wallet PR. The next engineering slices are provenance continuity, Muse runtime receipts, Terminal-Bench 4.1, and a common job/attempt envelope. Existing authorities remain intact; new adapters increase the number of useful consumers per verified execution.
