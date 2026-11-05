# Proposal: Polyglot Build Orchestration — Evidence-Led Evaluation and Governed Pipeline Integration

**ID:** `build-orchestration-evaluation`  
**Status:** posted; proposal only, not accepted for runtime implementation  
**Priority:** P1  
**Filed:** 2026-11-05  
**Owner:** proposal author ChatGPT; operator review requested  
**Branch:** `proposal/build-orchestration-evaluation`  
**Related governance:** `CLAUDE.md`, `docs/proposals/PROCESS.md`, `docs/CONSENSUS.md`, `docs/ARCHWIZ-GATE.md`, `archwiz/docs/PIPELINE.md`, `docs/agentic/AGENTIC_PHASE_FLOW_DESIGN.md`, existing DOE/MVT proposal.

---

## 1. Executive decision

Adopt an **adapter-based, evidence-led orchestration architecture** as the target design. Do not select a permanent engine until representative repository workloads have been measured under a shared contract.

The initial shortlist is:

1. **Native project tooling** — baseline and mandatory escape hatch.
2. **Moonrepo** — leading polyglot candidate to test first.
3. **Nx** — strong graph/affected-task and extensibility comparator.
4. **Turborepo** — targeted JS/TS candidate, not presumed to orchestrate the whole repository.
5. **Bazel** — bounded reference candidate for hermetic/reproducible builds; not a default due to adoption and maintenance cost.

The proposal does **not** authorize installing or enabling a root-wide tool, introducing remote caching, dispatching workflows, changing task execution semantics, or modifying production pipelines. It authorizes review of this proposal and, after acceptance, the bounded inventory and benchmark work items.

**Recommendation:** preserve the current control plane; add a narrow orchestration adapter boundary. Build tools execute declared tasks. They do not own governance, approval, workflow authority, secrets, proposal state, or promotion.

## 2. Problem statement and opportunity

The repository is a mixed research, automation, and agentic-development monorepo with Android/Termux as the primary execution target. Its existing project discovery logic recognizes multiple ecosystems (including npm, Cargo, Go, and Python manifests), while its operational system already contains multiple pipeline and flow concepts.

The current architecture therefore has two distinct needs:

- **Project/task execution:** determine which project tasks are affected, order dependencies, execute safely, and reuse valid outputs.
- **Repository governance and orchestration:** decide whether work is authorized, which phase is eligible, what evidence is authoritative, which checks must pass, and whether promotion is permitted.

These are not the same problem. A build engine can optimize the first; it must not replace the second.

The earlier Turborepo fit review identified strong JS/TS task-graph and caching value but a weaker fit as the sole engine for a polyglot repository. This proposal refines that conclusion into a fair comparison and a concrete staged implementation.

### Verified repository context

- `CLAUDE.md` is the primary collaborator entry and binds the proposal registry, proposal process, dual gates, and adaptive WAIT loop.
- `docs/proposals/PROCESS.md` defines ingest → register → itemize → review → execute → close; proposal acceptance is separate from posting.
- `archwiz/docs/PIPELINE.md` documents a six-phase Fork → ForeSight → Generate → Validate → Promote → Index loop, plus ingestion, export/index, and context-scoping flows.
- `docs/agentic/AGENTIC_PHASE_FLOW_DESIGN.md` defines a separate, proposed dependency-phase control plane with validation, evaluation, idempotent readiness events, revalidation before dispatch, and no automatic promotion.
- The existing DOE/MVT live method-competition proposal defines pinned SHAs, live run receipts, observed-vs-planned cadence, controlled factors, and human merge authority.
- `.monorepo/discover_projects.py` is the current manifest-discovery precedent; it scans project roots and recognizes package, Cargo, Go, and Python manifests.
- The root repository should not be treated as a single JS workspace merely because nested projects may contain `package.json`. Workspace eligibility must be established by inventory.

These sources are architectural constraints and integration points, not evidence that a candidate build engine is already installed or configured.

## 3. Goals and non-goals

### Goals

1. Establish a canonical, language-neutral description of projects, tasks, dependencies, and execution evidence.
2. Compare candidates using identical task fixtures, immutable source revisions, equivalent environments, and predeclared metrics.
3. Reduce redundant work through correct affected-task selection and content/environment-aware caching.
4. Keep Termux/Android support first-class, with explicit capability detection and graceful native fallback.
5. Integrate measurements with existing DOE/MVT, action-effectiveness, and pipeline receipts without creating duplicate telemetry authorities.
6. Preserve existing proposal, dependency-phase, CI, review, dual-gate, and operator-approval boundaries.
7. Make adoption reversible: adapter removal must not strand project tasks or invalidate their native commands.

### Non-goals

- Replacing GitHub Actions, ArchWiz, dependency-phase governance, proposal lifecycle, or repo-gate/termux-smoke.
- Making every directory a managed project or forcing one language/package manager across the repository.
- Enabling automatic deployments, production dispatch, remote execution, or cache sharing as part of the proposal commit.
- Treating a green cache hit as proof of task correctness.
- Moving secrets into task definitions, logs, cache keys, or artifacts.
- Rewriting historical telemetry or backfilling inferred build outcomes as observed facts.
- Selecting a vendor based on feature checklists alone.

## 4. Architecture — separate execution from authority

### 4.1 Control-plane layers

| Layer | Owns | Must not own |
|---|---|---|
| Repository governance | Proposal acceptance, item scope, human-only approvals, merge/promotion authority | Build scheduling internals |
| Project inventory | Canonical project IDs, roots, manifests, language/toolchain hints, source confidence | Permission to execute |
| Task contract | Task IDs, commands/adapters, inputs, outputs, dependencies, resource class, environment requirements | Secrets or approval decisions |
| Orchestration adapter | Translate canonical tasks into native/Moon/Nx/Turbo/Bazel invocations; collect execution results | Proposal status, branch policy, merge authority |
| Execution surface | Termux, GitHub Actions, optional local runner; isolated work directories | Becoming a source of truth for authorization |
| Evidence plane | Immutable run receipts, metrics, provenance, cache observations, DOE linkage | Deleting or rewriting historical evidence |
| Presentation | ArchWiz cockpit, maps, dashboards, reports | Making dispatch or promotion decisions |

### 4.2 Canonical flow

```text
Proposal / approved dependency phase / explicit developer command
                         |
                         v
               Governance admission
          (scope + approval + branch + policy)
                         |
                         v
              Project/task inventory
                         |
                         v
              Dependency & impact graph
                         |
                         v
               Orchestration adapter
          +--------------+---------------+
          |              |               |
       Native          Moonrepo         Nx/Turbo
          |              |               |
          +--------------+---------------+
                         |
                         v
                Execution receipt
                         |
            +------------+-------------+
            |                          |
      Evidence/DOE ledger         CI/test artifacts
            |                          |
            +------------+-------------+
                         |
                         v
            Repo gates + review + outcome check
                         |
                         v
             Existing promotion authority
```

A task runner may report `success`, but the governance layer derives completion only when the task result, required tests, current commit, item state, and approval evidence agree.

### 4.3 Existing pipeline/flow integration map

| Existing surface | Relationship | Proposed integration |
|---|---|---|
| `archwiz/docs/PIPELINE.md` six-phase loop | Existing operational pipeline description | Add a build-task subflow under Generate/Validate; do not change Promote semantics. |
| `archwiz/pipeline.py` and dispatch pipeline | Existing ArchWiz dispatch/logging surface | Optional future adapter emits a receipt; no direct build dispatch in v1. |
| `docs/agentic/AGENTIC_PHASE_FLOW_DESIGN.md` | Proposed phase admission and dependency ordering | Treat phase eligibility as an upstream authorization input; revalidate immediately before any future dispatch. |
| `docs/proposals/registry.yaml` + ITEMS | Proposal intent and authorized scope | Require item IDs in all implementation receipts and PR descriptions. |
| DOE/MVT live method-competition | Controlled method comparison | Register each candidate as a treatment; pin base SHA, task fixture, trigger source, environment and observed cadence. |
| Action-effectiveness / evidence-envelope | Operational measurement and provenance | Reuse canonical evidence identities; do not create a competing telemetry store. |
| GitHub Actions | CI, validation, workflow execution | Keep workflow-level policy and checks in Actions; runner is an execution surface, not governance. |
| `repo-gate` + `termux-smoke` | Required repository quality gates | Both remain mandatory for promotion; candidate tools cannot waive or redefine them. |
| ArchWiz maps/dashboards | Navigation and observation | Display project/task graph and receipts as derived views, never as authoritative state. |

## 5. Candidate assessment and selection hypothesis

| Candidate | Best-fit role | Strengths to measure | Risks / limits to measure |
|---|---|---|---|
| Native tools | Baseline, fallback, simple projects | Lowest new dependency; ecosystem-native correctness; Termux compatibility | Repeated orchestration logic; limited cross-project graph/caching |
| Moonrepo | Leading polyglot candidate | Unified project/task graph; multi-language coordination; toolchain/task orchestration | Termux install/runtime support, configuration burden, remote-cache backend and ecosystem maturity |
| Nx | Graph and affected-task comparator | Project graph, affected detection, task caching, plugins/generators, distributed CI options | Node-centric control plane and plugin overhead; polyglot capability must be proven on actual tasks |
| Turborepo | JS/TS task lane | Low-friction package-script orchestration, parallelism, content-aware local/remote cache | JS/TS-first model; does not replace Cargo/Python/Go native tooling; workspace assumptions |
| Bazel | Bounded reproducibility comparator | Hermetic build model, explicit dependencies, remote cache/execution ecosystem | Rule/toolchain authoring and migration cost; potentially excessive for current repository scale |

### Selection hypothesis (not a decision)

Moonrepo is the first polyglot candidate to prototype; Nx is the second broad comparator; Turborepo is evaluated only on eligible JS/TS subgraphs; Bazel is limited to a small reproducibility reference. Native tooling remains the control group and permanent fallback.

A candidate wins only if it improves the measured workload without violating Termux compatibility, task correctness, maintainability, or governance.

## 6. Canonical project and task contracts

The inventory and schemas are proposed as versioned repository contracts. The first implementation should use a small explicit registry and derive richer maps from it.

### 6.1 Project record (illustrative)

```yaml
schema_version: 1
project_id: deepcli-tui
root: deepcli-tui
manifest:
  path: deepcli-tui/package.json
  kind: npm
  confidence: observed
toolchain:
  runtime: node
  version_source: package-manager-or-runtime-file
tasks:
  - task_id: deepcli-tui:test
    adapter: native
    command: ["npm", "test"]
    inputs: ["src/**", "test/**", "package.json", "lockfile"]
    outputs: []
    depends_on: []
    cache:
      mode: none
    environment:
      platform: [linux, android]
      network: false
```

This is an example only. Actual roots, scripts, versions, dependencies, and platform claims must come from BOE-00-01 inventory and tests.

### 6.2 Task invariants

- Stable task identity is `<project-id>:<task-name>`; never depend on directory enumeration order.
- Commands are argument arrays, not shell-interpolated strings, unless a shell is explicitly required and reviewed.
- Inputs include source files, manifests, lockfiles, toolchain declarations, relevant configuration, and declared environment values.
- Outputs are explicit paths; undeclared side effects make a task non-cacheable.
- Environment fingerprint includes OS/architecture, runtime/toolchain version, relevant configuration, and declared non-secret environment values.
- Dependencies form an acyclic directed graph; cycles and missing task IDs fail closed.
- Every task has a timeout, resource class, network policy, and failure policy.
- Secret values are never included in fingerprints, logs, cache metadata, receipts, or artifacts. If a task depends on a secret, it is non-cacheable by default and records only a stable secret-name/version marker if the platform can provide one safely.
- A cache hit is valid only when the full input and environment fingerprint match and output integrity is verified.
- Unknown tasks run natively only when explicitly admitted; unknown must never mean “run arbitrary command”.

### 6.3 Execution receipt (minimum fields)

```json
{
  "schema_version": 1,
  "receipt_id": "sha256:<canonical-run-identity>",
  "proposal_id": "build-orchestration-evaluation",
  "item_id": "BOE-10-01",
  "project_id": "observed-project-id",
  "task_id": "observed-project-id:test",
  "adapter": "native",
  "candidate": "control",
  "source_sha": "<immutable-git-sha>",
  "task_contract_sha256": "<digest>",
  "environment_fingerprint": "<digest>",
  "input_fingerprint": "<digest>",
  "trigger_source": "manual|workflow_dispatch|scheduled",
  "started_at": "<UTC timestamp>",
  "finished_at": "<UTC timestamp>",
  "exit_code": 0,
  "outcome": "passed|failed|canceled|timed_out|skipped",
  "cache": {"state": "disabled|miss|hit|rejected", "verified": false},
  "artifacts": [],
  "gate_evidence": [],
  "provenance": {"workflow_run_id": null, "runner": "termux|github-hosted|self-hosted"}
}
```

The schema must distinguish not-run, skipped, unavailable, failed, and unknown. Do not coerce missing evidence into success.

## 7. Fair benchmark and DOE/MVT design

### 7.1 Experimental unit and controls

- One task invocation on one immutable source SHA and one declared environment fingerprint is one observation.
- Repeated runs of the same task/SHA/environment are repeated measures, not independent projects.
- Compare equivalent tasks and outputs. Candidate-specific setup tasks are measured separately from steady-state task runtime.
- Pin lockfiles, toolchain versions, task inputs, runner class, resource limits, network policy, and task timeout.
- Run cold-cache and warm-cache trials separately. Cache state is a factor, not a hidden confounder.
- Randomize or block candidate order by project and time window where feasible; record order and trigger source.
- Record operator wakes and manual reruns; do not pool them blindly with scheduled runs.
- Exclude canceled/superseded runs from settled-build success, but retain their receipts with explicit exclusion reason.
- No live production task receives experimental treatment unless it is explicitly designated and admitted under the existing policy.

### 7.2 Primary and secondary outcomes

Primary outcomes:

1. Correctness parity: candidate output and exit status agree with native reference on the same fixture.
2. End-to-end wall-clock time (cold and warm).
3. Incremental execution precision/recall: tasks selected vs the true dependency-affected set.
4. Cache correctness: invalidation false-positive/false-negative rate and artifact integrity.
5. Termux compatibility: successful execution on the supported Android environment.

Secondary outcomes:

- CPU time, peak RSS, disk/cache footprint, network bytes, CI minutes.
- Cache hit ratio, cache transfer time, cache storage cost.
- Configuration lines and custom adapter code required.
- Upgrade burden, ecosystem friction, and maintenance incidents.
- Agent context tokens and human review time.
- Reproducibility across two clean workspaces and runner types.

### 7.3 Acceptance thresholds

Thresholds are predeclared for each pilot before data collection:

- Correctness: 100% parity for required outputs and no skipped required test.
- Safety: zero secret leakage, unauthorized dispatch, or promotion bypass.
- Dependency selection: no false negatives; false positives reported and quantified.
- Cache: zero incorrect cache reuse in the acceptance corpus; otherwise caching stays disabled.
- Performance: require a material improvement over native baseline (initial target ≥15% median wall-clock reduction on the eligible repeated workload) without >10% regression in p95 or unacceptable resource overhead. These are proposed pilot thresholds and may be changed only before the confirmatory run, with rationale recorded.
- Termux: no regression in native workflows; unsupported candidate execution must fall back to native execution with an explicit receipt, not silent skip.
- Maintenance: adapter/configuration overhead must be justified by measured saved work and operational simplicity.

A performance win cannot compensate for correctness or safety failure.

### 7.4 Sample size and confirmation

Use pilot runs to estimate variance and observed dispatch cadence. Calculate confirmatory sample requirements from observed rates; do not infer capacity from cron schedules. Use held-out tasks or later time windows for confirmation. Declare stopping rules and primary outcomes before running. If sample size is insufficient, report inconclusive rather than selecting a winner.

## 8. Cache and supply-chain security

1. Start with local cache only. Remote cache is a separate reviewed capability.
2. Cache only deterministic tasks with declared outputs and complete input/environment fingerprints.
3. Do not cache secret-dependent tasks, credentials, private browser/session state, or unclassified artifacts.
4. Treat cache storage as an artifact distribution boundary. Require repository-scoped authorization, least privilege, retention limits, integrity verification, and audit logs.
5. Require signed cache artifacts or an equivalent integrity mechanism before trusting cross-runner cache imports.
6. Prevent cache poisoning across forks and untrusted pull requests; untrusted PR jobs must not write trusted cache namespaces.
7. Never echo tokens or sensitive environment values. Task logs and artifacts are potentially retained and retrievable.
8. Make cache namespace include repository, trust class, task, contract version, and environment compatibility.
9. Cache eviction must not delete source evidence or telemetry receipts.
10. Remote execution is out of scope for the first release.

## 9. Termux-first compatibility

- Android/Termux is the reference execution target; GitHub-hosted Linux runners are comparison/support surfaces, not proof of Android support.
- Candidate installation must use documented package sources and pinned versions; no implicit root privileges or system-wide mutation.
- Detect runtime, architecture, filesystem semantics, symlink behavior, executable availability, and memory/disk constraints before selecting an adapter.
- Provide a native-command fallback for unsupported candidate features.
- Keep shell entry points POSIX-compatible where practical; avoid requiring Docker or a daemon on-device.
- Do not make network access a default task requirement.
- Validate on a real Termux device when available; if not, label device compatibility unverified and keep termux-smoke authoritative.
- Never let candidate-generated project files overwrite user state without explicit diff/review.

## 10. GitHub Actions and pipeline topology

The implementation should follow the separation already described in the agentic dependency-phase design:

| Workflow/job | Responsibility | Permission profile |
|---|---|---|
| Inventory/contract validation | Parse manifests and task registry; validate schema and graph | contents: read |
| Candidate evaluation | Run controlled benchmark fixtures on a pinned SHA | contents: read; checks: read |
| Optional execution dispatch (future) | Invoke a specifically approved task after fresh admission | minimum contents/issues/PR permissions required by the existing dispatch adapter |
| Evidence publication | Attach immutable run receipt and summary | contents: read; artifacts only unless explicit writer is approved |
| Existing repo gates | Run repo-gate and termux-smoke | unchanged; remain authoritative |

Use explicit `workflow_dispatch` or `repository_dispatch` contracts where required. Do not assume a bot-authored label/comment will trigger another workflow. Every dispatch must re-read the plan, branch, PR, proposal item, and approval evidence. Idempotency key should include plan digest, phase/task ID, source SHA, and environment fingerprint.

Do not create a new workflow in the proposal-only phase. The future workflow split is design intent subject to review and repository workflow-owner permission.

## 11. Implementation plan and rollout

| Phase | Work | Deliverable | Exit |
|---|---|---|---|
| 0 — Recon | Inventory manifests, tasks, dependencies, workflows, toolchains, and Termux constraints | Machine-readable inventory + unknowns ledger | Inventory reconciles to repository paths |
| 1 — Contract | Define project/task/receipt schemas and adapter interface | Versioned schemas + fixtures | Validation and negative tests pass |
| 2 — Baseline | Run native task corpus and collect cold/warm measurements | Baseline receipts | Repeatability and output parity established |
| 3 — Candidate pilots | Moon, Nx, Turbo, bounded Bazel comparison | Per-candidate adapter reports | Same tasks, same controls, comparable receipts |
| 4 — Evaluation | DOE/MVT analysis and cost/maintenance review | Candidate scorecard + ADR | Held-out confirmation supports selection |
| 5 — Integration | Add read-only registry/evaluator and evidence bridge | Minimal validated adapter integration | Existing pipelines unchanged; gates green |
| 6 — Controlled adoption | Enable selected adapter only for approved projects/tasks | Opt-in project migrations | Rollback and native fallback tested |
| 7 — Expand | Add more projects only where value is demonstrated | Versioned expansion plan | Each cohort independently justified |

### Rollback

- Disable the adapter at the project/task registry boundary.
- Execute the original native command.
- Keep all receipts and benchmark data.
- Invalidate candidate cache namespaces if integrity or keying is in doubt.
- Revert adapter integration without reverting project source changes.
- Never delete historical evidence to make a rollback appear clean.

## 12. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Wrong affected-task graph skips required work | Compare against native full-run oracle; fail closed on unknown dependency |
| Stale or incomplete cache key | Contract includes manifests, lockfiles, toolchain and environment fingerprint; negative invalidation tests |
| Remote cache leaks secrets/artifacts | Local-only first; trust namespaces, signing, allowlists, no secret-dependent caching |
| JS-centric tool becomes repo-wide standard by accident | Adapter boundary and language-specific pilots; native fallback |
| More config than value | Measure config/maintenance burden; require ROI threshold |
| CI and Termux differ | Separate environment cohorts; device verification required |
| Duplicate orchestration with ArchWiz or dependency phases | Existing governance remains upstream; build adapter is a leaf executor |
| Telemetry schema proliferation | Reuse evidence-envelope/action-effectiveness/DOE identities |
| Unreviewed dispatch or workflow-token assumptions | Explicit event contract, least privilege, fresh revalidation |
| Candidate churn or abandoned ecosystem | Pin versions, maintain native commands, adapter removable |

## 13. Governance and acceptance

- Proposal lifecycle remains authoritative. Posting this proposal does not equal acceptance.
- P1 acceptance requires the applicable non-author review / consensus tier under `docs/CONSENSUS.md`.
- No implementation beyond accepted `ITEMS.md` rows.
- Each implementation PR cites `Implements: BOE-XX-YY`.
- Do not modify workflow YAML, secrets, cache credentials, or remote infrastructure during the evaluation without the relevant permission and approved item.
- Both `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py` remain required for promotion.
- WAIT → VALIDATE → RE-FETCH: a queued or in-progress check is not a pass; verify immutable head SHA.
- No engine can waive review, approval, or promotion policy.

## 14. Decision requested

Review and decide:

1. Accept the adapter-based architecture as the design direction, subject to benchmark evidence.
2. Authorize BOE-00-01 and BOE-00-02 as the initial bounded implementation items.
3. Authorize candidate pilots only after the shared task contract and fixture set are approved.
4. Confirm Moonrepo as the first polyglot candidate to test, not the predetermined winner.
5. Keep Turbo limited to eligible JS/TS subgraphs unless evidence supports a broader role.
6. Keep remote cache, remote execution, workflow dispatch, and production adoption out of scope until separate security and operational review.

**The target outcome is not “install a monorepo tool.” It is a reproducible, Termux-compatible, evidence-producing execution layer that compounds the value of the pipelines already in place without taking authority away from them.**
