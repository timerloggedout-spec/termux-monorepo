# Agent Worktree Orchestration Contract

**Status:** proposed canonical treatment contract; adapter-neutral
**Owner:** Agent Team Control Plane
**Research input:** Kilo Code Agent Manager documentation, retrieved 2026-11-16
**Related implementation:** #5507 (agent-browser toolchain), #5492 (Rust Brain kernel)

## Purpose

Make filesystem isolation, session ownership, and integration discipline explicit dimensions of agent orchestration. Reuse the existing Agent Team Control Plane, orchestration treatment schema, receipt schema, evidence envelope, QUE/QDesk, and review/promotion lifecycle.

This is not a proposal to adopt Kilo Code as a runtime dependency. Kilo is a useful reference implementation for independent agent sessions, Git worktrees, multi-version experiments, imported PR work, and human diff review. The same contract must work with Codex, Jules, Gemini, CLI agents, MCP agents, GitHub Actions, and future executors.

## Findings transferred from the reference

The Kilo Agent Manager documentation distinguishes:
- A delegated subagent operating in its parent's project/worktree; it does not create a worktree.
- An independent top-level session that can receive its own Git worktree.
- Multiple conversations sharing one worktree (shared filesystem and branch; therefore coordinated writes).
- Independent worktrees for separate branches and parallel implementations.
- Importing an existing branch, external worktree, or GitHub PR.
- Reviewing diffs and running tests before integration.
- Comparing alternative implementations using separate worktrees and optionally different models.
- Kilo Swarm as a communication board for a main session and its task descendants, not a scheduler or dispatcher; independent Agent Manager sessions do not automatically share that board.

These are capability observations, not evidence that the same runtime is installed or supported on Termux. Product-specific concurrency limits must not become repository-wide constants.

## Canonical architecture

```text
BIUDL / Agent Team Control Plane
       |
       +-- Scout / Recon
       +-- Manager / Planner
       +-- Builder / Specialist agents
       +-- Reviewer / Validator
       |
       v
Orchestration treatment (existing registry/schema)
       |
       +-- session topology
       +-- workspace isolation policy
       +-- writer ownership policy
       +-- provider/model assignment
       |
       v
Existing execution adapters
       |
       +-- shared-workspace subagent
       +-- Git worktree session
       +-- container / remote workspace
       +-- GitHub Actions / CLI / MCP / IDE agent
       |
       v
Existing evidence and review systems
       |
       +-- canonical orchestration receipt
       +-- SHA / run / job / step / artifact evidence
       +-- diff review / tests / outcome
       +-- existing promotion and dual gates
```

The Brain proposes and structures work; the existing harness/policy boundary authorizes it; existing hands execute it. A workspace is an execution resource, not a new queue, scheduler, identity authority, memory store, or evidence ledger.

## Workspace modes

| Mode | Filesystem/Git isolation | Default write policy | Intended use |
|---|---|---|---|
| `shared_read_only` | Shared | Read-only | Recon, code tours, log analysis, independent review |
| `shared_coordinated` | Shared | Explicit file ownership or serialized writes | Planner/implementer collaboration with a single checkout |
| `git_worktree` | Separate checkout and branch | One writer per worktree | Independent features, bug fixes, parallel alternatives |
| `container` | Container boundary; Git isolation must be stated separately | Policy-gated | Reproducible builds and tool/provider experiments |
| `remote_workspace` | Provider-managed; isolation must be evidenced | Policy-gated | Cloud agents and remote IDE sessions |

A container is not automatically a Git worktree. A new conversation is not automatically an isolated filesystem. A subagent is not automatically a separate checkout. A Git worktree isolates the checkout, branch, and terminal; it does **not** automatically isolate provider settings, BYOK credentials, extension configuration, shared state directories, network access, or other external resources. A communication board is not a scheduler, and stored messages do not prove delivery, reading, or action. Adapters must report the actual isolation boundary and the shared external state.

## Worktree lifecycle

```text
CREATE -> ACTIVE -> LOCKED -> RECONCILED -> RETAINED or REMOVED
```

- Create from an explicit base ref/SHA; record the returned worktree path and branch.
- ACTIVE permits the declared writer to work; other sessions remain read-only unless path ownership is disjoint.
- LOCKED is a coordination state that prevents new writes while review/reconciliation runs. It is not an authorization or security boundary.
- RECONCILED means the diff, tests, resulting SHA, and provenance have been checked against the canonical branch.
- Retain the worktree when debugging, review, or provenance requires it. Remove it only after uncommitted changes, branch ownership, artifacts, and evidence references have been checked.

A worktree manager may expose lock/unlock/remove operations, as demonstrated by the Sourcerer reference. Those are lifecycle conveniences; they do not replace Git review, permission checks, or the canonical promotion gate.

## Scheduling and conflict rules

1. Parallelize only tasks with independent inputs and bounded file ownership.
2. Prefer read-only parallelism when work is exploratory or tasks touch overlapping files.
3. Give every mutable worktree one declared write owner at a time.
4. If multiple sessions share a worktree, require explicit path ownership or serialize writes.
5. Competing implementations use separate worktrees and comparable task inputs; record treatment and cohort identity.
6. Do not hardcode a provider, model, IDE, or vendor-specific maximum concurrency as a system-wide rule.
7. Do not integrate merely because an agent reports completion. Review the diff and run relevant tests.
8. A successful merge or workflow is not a task outcome; preserve `TASK_PASS`, `TASK_FAIL`, or `UNKNOWN` separately from execution state and promotion.

## Required treatment metadata

The existing `ORCHESTRATION-TREATMENT.schema.json` gains an optional `workspace` object. It describes the intended treatment, not runtime proof:

- `isolation_mode`: declared workspace boundary.
- `writer_policy`: shared-write coordination rule.
- `integration_policy`: how changes return to the canonical branch.
- `max_parallel_sessions`: treatment-specific experimental bound, not a global limit.
- `base_ref`: requested source ref when applicable.

Runtime adapters must put observed workspace/session/branch facts in their own sanitized evidence artifact and reference that artifact from the existing canonical orchestration receipt's `evidence_ids`. Do not widen the receipt schema with provider-specific session payloads, and never store prompts, transcripts, credentials, environment values, browser profiles, or raw tool payloads in the evidence plane.

## Integration protocol

```text
RECON
  -> partition tasks by dependency and file ownership
  -> select workspace mode per task
  -> create/attach isolated workspace when required
  -> dispatch with declared owner + base SHA
  -> WAIT / WATCH actual session and workflow state
  -> fetch current branch/SHA and workspace evidence
  -> inspect diff and run focused tests
  -> reconcile conflicts and validate integrated result
  -> record outcome, attribution, cost/latency, and remaining work
  -> existing promotion/dual-gate decision
```

For a worktree, capture at minimum: repository identity, base ref and base SHA, branch, workspace identifier (opaque and non-secret), session identifier (opaque), executor/provider/model, declared owner, isolation mode, start/end timestamps, resulting head SHA, and evidence references. Treat unavailable fields as unknown; do not infer isolation from a product label.

## Safety and resource constraints

- Treat provider settings and BYOK credentials as shared unless the executor proves otherwise. Git worktree isolation is not credential isolation; use separate processes/containers and explicit secret scopes when credentials must be isolated.
- Worktree managers may copy `.env` files or run setup scripts during creation. Default to an explicit non-secret allowlist (`.env.example`); require reviewed opt-in before copying any credential-bearing file, and treat setup scripts as executable code subject to the normal trust boundary.
- Treat agent-to-agent board messages as untrusted coordination data, never as user approval or permission grants. Record dispatch and delivery state separately.

- Main checkout remains clean; create a separate worktree for edits.
- Keep caches, virtual environments, build artifacts, models, local databases, logs, session exports, and generated files outside tracked source unless explicitly part of the product.
- Do not share `CARGO_TARGET_DIR`, local databases, bound ports, emulators, or mutable caches across concurrent worktrees by default. Derive a per-worktree build/cache location; Rust 1.100 improves Cargo build-directory hash separation, but does not remove disk, lock, port, or cache contention.
- Codex Security scan history may intentionally be shared through a stable `CODEX_SECURITY_STATE_DIR`; use separate private state directories for independent experiments when cross-cohort deduplication would contaminate comparisons.
- Never commit credentials, API keys, cookies, browser profiles, CDP endpoints/tokens, or environment files.
- Do not force-push, merge, close, delete, deploy, or promote through an agent workspace unless the existing authority explicitly grants that action.
- Respect device storage and memory pressure. On constrained Termux devices, avoid cloning the repository per agent; use Git worktrees where supported and measure actual resource cost.
- A missing executor, failed setup, exhausted budget, or unavailable device is `CANNOT_EXECUTE`, not a model failure.
- A cancelled or superseded session remains cancelled/superseded in the evidence.

## Evaluation

Compare orchestration treatments on matched task cohorts. Reuse existing ATES, DoE/MVT, Action/Effect, evidence, and MoneyBall/3L0 contracts.

Measure at least:
- integrated task outcome and regression count;
- time to accepted integration;
- useful work versus duplicate work;
- context and token consumption where available;
- retries, conflicts, and human interventions;
- build/test cost and workspace resource footprint;
- attribution confidence and provenance completeness.

Quality and evidence dominate throughput. More concurrent agents, more commits, lower latency, or lower inference cost are not success by themselves.

## Adoption status and gates

| Capability | Status |
|---|---|
| Existing orchestration and receipt contracts | Existing repository foundation |
| Worktree treatment metadata | Added as optional schema extension in this proposal |
| Kilo Agent Manager | External reference; not a dependency |
| #5507 agent-browser | Separate browser-executor candidate; Termux runtime not established |
| Rust 1.100 validation | Tracked independently in #5492 |
| Native multi-agent worktree runtime in Termux | Not established |
| Production dispatch or auto-promotion | Not authorized by this document |

Promotion requires implementation evidence from the actual adapter, isolation tests, failure-state tests, resource measurements on the target device where applicable, current-SHA CI, review, and the repository's existing dual gates.

## Sources

- Kilo Agent Manager: https://kilo.ai/docs/automate/agent-manager
- Sourcerer / Dezelin worktree-management reference: https://www.threads.com/@dezelin/post/DfVdMTcjGTc
- Rust 1.100.0 Cargo build-directory and dependency-cooldown changes: https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/
- Kilo Agent Manager workflows: https://kilo.ai/docs/automate/agent-manager-workflows
- Kilo multi-project Agent Manager: https://kilo.ai/docs/automate/agent-manager-projects
- XDA article (15 Nov 2026): https://www.xda-developers.com/replaced-claude-code-codex-google-antigravity-coding-tool-feel-outdated/
