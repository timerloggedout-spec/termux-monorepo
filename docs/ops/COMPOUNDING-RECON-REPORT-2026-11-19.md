# Compounding Systems RECON — detailed report and implementation proposal

**Repository:** `timerloggedout-spec/termux-monorepo`  
**Snapshot:** 2026-11-19, GitHub repository head observed at `c655993c7538f629f8d596c988187ca6e9a23ec1`  
**Scope:** DoE, benchmarks, DeepSeek/Termux provenance, Muse/Hark execution, Temporal, HindSight, ML Ops, refTemplates/smods, MergeEarn, quota attribution, and compounding optimization.

## 1. Executive decision

The repository already contains a substantial operating system for agentic development. The highest-return move is **integration and evidence continuity** across its existing scheduler, score, telemetry, and benchmark systems.

The recommended programme is:

1. Preserve the existing canonical authorities: AEF for evaluation contracts, DoE for experiment assignment, QUE for admission/leases, Temporal for durable workflow execution where deployed, compute mesh for placement, chat/session provenance for attribution, 3L0 for agent/provider suitability, MoneyBall for economic valuation, ForeSight/HindSight for evidence and memory projections, and WagerTome for the private wagering ledger.
2. Make benchmark coverage multi-domain. SWE-bench remains essential, but Terminal-Bench 4.1 is the immediate terminal complement; BFCL/ToolSandbox cover tool use; BrowserGym/WebArena and OSWorld cover browser/desktop execution; τ²-bench covers policy-constrained tool-agent-user interaction; LongMemEval covers memory; AndroidWorld covers mobile; MLE-bench covers ML engineering; AgentDojo covers adversarial tool security.
3. Join existing DeepSeek/Termux session lineage to the canonical `chat-provenance/v1` feed using stable session/message/dispatch IDs and commit/run evidence. Preserve the distinction between a proven session store and a cohort-specific outcome.
4. Treat Muse's existing Temporal, HindSight, and ML Ops work as live operating context, with the repo's current daily ML Ops receipts as supporting evidence. Capture the exact VM port, process health, cron invocation, and output receipt in a common runtime manifest when a host-side probe is available.
5. Register MergeEarn in the existing agentic-wallet reference-template lineage as an external comparator, while preserving the fleet wallet ledger as the only internal balance/event authority.
6. Reuse the current wait/watch/re-fetch/compare/record discipline and automated QUE machinery. Add only the missing evidence adapters and crosswalks.

**Implementation in this branch:** a cross-domain benchmark family registry and this report are being added. Fresh current-base draft PR #5664 carries the Agentic Wallet template and MergeEarn source registration. Both draft PRs remain open; production VM, schedule, credential, and runtime configuration remain unchanged.

## 2. Evidence model and collection boundaries

This report uses the following state labels:

| Label | Meaning |
|---|---|
| **VERIFIED** | Direct repository file, commit, PR, or run receipt supports the statement. |
| **OWNER-REPORTED** | Explicit operating fact supplied by the repository owner; accepted as current context but still awaiting a host-side receipt where one is needed. |
| **WIRED** | Automation or contract exists; execution must be proven separately. |
| **EXECUTED** | A specific run receipt or commit proves an execution. |
| **CANDIDATE** | Identified for adoption; production adapter/execution evidence pending. |
| **GAP** | Evidence or integration needed to close the loop. |
| **STALE / CONFLICTED** | Existing sources disagree or a timestamp/lease requires a fresh observation. |

The inspected repository snapshot is `c655993c7538f629f8d596c988187ca6e9a23ec1`. The latest accountability receipt added at that head records a successful sweep for the checked-out `master` ref, with 26,269 reachable commits and complete Git-history coverage for that ref. Its `expected` count is null and its scope covers the checked-out repository ref; external-source census and private VM history remain separate evidence domains.

GitHub search and fetch supplied the repository paths and PRs cited below. External benchmark release details were checked against benchmark owners and publishers on 2026-11-19. The connected tool set provided GitHub repository access; direct Termux device and Muse VM shell/health probes require their dedicated endpoints. Device memory pressure, live listener port, process tree, VM cron daemon state, and current Hark/Muse host telemetry remain pending host-side receipts.

## 3. Verified existing architecture

### 3.1 Evaluation and experiment planes

**VERIFIED — AEF is already the broad evaluation taxonomy.**  
`docs/architecture/AGENT-EVALUATION-FRAMEWORK.md` defines SWE-agent treatments, SWE-bench, repository-history replay, custom environments, deterministic regression, trajectory validation, tool/API boundaries, cognitive regression, oversight/security, patch quality, long-horizon stability, adversarial robustness, orchestration, provider/model, manager/team policies, and scout selection.

**VERIFIED — the SWE cohort registry is more than a single benchmark.**  
`docs/evaluations/swe-performance/COHORTS.md` names Full, Lite, Verified, Multimodal, Multilingual, and Live cohorts; it separates external SWE treatment signals from repository-local development performance. The mini-SWE fork is a bounded reference adapter with a pinned revision. The full SWE-agent fork is a reference treatment candidate. A task execution and a benchmark-resolved result remain distinct states.

**VERIFIED — DoE has a broader family model.**  
`docs/ops/DOE-FAMILY.md` defines one experiment record per dispatched run, with configured instance fields for provider, model version, prompt/tool references and hashes, role, moniker, context, and instance key. MVT is one member of the broader DoE experiment family. The registered Delphi research population and broader provider/model/endpoint/agent/orchestrator cohorts must remain distinct populations.

**VERIFIED — 3L0 and MoneyBall remain separate.**  
`docs/ops/3L0-PLANE.md` defines the scoring plane for agents/models/providers/scouts/orchestrators/collaborators and consumes committed telemetry. `docs/ops/MONEYBALL-PLANE.md` defines a separate economic valuation plane. The documented 3L0 weighting relationship may consume MoneyBall-derived quota multipliers while the two records and authorities remain separate.

**VERIFIED — TDQS is already integrated locally.**
The repo has `she/metrics/tdqs.py`, `tests/test_tdqs.py`, `docs/ops/TDQS-ADMISSION-MATRIX.md`, and `docs/ops/TDQS-EVIDENCE.schema.json`. The deterministic module handles context signals, hard gates, aggregation, tiers, and server rollups without network/model calls; the six rubric dimensions come from a separately recorded evaluator. The admission matrix already names `gh-mcp`, `termux-mcp`, and `mcp-toolshed_fork` as priority scoring cohorts. Reuse this lane for static tool-definition quality; add task-level MCP benchmarks for behavior. The local implementation declares TDQS v1.3, so keep public rubric-version drift explicit.

### 3.2 Session and execution provenance

**VERIFIED — canonical chat provenance is implemented.**  
The emitter `scripts/telemetry_ingest/session_history.py` transforms per-surface rows into `chat-provenance/v1`, appending emit-once records to `ops/telemetry/session-history.jsonl`. The schema uses stable `sess:<chat_id>:<message_id>` dispatch IDs, scrubs credential-shaped values before hashing/writing, records route limitations, and keeps missing outcomes observational.

**VERIFIED — the initial population is 614 records.**  
`ops/telemetry/session-history-receipt.json` records 15 Muse DB export rows plus 599 PR-artifact backfill rows, 614 total, 52 null actors, two redactions, and 599 mappings into 3L0 as observational. The receipt names the session store origin as DeepCLI `core.py` webWrapper machinery. DeepSeek API attribution and successful dispatch outcomes require their own source joins and outcome receipts.

**VERIFIED — DeepSeek session continuity and capture predate the canonical feed.**  
The DeepSeek web-wrapper CI/session machinery landed in PR #174 / commit `40683687b1bf50d70c74d6eb2426767f1f8836f8` (2026-08-13) with session caching, account-aware session management, and chat-session IDs; PR #216 / commit `3ebfbd4130e16fb32ff691bbbc50af9fe7665082` extended persistent session fidelity. `deepcli/session_store.py` persists a DeepSeek session ID by task identity (hash of path + first 500 characters of task text), tracks runs/last-used metadata, and includes atomic run-state checkpoints. `docs/DEEPSEEK-CAPTURE-PIPELINE.md` documents a webWrapper capture pipeline built and tested locally on a Termux device before this GitHub repo existed. `deepcli/session_manager.py` consumes session/cookie state; `deepcli/ci_mode.py` emits provider account and chat-session ID into the CI run.

**VERIFIED — Termux Origin session-provenance reconstruction exists in owner-original Repo Replay; capture completeness is PARTIAL.**  
The monorepo's `docs/ops/REPO-REPLAY.md` identifies `timerloggedout-spec/repo-replay` as a reconstruction engine whose source of truth is session-chat code exports. Its V4 validator is the device Origin, whose first commit was corrupted; its graduation test rebuilds prior state from Session Provenance mappings. The external `repo-replay/revwright/pipeline.py` records the origin-capture failure: git-init's first add/commit failed and an `rm` removed material, so some early state lacks a durable record. The pipeline marks provenance **PARTIAL** and classifies missing code as `never_in_chat | lost_at_origin_capture | unharvested_provider | drifted_final_edit | UNRESOLVED`. The missing `_session_cache_key` has zero mentions in the harvested corpus and remains **UNRESOLVED**; the source explicitly keeps its cause open. This supports the owner's correction that capture/provenance machinery was established while preserving the origin-loss boundary.

**VERIFIED — the Termux multi-agent logger is a separate, coarser telemetry stream.**  
`termux-multi-agent/src/telemetry.py` appends timestamp, level, agent, target, attempt, and message to `agent_telemetry_stream.json`. It is operational agent telemetry; session IDs, message/block pointers, provider/model identity, and confirmed outcomes come from the dedicated session/provenance sources. Keep this logger as a correlated source.

**VERIFIED — canonical chat provenance is a later normalization layer.**  
The pipeline landed in PR #3453 / commit `6050e1975ae5dabdb3b5751af7a8ad6ac016b5de` on 2026-11-01; the session-store origin was recorded by PR #3625 / commit `1e898b4606cbe1de01fa6f848e2ad6a3f10e4309`.

**GAP — provenance continuity join across established telemetry sources.**  
Join the available DeepSeek session store, Termux Origin exports, Repo Replay objects/index, Git commit history, workflow runs, and canonical `chat-provenance/v1` feed by full session ID, message index/ID, block index, content hash, task identity, workflow/dispatch ID, and timestamps. Preserve 1:N pointers and source-specific gap classifications; emit only missing canonical dispatch IDs. Keep ambiguous source data observational until corroborated. This is a recovery, continuity, and attribution task.

**VERIFIED — shared PAT attribution has a known limit.**  
`docs/ops/QUOTA-ATTRIBUTION.md` establishes that GitHub's shared user-principal bucket reports aggregate usage. Attach a consumer key at requisition time to establish agent/lane attribution; GitHub actor identity remains a separate identity field.

### 3.3 Muse, Hark, Temporal, HindSight, and ML Ops

**VERIFIED — the compute allocation is explicit.**  
`ops/compute/ALLOCATION.md` (2026-11-18) assigns:
- Muse VM to Temporal/staging/registry cadence, MiroFish/OASIS pilot orchestration, BRR, pool refresh, endpoints DB rebuild, weekly Linguist corpus runs, classifier replication, daily HindSight + ML Ops, and chunked Jules publish/harvest work.
- Hark VM to bounded export cadence and isolated compute.
- GitHub Actions to QUE machinery, bounded dispatch, and gates.
- Workers/Deno/Lambda/Cloud Run to request-shaped slices.
- The inference pool to model inference.

**VERIFIED — Muse daily ML Ops and HindSight census job runs.**  
`ops/ml/local-runs.jsonl` records:
- `vm-mlops-daily-20261117-055414`: `ml-ops-smoke` result `pass`.
- `vm-mlops-daily-20261118-055414`: `unchanged`.
- `vm-mlops-daily-20261119-055414`: `unchanged`.

The private Muse memory record `t0/memory/2026-11-19.md` adds the 05:54 PST job detail: ML Ops smoke was `UNCHANGED` and skipped by the change gate (0/0 tests); HindSight ran a census only; `~/workspace/hindsight-local-test/RESULTS.md` retained its 2026-11-03 timestamp. This proves the daily job and census ran, while current ML Ops tests and HindSight retain/recall activity require separate receipts.

**VERIFIED — the Muse workspace backup exported successfully on November 19.**  
The latest private `muse-vm-workspace-backup/EXPORT.json` reports `export_id=exp-20261119T145835Z-881e42`, exported at `2026-11-19T15:00:49Z`, with T0=698, T1=92,637, manifest-only=37, excluded=71, split=3, vanished=0, and 124,474,904 bytes. Inventory, denylist, and content-scrub gates all pass. T1 remains manifest-only in this phase. The backup operator record uses the `vm-backup-state-watch` state-change poll and exporter; this workspace backup cycle is separate from the owner-reported HindSight cron export.

**OWNER-REPORTED — Temporal, HindSight, and ML Ops have executed on Muse.**  
The owner confirms prior Muse execution; one earlier test consumed GitHub compute quota. The current Muse Temporal service and daily ML Ops/census receipts provide additional runtime context. Current workload activity is tracked separately from service health and historical tests.

**VERIFIED — Muse Temporal self-host is live and currently idle.**  
Issue #2028's 2026-11-19T12:59:33Z living snapshot reports `temporal-selfhost` + `temporal-relay` active, gRPC at `localhost:7233`, Web UI at `localhost:8233` returning HTTP 200, relay `0.0.0.0:7234 → 127.0.0.1:7233`, a 983,040-byte SQLite DB, daily integrity-checked snapshots, and a 15-minute keepalive. The same record reports seven unit repairs after platform image replacements reset `/etc`. The workflow list is empty. Issue #5632 records zero executions and zero schedules that day, one namespace, and the continuity probe as the first live load. The service is healthy; the fleet-workflow lane remains to be wired and receipted.

**VERIFIED — Temporal N5 durable-execution acceptance is complete on the Actions engagement surface.**  
`docs/ops/TEMPORAL-DELPHI-CYCLE.md` and `ADDENDUM-2026-10-28-N5.json` record worker 1 SIGKILL, worker 2 resume, hash-gate rejection of incomplete/mismatched round-two evidence, four exactly-once ledger payloads, replay returning `already_posted`, and zero workflow/script parity diffs. GitHub runs 40758279842 (`delphi-cycle`) and 40759800247 (`engagement`) completed successfully, with artifacts 12845449786 and 12846223845. This proves the Actions engagement path and complements the active Muse self-host; each surface keeps its own workflow receipts.

**GAP — Temporal workload operationalization on Muse.**  
The 2026-10-28 migration record preserves the owner rule that the VM serves as a sandbox/evaluation surface. The 2026-11-19 living record shows the self-host active again for bounded staging/continuity work, with an empty workflow list. Issue #5632 is the registered path to score continuous-server versus per-batch arms, register QUE/VM producers, add workers, migrate schedules lane-by-lane, and capture the first fleet workflow receipt. Preserve the N5 Actions proof and use a separate Muse receipt for any Muse workflow.

**OWNER-REPORTED — HindSight runs on a Muse VM port with cron export.**  
The exact port, listener health, cron command, last successful export timestamp, output digest, and mapping to `HINDSIGHT_BASE_URL` require a current Muse-side receipt. Keep this HindSight job separate from the weekly `telemetry-ingest.yml` Actions workflow and from the workspace backup state-watch exporter.

**VERIFIED — HindSight's data path remains the highest-value P0 closure.**  
The 2026-11-19 Muse memory record reports 326 payloads blocked at exit #5553 and a written-but-unread attribution layer. Issue #5553 remains open for multi-arm extraction and replay of the 326 payloads; issue #5555 remains open for full message/thinking/Actions provenance ingestion and registered consumer reads. The prior hosted-sink census recorded 326 ingest + 62 density retain attempts returning HTTP 402; the later 2026-11-02 ingest receipt holds 336 payloads and 336 provenance records with `live_retain.attempted=0` because the retain stage was skipped. A Muse port and cron export establish service/export presence; a successful retain, stats, and recall canary establish a working memory path. The prior Fly/Koyeb census also found configuration divergence, a shared extraction-credit pool, Koyeb authentication awaiting configuration, and failover awaiting a verified drill.

**VERIFIED — Muse VM replacement and resource constraints shape compute placement.**  
The private VM memory record reports platform image replacement every 1h44–2h15; home state persists while `/etc` and running processes reset. The mesh probe measured 7.75 GB total RAM with 0.42–0.53 GB available across consecutive early-day readings, then 0.95 GB after the 02:49 PT replacement/recovery. The observer design uses a 60-second local state loop and a 15-minute guardian; its `setsid/nohup` relaunch repeatedly died on session teardown, with a tracked background-exec workaround used. Prefer checkpointed/chunked work under the replacement window and a one-shot, state-diff observer that records only material transitions.

**GAP — runtime receipt unification.**  
Use a common run envelope across Muse cron, Temporal workflow history, Actions runs, Hark requests, and HindSight exports. Each job should emit `job_id`, `run_id`, `started_at`, `ended_at`, `host_id`, `source_sha`, `workflow_id`, `status`, `input_digest`, `output_digest`, `export_uri`, and `health_probe`. Keep host secrets and raw private session content outside the public repo.

**STALE / CONFLICTED — Hark capacity and reachability.**  
The current `ops/compute/ALLOCATION.md` describes Hark as the same class as Muse (4 vCPU EPYC / ~8 GB RAM), while the previously inspected Hark node evidence describes a 2 vCPU ARM64 host with approximately 7.8 GiB RAM. The Muse memory record lists Hark at ~8.3 GB owner-stated and reports Hark absent from the tailnet peer list. The tailnet probe workflow was manually disabled during the 2026-11-19 window. A current node receipt and owner decision on the probe cadence will establish Hark placement and reachability.

**VERIFIED — current compute backlog has real queued work.**  
`ops/compute/BACKLOG.md` records the first provider stress-test wave fired across eight providers, clf-lab Tier 1 replicated on Muse at 12/12 cells, 3,443 unmapped endpoint DB rows measured, daily ML Ops/HindSight census, and probe-watch cadence. Other items occupy queued, stalled, and unbuilt states. This is an active portfolio with measurable execution evidence.

### 3.4 Reference templates and MergeEarn

**VERIFIED — the fleet-native Agentic Wallet template already has a complete spec proposal.**  
Original PR #4737, `feat/agentic-wallet-template`, introduced the wallet template files and family/index registration. Its branch diverges from current master and is 13,613 commits behind, so it remains lineage evidence.

The spec uses the existing hash-chained wallet ledger, provisioning set, and `scripts/moneyball/wallet_ledger.py` fold/verify/sweep tooling. It specifies `soft_quota_token` as observational and records explicit paper/test boundaries for chain, key custody, and real-money authority.

**OWNER-REPORTED — MergeEarn has already informed wallet-template use.**  
The owner reports prior MergeEarn use in wallet-template design. The upstream repository and PR #76 provide external product/contribution and bounty-flow context. The fleet template registers MergeEarn as a comparator while preserving the in-house wallet ledger as balance and settlement authority.

**IMPLEMENTED — fresh current-base registration is available in draft PR #5664.**  
PR #5664 carries the complete Agentic Wallet `README.md`, `SPEC.md`, and `SOURCE.txt`, plus index/family registration and the MergeEarn entry in `SOURCE-MAP.md`. The original PR #4737 remains open as lineage; #5664 is the current-base review path.

### 3.5 Compute and automation operating model

**VERIFIED — system-managed work already exists.**  
The generated automation catalog `docs/ops/generated/automation-workflow-catalog.md` lists 323 workflows. `docs/ops/ADAPTIVE-DISPATCH.md` defines event-driven wakes from PR lifecycle, selected lane completion, and canonical source-record pushes, plus a 30-minute cadence clock for 30-minute and hourly/modulo 3h/4h/6h/12h slots. The central dispatcher uses event and cadence triggers; the authenticated `/quota force all` issue command provides an auditable human override within the existing gates. QUE admission, Temporal workflows, Muse cron, Hark request/receipt stores, Actions orchestration, and scheduled telemetry ingest already form the operating substrate.

**GAP — cross-surface scheduler/receipt join.**  
The highest-value integration is one job/attempt identity and one status projection across QUE, Temporal, Muse/Hark cron, Actions, and output exports. Implement this as adapters into existing machinery.

**VERIFIED — retry and recovery controls already have a strong baseline.**  
Temporal N5 proves worker-loss recovery and exactly-once emission for the Delphi workflow. Extend the common receipt/attempt identity to other workloads, and reconcile unknown side effects before retry. Link every retry to its parent attempt and require a verifier or business receipt for terminal success.

### 3.6 Jules automation and API efficiency

The supplied Jules workflow guide describes issue delegation, PR review, setup actions, and reusable skill patterns. The repository already has a more governed implementation: `.github/workflows/agent-jules-on-issues.yml`, `.github/workflows/agent-pr-jules-handoff.yml`, reviewer automation, and `docs/ops/AGENT-JULES-HANDOFF.md`. The existing issue workflow pins GitHub Actions by immutable SHA, verifies trusted actors and source context, and uses the Jules API/GitHub App path. `tests/test_agent_jules_on_issues.py` explicitly protects the current design from legacy `google-labs-code/jules-action` and `jules-invoke` patterns. Preserve this integration instead of adding a parallel generic Jules action.

**VERIFIED — the PR handoff path exposed a high-frequency API cost.**  
PR #5664's `Agent PR Jules Handoff` mutation job received a GitHub App installation API rate-limit response while listing PR comments. The workflow was scanning comments on every PR synchronization event, including ordinary PRs with no Jules delegation.

**IMPLEMENTED IN DRAFT PR #5666 — pending-label API gate.**  
The new branch pins `actions/github-script` to its immutable v7.1.0 commit, adds a `jules-handoff-pending` label only after trusted-source and idempotency checks, gates mutation comment pagination on that label, records `MUTATION_OBSERVED`, and clears the label after the receipt. A focused Python test covers actor gating, action pins, label lifecycle, deduplication, and exact-SHA receipt fields. This reduces API reads across ordinary PR sync events while preserving the existing handoff state machine.

## 4. What exists beyond SWE

SWE-bench measures software issue-to-patch resolution. Build the broader agent portfolio around distinct capabilities: terminal execution, MCP tools, browser and desktop interaction, policy-constrained workflows, memory, mobile, ML engineering, security, and multi-agent coordination. The new `docs/evaluations/BENCHMARK-FAMILY-REGISTRY.md` records the families, native score semantics, adapter states, and admission sequence.

**MCP is the highest-fit extension for this repository.** TDQS already provides static MCP tool-definition quality and server-coherence signals. Add MCPMark for deterministic task outcomes, then DynamicMCPBench for trace-grounded effects on synthetic fleet-owned servers. MCP-Atlas, MCPAgentBench, and MCP-Bench extend coverage to cross-server discovery, distractor handling, and multi-step orchestration.

The highest-leverage additions are:

- **Terminal-Bench 4.1:** terminal-native work and systems tasks; immediate next terminal adapter. Its 4.1 release re-grades saved 4.0 trials with hardened verifiers and reward-hack resistance. Preserve 4.0 observations and 4.1 regrades as linked records.
- **MCPMark:** 127 curated MCP tasks with programmatic verification and controlled initial state; strongest first benchmark for CRUD, multi-turn, and stateful MCP workflows.
- **DynamicMCPBench:** trace-grounded, effect-scored framework for live MCP servers; ideal for synthetic versions of the fleet's own MCP servers, with pass^3 reliability and intermediate state-effect checks.
- **MCP-Atlas / MCPAgentBench / MCP-Bench:** cross-server tool discovery, distractor handling, multi-step orchestration, and intermediate-result grounding. These complement local TDQS and MCPMark.
- **BFCL v4 + ToolSandbox:** function-call accuracy, schema/argument correctness, multi-turn stateful tools, and intermediate/final state validation. BFCL's independent audit identified defects in 24 of 50 sampled tasks; attach task-level quality annotations and pair its aggregate with an independent local sanity set.
- **BrowserGym + WebArena / WebArena-Verified / WorkArena:** browser and web-app workflows with self-hosted task state; WebArena-Pro adds a recent multimodal research direction.
- **OSWorld / OSWorld-MCP:** desktop and cross-application computer-use tasks; allocate a dedicated disposable VM/GUI environment.
- **τ²-bench:** user-agent-tool interactions under policy and changing backend state, with text and voice variants.
- **LongMemEval / V2:** memory retrieval, temporal reasoning, knowledge updates, abstention, and query latency; directly relevant to HindSight and ForeSight.
- **AndroidWorld:** mobile workflows on an Android emulator; relevant to Termux and device-agent work.
- **MLE-bench:** 75 Kaggle ML engineering competitions. Official setup recommends 3 seeds and 24 hours on 36 vCPU, 440 GB RAM, and one 24 GB A10 GPU; the Lite/Low split has 22 competitions. Dataset terms are separate from the code license, and upstream leaderboard submissions remain paused per the official 2026-04-24 notice. Place full-suite runs on a dedicated 36-vCPU/440-GB/24-GB-A10 surface; use Muse for orchestration and preprocessing.
- **AgentDojo:** prompt-injection and defense evaluations in isolated synthetic environments.
- **GAIA / AgentBench / Terminal-Bench-Science:** broad assistant, multi-environment, and scientific workflow coverage.

Register each family as **CANDIDATE** or **RESEARCH**, then graduate it to **WIRED** and **EXECUTED** through pinned environments, adapter tests, and receipts. Preserve native metrics and version/regrade lineage.

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
| Durable execution | Temporal history + checkpoints + idempotent attempts | Long jobs survive worker loss and prevent duplicate side effects |
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
5. **Reuse verified artifacts.** Run verifier-only regrades when the benchmark allows it; record each regrade as a new observation linked to the original run. Terminal-Bench 4.1 is a current example.
6. **Keep native metrics.** Optimize a Pareto set across success, latency, tokens, cost, retries, interventions, and long-horizon reliability. Expose trade-offs through the separate metric dimensions.
7. **Promote replicated gains.** Require preregistration, multiple seeds/replicates, blinded evaluation where practical, independent verification, and green deterministic internal controls.
8. **Make schedules idempotent.** Stable job keys, leases, run IDs, output digests, and unchanged receipts reduce redundant work and make recurring systems self-maintaining.

### 5.4 Compounding scorecard

Measure compounding through the existing source ledgers and receipts. Keep this scorecard as a read-only projection; 3L0, MoneyBall, AEF, benchmark verifiers, the wallet ledger, and HindSight retain their existing authorities.

| Metric | Calculation | Current evidence | Next measurable gain |
|---|---|---|---|
| Evidence reuse ratio | Distinct verified consumers per canonical evidence unit | Session-history, workflow, DoE, benchmark, and provenance consumers already share source records | Link each consumed artifact to its downstream consumer IDs and count reuse |
| Provenance completeness | Runs with stable session/task/dispatch/actor/source-SHA/outcome joins ÷ total runs | 614 session-history records; 599 backfilled as observational; actor and outcome gaps remain | Join Termux Origin and DeepSeek session pointers; increase confirmed outcome coverage |
| HindSight population yield | Successful retains, indexed payloads, and recall hits per eligible payload | 326 payloads await extraction/replay; prior hosted retain attempts returned 402; current Muse daily job ran census only | Pass a 3-unit retain → stats → recall canary, then replay the 326 payloads with source IDs |
| Durable execution yield | Verified terminal outcomes ÷ workflow attempts, with retry and duplicate-effect rates | Actions N5 proof passed worker recovery and exactly-once emission; Muse self-host currently has zero workflow executions/schedules | Record the first Muse fleet workflow and scheduled run under #5632 |
| Compute efficiency | Verified outcomes per vCPU-hour and token/cost unit, stratified by surface | Muse export passed; Muse memory headroom and ~2-hour image replacement constrain long work | Route by live headroom; checkpoint each slice inside the replacement window |
| Queue health | Queue age, lease expiry, retry rate, stale-work reclaim, and receipt latency | QUE and pull-based VM request paths exist; Hark lease/reachability needs a fresh receipt | Publish one shared job/attempt projection from existing queue and worker receipts |
| Benchmark coverage | Candidate → wired → executed → resolved counts by family, with native metric | SWE lanes exist; TDQS is wired; MCPMark, DynamicMCPBench, and Terminal-Bench 4.1 are next candidates | Add adapters and receipts in family order; preserve score semantics and seed lineage |
| Template reuse | Active lane/agent instantiations per template version and downstream source consumers | Agentic Wallet + MergeEarn source registration is in draft PR #5664 | Record instantiation IDs and template version in provisioning receipts |
| Automation efficiency | API calls and compute minutes per verified state transition | Jules handoff scan was rate-limited on an ordinary PR sync; label-gated guard is in draft PR #5666 | Keep comment pagination restricted to pending handoffs; track API reads per dispatch |

The scorecard's primary optimization target is **verified downstream value per unit of compute and evidence-capture cost**. Reuse one validated artifact across every eligible consumer, while preserving each consumer's own acceptance test and authority.
 
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
- Preserve SWE-bench as its own coding-resolution track; keep native score scales separate.

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
| TDQS tool-definition lane | **IN-REPO** | `she/metrics/tdqs.py`, `tests/test_tdqs.py`, TDQS admission matrix and evidence schema; reuse for MCP static quality |
| Detailed compounding RECON report | **IMPLEMENTED on this branch** | This document; refresh after runtime probes |
| MergeEarn refTemplates lineage | **IMPLEMENTED on fresh current-base PR #5664** | Agentic Wallet README, SPEC, SOURCE, index, family README, and SOURCE-MAP; draft PR pending CI/review. Original PR #4737 remains open as lineage and diverges from current master. |
| DeepSeek / Termux Origin provenance | **MACHINERY VERIFIED; ORIGIN CAPTURE PARTIAL; JOIN GAP** | DeepCLI session store, Termux capture docs, Repo Replay RevWright pipeline, and canonical chat-provenance feed exist; recover source mappings and append missing canonical IDs |
| Muse workspace export | **EXECUTED / GATES PASS** | 2026-11-19 private export: T0=698, T1=92,637, 37 manifest-only, 71 excluded, 3 split; T1 content remains manifest-only |
| Muse Temporal service | **LIVE / IDLE** | #2028 reports active units, ports 7233/8233/7234, healthy CLI/UI, and empty workflow list; #5632 tracks first fleet workflow and schedule |
| Temporal N5 acceptance | **PASS ON ACTIONS** | Runs 40758279842 and 40759800247; worker kill/resume, hash gate, exactly-once ledger emission, and parity passed |
| HindSight Muse port + cron | **OWNER-REPORTED SERVICE; POPULATION GAP** | Daily job performed census only; local test results stale since Nov 3; 326 payloads blocked at #5553; #5553/#5555 remain open for extraction and provenance |
| Muse VM observer | **RELIABILITY GAP** | ~2h image replacement; /etc resets; 60s observer relaunch failed across exec-session teardown; move to one-shot state-diff probe |
| Hark capacity / reachability | **STALE / CONFLICTED** | Allocation and prior node probe disagree; Hark absent from current tailnet peer list; obtain current node receipt |
| Terminal-Bench 4.1 adapter | **CANDIDATE / P0** | Add adapter and isolated verifier harness |
| MCPMark + DynamicMCPBench | **CANDIDATE / P0** | Reuse TDQS; implement deterministic task and effect-based MCP adapters |
| Tool/browser/GUI/memory/mobile adapters | **CANDIDATE** | Sequence by P1/P2 roadmap |
| Unified runtime job identity | **GAP** | Extend QUE/Temporal receipts and preserve existing scheduler authorities |

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
- [HindSight continuity/SPOF census](CONTINUITY-SPOF-CENSUS-2026-11-01.md)
- [Telemetry ingest operator record](TELEMETRY-INGEST.md)
- [HindSight ingest receipt](../../ops/telemetry/ingest-receipt.json)
- [HindSight density retain receipt](../../ops/telemetry/hindsight-retain-density.json)
- [Temporal living status issue #2028](https://github.com/timerloggedout-spec/termux-monorepo/issues/2028)
- [Temporal operationalization issue #5632](https://github.com/timerloggedout-spec/termux-monorepo/issues/5632)
- [HindSight extraction exit issue #5553](https://github.com/timerloggedout-spec/termux-monorepo/issues/5553)
- [Full Provenance ingestion issue #5555](https://github.com/timerloggedout-spec/termux-monorepo/issues/5555)
- [Muse VM compute request issue #5603](https://github.com/timerloggedout-spec/termux-monorepo/issues/5603)
- [Muse VM backup export](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/EXPORT.json)
- [Muse daily runtime memory receipt](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/t0/memory/2026-11-19.md)
- [VM workspace backup operator record](../../ops/vm-backup/README.md)
- [Adaptive dispatch](ADAPTIVE-DISPATCH.md)
- [Generated workflow catalog](generated/automation-workflow-catalog.md)
- [TDQS architecture](../architecture/TOOL-DEFINITION-QUALITY-SCORE.md)
- [TDQS admission matrix](TDQS-ADMISSION-MATRIX.md)
- [ML Ops local receipts](../../ops/ml/local-runs.jsonl)
- [Temporal durable execution RECON](../rfps/temporal-durable-execution/RECON.md)
- [Temporal Delphi cycle operator record](TEMPORAL-DELPHI-CYCLE.md)
- [Temporal N5 acceptance addendum](../proposals/passes/temporal-durable-execution/implementation/ADDENDUM-2026-10-28-N5.json)
- [Temporal self-host migration / retirement record](TEMPORAL-SELF-HOST.md)
- [Jules handoff evidence contract](AGENT-JULES-HANDOFF.md)
- [Jules handoff API-load guard PR #5666](https://github.com/timerloggedout-spec/termux-monorepo/pull/5666)
- [Reference template consolidation](REFTEMPLATES-CONSOLIDATION.md)
- [Fresh current-base Agentic Wallet + MergeEarn registration PR #5664](https://github.com/timerloggedout-spec/termux-monorepo/pull/5664)
- [Original Agentic Wallet template PR #4737](https://github.com/timerloggedout-spec/termux-monorepo/pull/4737) — retained for lineage; diverged and 13,613 commits behind current master
- [DeepSeek capture pipeline](../DEEPSEEK-CAPTURE-PIPELINE.md)
- [Repo Replay consumer record](REPO-REPLAY.md)
- [Owner-original Repo Replay system](https://github.com/timerloggedout-spec/repo-replay)
- [RevWright provenance-gap rules](https://github.com/timerloggedout-spec/repo-replay/blob/main/revwright/pipeline.py)
- [Repo Replay origin pipeline correction](https://github.com/timerloggedout-spec/repo-replay/blob/main/PIPELINE-001.md)
- [Repo Replay source model](https://github.com/timerloggedout-spec/repo-replay/blob/main/README.md)
- [DeepSeek web-wrapper session commit / PR #174](https://github.com/timerloggedout-spec/termux-monorepo/commit/40683687b1bf50d70c74d6eb2426767f1f8836f8)
- [Canonical session provenance commit / PR #3453](https://github.com/timerloggedout-spec/termux-monorepo/commit/6050e1975ae5dabdb3b5751af7a8ad6ac016b5de)
- [DeepCLI session-store origin commit / PR #3625](https://github.com/timerloggedout-spec/termux-monorepo/commit/1e898b4606cbe1de01fa6f848e2ad6a3f10e4309)
- [MergeEarn upstream](https://github.com/Saidur-droid/MergeEarn)

External benchmark sources are collected in [BENCHMARK-FAMILY-REGISTRY.md](../evaluations/BENCHMARK-FAMILY-REGISTRY.md).

## 10. Decision summary

The best compounding path is to turn the repository's existing work into one evidence-linked lifecycle. The first concrete additions are the benchmark-family registry, the detailed operating report, and MergeEarn's explicit source registration in fresh current-base PR #5664. Original PR #4737 remains preserved as lineage, with its divergence called out for maintainer disposition. The next engineering slices are HindSight retain/read recovery, Temporal's first Muse fleet workflow, VM observer durability, DeepSeek/Termux provenance continuity, Terminal-Bench 4.1, MCPMark/DynamicMCPBench, and a common job/attempt envelope. Existing authorities remain intact; new adapters increase the number of useful consumers per verified execution.


## 11. RECON refresh protocol

- Re-fetch each canonical source at the start of a new cycle and record the source SHA, observation time, and scope.
- Append a dated delta when a runtime, receipt, branch, workflow, or benchmark status changes; preserve prior evidence snapshots.
- Join records through stable IDs and hashes; keep source-specific lineage and uncertainty beside every projection.
- Re-run the smallest relevant verifier after each implementation slice, then inspect the full PR check set and artifact receipts.
- Reconcile stale or conflicting surfaces through a fresh host/run receipt before changing allocation, routing, or promotion state.
- Close each cycle with a decision record: promote, retain, cull, defer, or request the missing evidence.
