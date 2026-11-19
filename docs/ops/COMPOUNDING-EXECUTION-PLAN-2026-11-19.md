# Compounding Systems — execution plan

**Date:** 2026-11-19  
**Companion:** [RECON report](COMPOUNDING-RECON-REPORT-2026-11-19.md)  
**Benchmark catalogue:** [Benchmark Family Registry](../evaluations/BENCHMARK-FAMILY-REGISTRY.md)

This plan composes the existing QUE, Temporal, compute mesh, DoE, provenance, AEF, 3L0, MoneyBall, ForeSight/HindSight, and reference-template systems into a bounded implementation queue.

## 1. Execution policy

- System schedules own recurring discovery and execution.
- QUE owns admission, leases, and work identity.
- Temporal owns durable workflow state, retries, and checkpoints where the deployed integration is verified.
- Muse/Hark/Actions/pool own placement according to the current allocation card and live capacity receipt.
- Every dispatched unit emits one immutable run receipt and one DoE experiment record.
- Each retry or regrade links to its parent; uncertain side effects enter reconciliation before replay.
- Benchmark-native metrics and scoring authorities remain separate.
- Schedules and QUE own recurring operation; manual dispatch remains an authorized entry path.
- Keep PRs reviewable as drafts until checks, provenance, and required approvals are complete.
- Reuse `.agents/skills/adaptive-wait/SKILL.md`, `.agents/skills/adaptive-feedback-cycle/SKILL.md`, and `.agents/skills/evidence-led-monorepo-ops/SKILL.md` as the operating controller; keep this programme inside the established loop.

## 2. Bounded compounding loop

Each cycle uses the six-step loop already compatible with the repository's adaptive-wait and adaptive-feedback skills:

1. **Observe** — re-fetch immutable branch/SHA, queue, workflow, job, artifact, and runtime state.
2. **Choose** — select the highest-value in-scope action using evidence, risk, resource fit, and dependency readiness.
3. **Act** — make one bounded, reversible change or run one admitted task cohort.
4. **Verify** — run the same acceptance check under recorded conditions; inspect terminal job/step/artifact evidence.
5. **Record** — append run/effect/provenance receipt and update the owning registry.
6. **Repeat or stop** — continue while measurable progress exists; stop at `success`, `clean-no-op`, `blocked`, `approval-required`, `exhausted`, or `stagnated`.

WAIT is an evidence-collection phase. Re-fetch after material changes, back off on unchanged live state, and continue disjoint work while checks run. Retry only when an evidence-backed change exists. The user-supplied Loopy API skill provides a bounded-loop design reference; this programme reuses repo-native controllers, while separate Loopy catalog or `LOOPS.md` registration remains an explicit future step.

## 3. Workstream plan

| ID | Priority | Workstream | Implementation | Acceptance evidence | State |
|---|---|---|---|---|---|
| CEX-001 | P0 | DeepSeek / Termux Origin provenance continuity | Reuse DeepSeek webWrapper/session-store history and the owner-original Repo Replay / RevWright Session Provenance extraction model. Recover available exports, session/message/block pointers, hashes, and surviving Git history; classify missing origin state with the documented gap taxonomy; join to `chat-provenance/v1` idempotently | Source-to-canonical join receipt; duplicate-free feed delta; 1:N reverse index; actor-confidence report; gap classes `never_in_chat/lost_at_origin_capture/unharvested_provider/drifted_final_edit/UNRESOLVED`; outcome remains observational until confirmed | **PROVENANCE MACHINERY EXISTS; ORIGIN CAPTURE PARTIAL; JOIN REQUIRED** |
| CEX-002 | P0 | Muse HindSight runtime + population receipt | Map the owner-reported Muse VM port to the actual `HINDSIGHT_BASE_URL`/export target; extend the existing cron receipt with host/process/listener health, port identity, input/output digests, and a bounded 3-unit retain + recall canary. Reconcile the daily census-only run, stale local RESULTS.md, 326 blocked payloads, and issues #5553/#5555. Keep this distinct from the weekly Actions ingest workflow and workspace backup state-watch exporter | Current Muse host/cron receipt; 3/3 proof retains; stats + recall canary; output digest; redacted receipt fields; replay receipt for the 326 payloads | **OWNER-REPORTED SERVICE; POPULATION/READ PATH UNVERIFIED** |
| CEX-003 | P0 | Hark/Muse capacity reconciliation | Probe each host; reconcile CPU architecture, vCPU, RAM, seat lease, disk, and current process pressure against `ops/compute/ALLOCATION.md`; include Muse's sub-1-GB available-memory readings and Hark's current tailnet visibility | Timestamped node receipts; allocation card updated from live measurements; placement thresholds match the measured host | **CONFLICTED CARD / MUSE MEMORY PRESSURE / HARK REACHABILITY GAP** |
| CEX-004 | P0 | Common job/attempt identity | Define a crosswalk from QUE item/lease, Temporal workflow/run/activity, cron run, Actions run/job, and Hark request/DONE receipt | One synthetic lifecycle test with admission → placement → retry → resume → terminal receipt | **DESIGN READY** |
| CEX-005 | P0 | Temporal Muse workflow activation | Preserve the N5 kill/resume PASS on Actions; use the live Muse self-host from #2028 as a bounded staging surface; execute the first registered fleet workflow and schedule under #5632; capture producer, worker, task queue, workflow ID, run ID, and host receipt | Existing Actions runs 40758279842 + 40759800247 and artifacts 12845449786 + 12846223845 remain linked; Muse shows one scheduled execution with a terminal receipt and a current workflow list | **MUSE SELF-HOST LIVE / IDLE; FIRST FLEET WORKFLOW PENDING** |
| CEX-006 | P0 | Terminal-Bench 4.1 adapter | Pin Harbor, benchmark/task revision, RewardKit/verifier revision, resource profile, agent harness; execute a small CPU slice in isolated workers | Task-level receipt, verifier integrity tests, artifact regrade lineage, repeated-trial statistics | **CANDIDATE** |
| CEX-007 | P0 | MCP task adapter | Reuse TDQS as the static tool-definition preflight; implement MCPMark with curated initial state and programmatic verifier; then DynamicMCPBench on synthetic fleet-owned MCP servers with effect checkpoints | TDQS evidence hash + task-level receipt + pass@1/pass^4 or pass^3 semantics + state-effect verification + sandbox reset | **CANDIDATE; TDQS IN-REPO** |
| CEX-016 | P1 | MCP discovery / cross-server cohort | Add MCP-Atlas, MCPAgentBench, and MCP-Bench after CEX-007; test tool discovery, distractors, multi-server coordination, and intermediate-result grounding | Tool-selection diagnostics, per-server identity, cross-tool trajectory, claims/effect receipt, version pins | **CANDIDATE** |
| CEX-008 | P1 | Browser adapter | Use BrowserGym as the shared harness for WebArena / WebArena-Verified; retain WebArena-Pro as research; synthetic users and seeded data | Reproducible environment reset, DOM/screenshot trace, state-based verifier, synthetic accounts only | **CANDIDATE** |
| CEX-009 | P1 | Benchmark envelope | Add the canonical benchmark/run fields to the existing experiment/receipt contract; preserve native score schema | Schema validation, migration notes, backward-compatible fixture, one end-to-end run | **DESIGN READY** |
| CEX-010 | P2 | Memory evaluation | Add LongMemEval / V2 against HindSight/ForeSight retrieval and memory projections | Accuracy, temporal reasoning, update, abstention, latency, privacy/retention checks | **CANDIDATE** |
| CEX-011 | P2 | GUI/mobile evaluation | Add OSWorld and AndroidWorld using dedicated disposable VM/emulator surfaces | State reset, device/environment fingerprint, app-level task receipts, resource cap | **RESOURCE GATED** |
| CEX-012 | P2 | Policy / adversarial evaluation | Add τ²-bench and AgentDojo in synthetic isolated environments | Policy compliance, tool-state correctness, prompt-injection defense, side-effect containment | **CANDIDATE** |
| CEX-013 | P2 | ML engineering evaluation | Add MLE-bench lite/internal subset when GPU/RAM/time are admitted | Resource receipt, Any-Medal metric, split breakdown, internal-vs-official status label | **RESOURCE GATED** |
| CEX-014 | P2 | MergeEarn template lineage | Review the source-map and wallet-template registration on fresh current-base PR #5664 | Approved refTemplates registration; fleet ledger remains the internal record of record | **IMPLEMENTED ON CURRENT-BASE DRAFT PR** |
| CEX-015 | P3 | Verified treatment promotion | Promote replicated DoE winners into runtime routing/templates/skills | Preregistered arm, independent scorer, replicated outcomes, regression pass, governance sign-off | **CONTINUOUS** |
| CEX-018 | P0 | Muse VM observer durability | Replace the session-bound 60-second observer loop with an idempotent one-shot state-diff probe under the existing 15-minute guardian. Persist the prior fingerprint under durable home storage; capture boot ID, machine ID, `/etc` fingerprint, process/port state, and memory headroom; emit only material transitions | Two image-replacement cycles produce one receipt each; state survives `/etc` reset; guardian runs complete; duplicate transition alerts collapse by boot ID | **RELAUNCH FRAGILITY OBSERVED; FIX DESIGN READY** |
| CEX-019 | P2 | Jules handoff API load guard | Gate PR mutation comment pagination on a `jules-handoff-pending` label, attach it after trusted dispatch/idempotency checks, clear it after mutation receipt, and pin github-script by SHA | Ordinary PR sync events skip comment pagination; trusted handoff adds label; mutation emits one exact-SHA receipt and clears label; duplicate receipt cleanup is idempotent | **IMPLEMENTED ON DRAFT PR #5666; CI PENDING** |
| CEX-020 | P2 | Compounding scorecard | Build a read-only projection from existing source ledgers and receipts: evidence reuse, provenance completeness, HindSight population yield, durable execution yield, compute efficiency, queue health, benchmark coverage, template reuse, and automation API cost | Every metric binds to canonical source IDs and native authority; scorecard exposes gaps and trends without creating a new scoring plane | **SPECIFIED; IMPLEMENTATION READY AFTER P0 RECEIPTS** |

## 4. First execution batch

Run the following as one bounded P0 batch:

1. Recover DeepSeek and Termux Origin history using the existing RevWright/session provenance method; preserve the canonical feed during reconciliation.
2. Generate a join report keyed by session ID, message/turn ID, workflow run ID, source commit, timestamp, route, and actor evidence.
3. Probe Muse and Hark, capturing host IDs, resource cards, memory headroom, and tailnet visibility.
4. Capture the Muse HindSight port/listener/cron/export receipt, then run the 3-unit retain → stats → recall canary and reconcile the 326-payload replay.
5. Activate one registered Muse Temporal fleet workflow under #5632; retain the completed Actions N5 proof and capture the Muse workflow/host receipt.
6. Re-fetch all generated receipts and compare against the previous known state.

The batch produces a decision packet for CEX-001 through CEX-005 and CEX-018 while preserving routing weights and historical records.

## 5. Benchmark execution batch

The first benchmark wave should be deliberately narrow:

- **Wave A:** Terminal-Bench 4.1 CPU tasks, one pinned agent treatment, multiple seeds, isolated verifier.
- **Wave B:** MCPMark deterministic tasks, then DynamicMCPBench on synthetic fleet-owned MCP servers; reuse TDQS as static schema preflight.
- **Wave C:** BFCL v4 and ToolSandbox, tool-call and stateful interaction tracks with task-quality annotations.
- **Wave D:** BrowserGym/WebArena, seeded synthetic web applications and reset receipts.

For each wave, run a small calibration cohort, inspect every failure and verifier artifact, then expand task coverage. Keep benchmark family scores separate. Compare treatments within each family and use the DoE design to test interactions across provider, model, prompt, toolset, manager, and compute surface.

## 6. Shared run envelope

Map the shared run envelope onto the existing canonical sources:

```text
experiment_id + arm_id + instance_key + seed
    ↓
QUE item_id + lease_id + dispatch_id
    ↓
Temporal workflow_id + run_id + activity_id
    OR cron run_id / Actions run_id / Hark request_id
    ↓
attempt_id + parent_attempt_id + checkpoint_id
    ↓
benchmark_id + version + task_id + task_fingerprint
    ↓
provider + model + endpoint + prompt_hash + tool_hash
    ↓
host_id + surface_id + environment_digest + resource_profile
    ↓
native_outcome + verifier_version + artifact_refs + cost/latency/tokens
    ↓
3L0 / MoneyBall / ForeSight / HindSight / failure corpus projections
```

Every projection carries the canonical run/dispatch reference. Each consumer applies its own schema and authority. The raw artifact is stored once under the owning evidence system.

## 7. Automation and cadence

| Cycle | System owner | Cadence / trigger | Output |
|---|---|---|---|
| Queue discovery and admission | QUE / QDesk + Adaptive Dispatch | PR/lane-completion/canonical-record event wakes plus the existing 30-minute cadence clock | Eligible work, lease, queue state; central dispatcher remains event-driven with an authenticated issue override |
| Durable execution | Temporal: Actions engagement for DelphiCycle; Muse self-host live/idle pending first fleet workflow | Workflow policy | History, checkpoint, activity receipt with surface/host identity |
| Daily HindSight + ML Ops | Muse VM cron | Existing daily schedule; latest job ran ML Ops smoke as unchanged and HindSight census only | Health receipt, export digest, run result, retain/recall canary |
| Bounded isolated export/hygiene | Hark VM | Existing registry/request cadence | REQUESTS → DONE receipt |
| CI validation and bounded orchestration | GitHub Actions | Push / PR / scheduled events; 323 workflows catalogued in generated automation index | Run/job/step/artifact receipt |
| Provenance ingest | Telemetry ingest workflow + VM-side emitters | Existing schedule and source availability | Append-only canonical feed and mapping receipt |
| Tool-definition quality | TDQS local lane | Tool-schema capture / registry update | Deterministic input hash, context signals, evaluator evidence, server-coherence receipt |
| Evaluation | AEF/DoE adapters | Queue admission and registered cohort cadence | Native benchmark result + experiment record |
| Promotion review | Governance/3L0/MoneyBall | After evidence thresholds | Promote, retain, cull, or request more evidence |

Cadence changes require current schedule and host receipts. Preserve the existing daily AI schedule and cron.

## 8. Required test and safety matrix

| Scenario | Expected behavior |
|---|---|
| Duplicate schedule tick | Stable job key deduplicates or returns existing run receipt |
| Worker dies before activity start | Lease expires safely; task re-enters eligible queue |
| Worker dies during unknown side effect | State becomes reconciliation-required; replay waits for side-effect check |
| Worker resumes from checkpoint | Exactly one terminal receipt; parent/child attempt lineage retained |
| Provider rate limit | Backoff and requeue under the current lease policy; attach consumer identity at requisition time and preserve unknown attribution states |
| Host capacity pressure | Admission defers or reallocates to a compatible surface; chunk work under the observed ~2-hour VM replacement window |
| Export has same digest | Record `unchanged`; retain last-known good export reference |
| VM image replacement | One-shot observer records boot ID and state fingerprint from durable home; work resumes from a checkpoint |\n| Export digest changes | Record new artifact and source SHA; verify scrub and restore |
| Verifier regrade | Create a new observation linked to the old run; preserve historical score |
| Missing actor/outcome | Retain null/observational state; keep 3L0 weight at zero until corroborated |
| Secret-shaped payload | Scrub before hashing/writing; record redaction count |
| Benchmark verifier executes untrusted code | Run in isolated process/container; trusted verifier retains reward authority |
| Benchmark task version changes | New task/version identity; retain prior result and compare only under valid protocol |

## 9. Completion and promotion

A workstream is complete only when:
- its acceptance evidence is linked to a commit or immutable artifact;
- the smallest relevant deterministic test passes;
- `git diff --check` and repository hygiene gates pass;
- CI reaches terminal states and all required jobs are inspected;
- the final branch SHA is re-fetched and compared;
- the report and registry state are updated from those receipts.

A PR reaches promotion after terminal checks, evidence review, and the repository's established governance decision.


## 10. Current review branches

- [#5663 — compounding RECON, benchmark registry, and execution plan](https://github.com/timerloggedout-spec/termux-monorepo/pull/5663): draft; CI and review pending.
- [#5664 — current-base Agentic Wallet + MergeEarn refTemplates registration](https://github.com/timerloggedout-spec/termux-monorepo/pull/5664): draft; CI and review pending.
- [#5666 — Jules handoff API-load guard](https://github.com/timerloggedout-spec/termux-monorepo/pull/5666): draft; CI and review pending.
- CEX-020 compounding scorecard reuses the existing canonical receipts after the P0 runtime joins land.
- [#4737 — original Agentic Wallet template lineage](https://github.com/timerloggedout-spec/termux-monorepo/pull/4737): preserved; branch diverges from current `master` and is 13,613 commits behind. Review #5664 as the fresh current-base registration path; maintainer disposition of #4737 remains open.
