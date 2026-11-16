# RECON — Temporal ecosystem × Bifrost / Gravitee / getDX / Witness

**Lane:** [MUSEai]@{role:{temporal-recon}}
**Date:** 2026-10-27 (America/Los_Angeles)
**Method:** live GitHub API at recon time — code-search counts/paths in
`timerloggedout-spec/termux-monorepo`, repo metadata + README heads for all
`temporalio/*` targets. Counts below are derived from those live responses,
not copied from any earlier snapshot.
**Companion:** `RFP.md` in this folder (generation-first Oracle Method RFP).

## 1. Link validation — the 19 supplied links

All 19 resolve. They decompose as: 1 Temporal Cloud free-tier page
(owner-gated, see §6), 1 org page (`temporalio`, 17 repos below), 17 repos.

**Every one of the 17 repos exists, is unarchived, and was pushed to within
the 7 days before recon — 15 of 17 on 2026-10-27 itself.** This is a live,
fast-moving upstream, not a reference fossil.

| # | Repo | ★ | Lang | Pushed (UTC) | One-line purpose |
|---|------|---|------|--------------|------------------|
| 1 | temporalio/temporal | 24,022 | Go | 2026-10-27 | Durable-execution server: workflows, event history, replay |
| 2 | temporalio/ui | 446 | TS | 2026-10-27 | Web UI over workflow history |
| 3 | temporalio/awesome-temporal | 479 | — | 2026-10-16 | Curated ecosystem index |
| 4 | temporalio/cli | 389 | Go | 2026-10-27 | CLI + `server start-dev` |
| 5 | temporalio/temporal-worker-controller | 197 | Go | 2026-10-27 | K8s worker lifecycle, Worker Versioning (GA) |
| 6 | temporalio/api | 136 | Go/proto | 2026-10-27 | gRPC API + proto contracts |
| 7 | temporalio/ai-cookbook | 107 | Python | 2026-10-26 | Runnable AI patterns: agents, HITL, deep research, durable MCP |
| 8 | temporalio/omes | 104 | Go | 2026-10-27 | Load generator / benchmark scenarios |
| 9 | temporalio/ai-integrations | 34 | Python | 2026-10-27 | Framework plugins: LangGraph, LangSmith, DeepAgents, Google ADK/GenAI, Spring AI |
| 10 | temporalio/pi-temporal | 15 | TS | 2026-10-27 | Pi coding agent on Temporal: kill worker mid-turn, another finishes |
| 11 | temporalio/temporal-auto-scaled-workers | 13 | Go | 2026-10-27 | Worker Controller Instance: backlog-driven autoscaling (Lambda/ECS/AgentCore) |
| 12 | temporalio/skill-temporal-serverless | 6 | skill | 2026-10-27 | Agent skill for serverless workers (Lambda / Cloud Run pools), Public Preview |
| 13 | temporalio/nexgen | 4 | Rust | 2026-10-27 | NexusRPC schema → typed models + shared validators, Go/Java/Python/TS |
| 14 | temporalio/kube-temporal | 1 | Go | 2026-10-27 | Shared CRDs / controller Go code |
| 15 | temporalio/cloud-operator | 1 | Go | 2026-10-27 | K8s operator for Temporal Cloud resources |
| 16 | temporalio/public-actions | 1 | Shell | 2026-10-27 | Shared public-repo Actions |
| 17 | temporalio/cruise-control-api | 0 | proto | 2026-10-27 | Cruise Control gRPC API / protos only |

## 2. Status in this repo — what already exists (implementation state)

Code-search totals on master at recon time (term → hits). Note the trap:
`temporal` = 284 hits is mostly the *word* (time/lineage). The real
Temporal.io footprint is the 4 anchors marked †.

| Surface | Hits | State | Evidence home |
|---------|------|-------|---------------|
| Temporal.io † | — | **P1 observational, smoke only.** Self-host compose + one hello workflow; LangSmith plugin adapter documented. No production workflow, no worker fleet, no CI gate dependency (by design). | `docs/proposals/active/temporal-langsmith-adapter/` (status: executing, P1), `docs/ops/TEMPORAL-LANGSMITH-ADAPTER.md`, `mcp-docker/temporal/`, `scripts/temporal/hello_workflow.py` |
| Bifrost | 26 | **Proposal landed, integration slice partial.** RECON + registry row + MCP catalog `evaluation` + provider-capabilities done (PR #611 lineage); benchmark smoke is backlog BIFROST-006; `.github/workflows/bifrost-006-smoke.yml` exists. Forks kept external, thin integration only. | `docs/proposals/active/bifrost-gateway-integration/{RECON,MANIFEST,ITEMS}.md`, `mcp-hub/catalog.json` |
| Gravitee | 13 | **Research seed only — pattern source, zero code.** Fork kept, no submodule, no vendoring; loop is RECON→WATCH→COMPARE→EXTRACT→PROPOSE. Sole occupant of `research-seeds/` besides its README. | `docs/repositories/GRAVITEE-RESEARCH-SEED.md`, `docs/repositories/research-seeds/gravitee-api-management.json` |
| getDX (DX) | **0** | **ABSENT.** `getdx`, `get-dx`, `"getdx"`, `developer experience dx` all return 0 code-search hits. No seed, no registry row, no proposal. This is the one true gap in the set — see RFP §7. | — (honest blank) |
| Witness | 7 | **Registry INVESTIGATE; composition rule landed** (PR #1674): Witness = only runnable attestation engine in the supply-chain-provenance family; evidence envelope stays canonical; attestation digests referenced *from* evidence records; keys names-only. | `config/agent_stack_integrations.json`, `docs/ops/FOSS-FORESIGHT-PROCUREMENT-REGISTRY.json` |
| Gantt seeds | 43 | Seed-selection decisions recorded: Camshaft = advisory adapter candidate (blocked on GanttML provenance), ICM/routing = governing policy seeds, rest pattern-only. Global no-go: no seed decides readiness/dispatch/merge. | `docs/agentic/decisions/SEED_SELECTION.md`, `docs/agentic/TEMPLATE_CAPABILITY_ASSESSMENT.md`, `docs/proposals/active/gantt-dependency-phases/` |
| MoneyBall | 175 | Real code + scorer/explain/quota-weights; feed + page live. | `ml/pipelines/moneyball/{scorer,explain,weights,quota_weights}.py`, `docs/ops/HEX-MONEYBALL-INTEGRATION.md` |
| DoE/MVT | — | Harness defined, loop defined-not-run at fleet scale; canonical row = cohort × task × arm × repetition, with task/env fingerprints + arm-factor hash retained per row. | `docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md`, `docs/ops/MVT-DOE-ATES-SEPARATION.md` |
| Oracle/Delphi | — | Generation-first method is owner law: generate n → cross-vote (source classes separate) → implementation round → round-2 on equalized evidence → calibration deltas to ledgers. | `docs/ops/DELPHI-LANE-CONTRACT.md` and successors |

**Seed/starter system the drafting reuses (`{seed}{starter}` templates):**
(1) research-seed record — `docs/repositories/research-seeds/*.json`
(Gravitee precedent, currently n=1); (2) proposal pack —
`MANIFEST.md` + `ITEMS.md` + `RECON.md` (Bifrost / Temporal-LangSmith
precedents); (3) RFP folder — `docs/rfps/<slug>/RFP.md`
(mesh-resiliency precedent, issue-tracked); (4) Repository Observatory —
starred/forked/watched repos are research *signals*, never adoption orders.

## 3. Best pieces — what to extract from each (no vendoring, anywhere)

- **temporal (server)** — the model, not the binary: deterministic workflow
  code + activities for side effects; event history as the replayable truth;
  signals (external input to a running workflow), queries (read state
  without mutating), updates; retries/heartbeats/timeouts as policy, not
  hand-rolled loops.
- **cli** — `server start-dev` single-command substrate; environment
  config as a first-class surface. Already our documented on-ramp.
- **api** — proto-first contracts, versioned independently of any SDK.
  The discipline our lane contracts / evidence schemas should mirror.
- **ai-cookbook** — the pattern catalogue closest to our work: agentic
  loops, human-in-the-loop approval as a workflow pause, multi-agent deep
  research (plan → search → synthesize), durable MCP servers, claim-check
  for large payloads, structured output, retry patterns. Each recipe is a
  self-contained runnable project = a starter template by construction.
- **ai-integrations** — plugin-per-framework packaging: each plugin its own
  package, deps, tests, version, release cadence. Includes the LangSmith
  plugin our existing adapter already rides on, plus LangGraph/DeepAgents —
  i.e. the bridge from our current P1 adapter to durable agent frameworks
  is upstream-maintained, not ours to build.
- **pi-temporal** — **highest novel relevance to this fleet.** A coding
  agent whose worker can die mid-turn while another machine finishes the
  turn; session file as shared state; started-but-unrecorded tool calls are
  reported to the model as *unknown outcome*, never blindly retried;
  `/background` tasks outlive the terminal; per-turn token/wall-clock
  budgets. Its `src/core/` is agent-agnostic (Pi is one implementation) and
  `examples/echo/` is a no-key, no-Docker starter. This is the
  VM-replacement / lane-death problem this fleet actually has, solved in
  the open.
- **skill-temporal-serverless** — an *agent skill* as the deployment
  runbook: scoping → access checks → packaging → registration →
  verification → rollback, for Lambda workers and Cloud Run worker pools.
  Directly mappable to our `.agents/skills/` form: the starter is the
  skill, not a repo fork.
- **temporal-worker-controller** — Worker Versioning as the safe answer to
  "changing worker code breaks running workflows": deployment versions,
  ramped rollouts, pinned builds. The actuation layer a routing decision
  needs before it may touch live work.
- **temporal-auto-scaled-workers** — autoscaling *as a workflow*: a Worker
  Controller Instance polls backlog/dispatch metrics, applies a
  configurable algorithm, invokes compute (Lambda one-off, ECS worker
  sets). Scaling groups keyed by task-queue type/region.
- **omes** — scenario-based load generation against the substrate itself:
  the missing load-evidence instrument for DoE arms (cf. Bifrost's
  benchmarking companion — same pattern, different plane).
- **nexgen** — one NexusRPC/JSON-Schema contract → typed models + a single
  shared validator enforced on both sides of the wire, violations
  aggregated into one error. Our cross-lane/cross-language contracts
  (evidence envelope, lane envelopes) want exactly this shape.
- **ui** — history-first observability: the timeline *is* the audit log.
  A rendering lesson for the evidence-projection / SHE surfaces, not a
  component to adopt.
- **kube-temporal / cloud-operator** — CRD/operator patterns only. No K8s
  fleet exists here; both are watch-tier until one does.
- **cruise-control-api / public-actions** — proto-only and CI-glue
  respectively; watch-tier, extract nothing now.
- **awesome-temporal** — the index pattern itself: a curated, classified
  list as a living research seed (our Observatory does this with
  provenance added).

## 4. The four-plane composition (why these names belong in one recon)

None of Bifrost / Gravitee / Temporal / getDX replaces another; each owns
one plane, and Witness attests across all four:

| Plane | Owner candidate | Owns | In-repo state |
|-------|-----------------|------|---------------|
| Request | Bifrost | LLM gateway: unified API, failover, budgets, MCP gateway | proposal + partial slice |
| Publication | Gravitee | API lifecycle, portal, policy, analytics | research seed only |
| Time | Temporal | durable execution: retries, history, human gates, scheduling | P1 smoke only |
| Measurement | getDX | developer-experience measurement (flow, friction, delivery) | **absent — gap** |
| Attestation | Witness | signed in-toto provenance of how artifacts were produced | INVESTIGATE, composition rule landed |

## 5. Priority verdict (MoneyBall-shaped, evidence at recon time)

Scored on: fleet-pain relevance × evidence maturity ÷ adoption cost
(remote-first law and no-vendoring rule applied as hard filters).

- **P0 — extract/prove now:** pi-temporal kill-and-resume pattern;
  ai-cookbook agent/HITL/deep-research recipes; ai-integrations plugin
  packaging (LangSmith bridge already in repo).
- **P1 — model, then actuate:** worker versioning + WCI autoscaling as
  the actuation layer for MoneyBall/quota routing; omes scenarios as DoE
  load evidence; nexgen contract-generation for lane envelopes;
  skill-temporal-serverless as a `{starter}` skill template.
- **P2 — watch:** kube-temporal, cloud-operator, cruise-control-api,
  public-actions, ui (pattern only).
- **Rejected shapes:** Temporal server on-device (B160V heavy-runtime law
  — remote/Codespace first); vendoring or submoduling any of the 17;
  Temporal Cloud signup in this lane (§6).

## 6. Owner gates (unchanged, restated)

- Link 1 (Temporal Cloud free tier) = **account creation: owner-gated.**
  Existing repo posture already says self-host first, Cloud only after
  operator confirms. This recon changes nothing there.
- Signing keys for any Witness-attested workflow history: names only,
  never values in repo/telemetry/artifacts (PR #1674 hard gate).

## 7. What this recon hands the RFP

1. The fleet's real durability gap is lane death (VM replacement, worker
   kill, session loss) — pi-temporal is the only supplied artifact that
   addresses it head-on.
2. Our Temporal footprint is a smoke, not a substrate: one hello
   workflow, zero production workflows, zero kill-resume evidence.
3. getDX has no in-repo existence at all; any DX measurement claim would
   currently be invented. It enters as a research seed or not at all.
4. The drafting machinery already exists — research-seed JSON, proposal
   MANIFEST/ITEMS, RFP folder, Observatory — so the build is *content
   through those templates*, not new scaffolding.
