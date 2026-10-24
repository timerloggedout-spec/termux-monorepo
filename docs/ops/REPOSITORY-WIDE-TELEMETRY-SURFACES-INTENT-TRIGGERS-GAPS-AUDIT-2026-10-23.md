# Repository-Wide Telemetry Surfaces, Intent Mappings, Triggers, and Gaps — RECON Audit

**Audit date:** 2026-10-23 (Pacific)  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Source snapshot inspected:** default-branch files at GitHub search/ref snapshot `7bfd678d90c0188999560eb361d334a9a2a08a12` (individual file SHAs are recorded in the evidence map below)  
**Purpose:** repository-wide telemetry discovery and architecture/validation audit  
**Scope correction:** this report covers the full telemetry ecosystem. RFP/Delphi is one lane among many; it is not the system boundary.  
**Claim discipline:** static source review and repository search only unless a runtime receipt is explicitly cited. No claim is made that every described lane is enabled, continuously running, fully integrated, or validated end-to-end.

---

## 1. Executive summary

The repository does not have one small “telemetry feature.” It has a broad, multi-lane evidence system spanning GitHub object history, Actions lifecycle and failures, agent execution, action/effect follow-through, task throughput, provenance, proposal/governance state, context relationships, provider/quota observations, Help-Wanted realization, research/foresight signals, lane events, self-healing/recovery, and downstream analytics/visualization.

The strongest architectural statement in the repository is in `docs/ops/AGENT-EVIDENCE-SUBSTRATE.md` and `docs/ops/EVIDENCE-PROJECTION-SURFACE.md`:

- **Canonical evidence:** repository-owned JSONL/receipt artifacts plus immutable Git SHA and run linkage.
- **Interoperability:** OpenTelemetry-compatible projection, not a requirement to use a hosted OpenTelemetry service.
- **GitHub/Git/Actions/artifacts:** upstream authoritative source events.
- **EPS / normalized event contracts:** bounded, provenance-bound projections; not a second source of truth.
- **Reducers and analytics:** derive metrics from evidence; do not rewrite source evidence.
- **SHE, Context Relationship Graph, Hex, Grafana, Gource, dashboards, and UI:** consumers/projections with different authority levels.
- **Promotion authority:** deterministic repository correctness gates plus explicit operator promotion; telemetry and quality metrics are observational unless a separate gate explicitly says otherwise.

### High-confidence conclusion

**The architecture is intentionally compositional, but its telemetry contracts and persistence surfaces are plural.** The repository contains several compatible or overlapping event/evidence shapes—EPS, EVIDENCE-ENVELOPE, OPS-EVENT-GOURCE, ACTION-EFFECT-EVENT, agent-throughput events, ATES orchestrator traces, GitHub normalized facts, lane-event rows, and Help-Wanted realization receipts. This may be a deliberate layered architecture, but it creates a material integration obligation: adapters need explicit mappings, stable identity joins, version/compatibility policy, and contract tests proving that no lane silently drops semantics.

The most important audit question is therefore not “does a telemetry workflow exist?” It is:

> For each declared intent and each authoritative source event, can we discover the expected observer/trigger, identify the actual execution (or explicit skip/defer/failure), validate the emitted receipt, join it to immutable source identity, and distinguish observed fact from derived inference and promotion decision?

### Preliminary rating

| Dimension | RECON finding | Confidence |
|---|---|---|
| Architecture and policy | Strong, explicit separation of evidence, projections, metrics, and promotion | High |
| Source-surface breadth | Broad and multi-lane; source families are identifiable | High |
| Canonical event/evidence vocabulary | Partially converged; multiple schemas and specialized ledgers remain | High |
| Trigger-to-producer mapping | Exists in lane-specific docs/workflows; no single complete cross-repo mapping proved by this audit | High |
| Cross-lane correlation | Stable IDs/SHA/run joins are specified in multiple contracts; full end-to-end coverage is not established | High |
| Runtime receipt coverage | Some lanes document implemented emitters and artifacts; this audit did not re-run all producers | High |
| Historical completeness | Explicitly bounded by API retention, pagination, snapshots, artifact TTL, and backfill status | High |
| Dashboard/analytics authority | Correctly framed as projections in policy; individual consumers still need freshness/coverage metadata | High |
| Privacy and attribution | Strong metadata-first rules; enforcement must be tested per producer/adapter | High |
| RFP/Delphi | A meaningful lane in the broader graph, not the overall telemetry plane | High |

---

## 2. System boundary and layered architecture

### 2.1 Whole-system flow

```text
INTENT / POLICY / REGISTRIES
  proposal manifests · issue/PR/task intent · lane/term definitions · quotas · evaluation cohorts
                    |
                    v
AUTHORITATIVE SOURCE EVENTS
  GitHub issues/comments/PRs/reviews/commits/refs
  Actions workflow/run/job/step/artifact events
  agent/orchestrator/tool/provider/local-runtime events
  explicit human attestations and external verification
                    |
                    v
OBSERVERS / PRODUCERS / COLLECTORS
  Actions observers · GitHub API collectors · ATES emitters
  EPS producer workflows · issue/lane recorders · quota pollers
  historical correlation/backfill · contributor/proposal adapters
                    |
                    v
NORMALIZED EVENT + EVIDENCE CONTRACTS
  EPS event · evidence envelope · action-effect event
  agent throughput event · ATES trace · ops/Gource event
  lane event · runtime manifest · domain-specific receipt
                    |
                    v
VALIDATION / DEDUPE / RECONCILIATION
  schema validation · source-SHA check · idempotency
  explicit missing/partial/deferred states · artifact hash checks
  historical completeness checks · attribution and privacy rules
                    |
                    v
CANONICAL LEDGERS / RETAINED RECEIPTS
  append-only JSONL · immutable artifacts · GitHub object/run IDs
  lane-event database where configured · external verification receipt
                    |
                    v
REDUCERS / RELATIONSHIPS / DECISION SUPPORT
  SHE metrics and recovery · CRG · lead/lag · action effectiveness
  agent throughput/evaluation cohorts · provider quota/cadence
  Help-Wanted stage accounting · research/foresight registries
                    |
                    v
PROJECTIONS / CONSUMERS
  EPS bundles · Hex/Moneyball · Grafana · Gource
  generated reports/catalogs · dashboards/UI · ML/bench adapters
                    |
                    v
GOVERNED DECISION / PROMOTION
  repository checks + current-SHA evidence + independent review
  explicit operator authorization; never inferred from dashboard score
```

This is a conceptual dependency map based on repository contracts. It does not assert that every arrow is implemented for every source/consumer pair.

### 2.2 Authority boundaries

| Layer | Owns | Must not do |
|---|---|---|
| Intent/control registries | What is requested, eligibility, scope, policy, expected gates | Pretend a declared intent means execution occurred |
| Source systems | Actual GitHub objects, Actions runs/jobs, local/provider results | Derive unrelated quality or causal claims from raw activity alone |
| Observers/collectors | Read source evidence and report observations | Execute untrusted triggering code or rewrite source history |
| Event/evidence schemas | Normalize identity, state, provenance, status, evidence references | Silently discard source-specific semantics or treat missing fields as success |
| Ledgers/artifacts | Preserve dated records and immutable references/hashes | Become truth merely because a record exists; attestations still require verification |
| Reducers/graphs | Derive metrics, relationships, temporal patterns and cohort summaries | Manufacture missing values, promote inferred edges to verified, infer causality from time |
| Dashboards/analytics | Query and present projections | Become a source of truth, authorization surface, or merge/promotion authority |
| Promotion | Apply repository gates and explicit authorization | Use telemetry volume, model score, or a green unrelated workflow as a substitute for required evidence |

---

## 3. Telemetry surface inventory

This is the primary system map. “Evidence status” describes what repository sources document; it is not a fresh runtime health check.

| Surface / family | Intent and unit of observation | Main source/trigger surface | Output / downstream use | Key gaps to validate |
|---|---|---|---|---|
| **GitHub object history** | Reconstruct issue → comment → PR → review → commit → run → artifact history | REST/GraphQL objects, refs, timestamps, stable IDs | Historical event ledger and correlation artifacts | Pagination, retention, event ordering, deleted/edited objects, stable joins |
| **GitHub Actions run observability** | Observe completed workflow runs and actionable failures | `workflow_run: completed`; watcher and SHE ingestion | Incident records, notification, normalized run/job state | Ensure observer runs on all expected completions; distinguish observation from notification |
| **GitHub telemetry snapshots** | Capture repo statistics, Actions usage, traffic, projects, discussions | Daily/scheduled snapshot workflow and explicit dispatch | Raw dated snapshots → normalized facts → versioned aggregates | Traffic API has 14-day retention; UI metrics require local reconstruction/reconciliation |
| **Historical correlation/backfill** | Link all historical GitHub event types and temporal follow-through | Scheduled/dispatch correlation workflow and API harvesting | Immutable correlation artifact, historical corpus and graph inputs | Bounded pages/windows, checkpoint integrity, partial history, cursor advancement |
| **EPS (Evidence Projection Surface)** | Emit small immutable, source-linked normalized events for consumers | PR production ledger; admitted agent-throughput observer; other explicit producers | EPS NDJSON bundles, reducers, analytics/Hex/Grafana/CRG | Producer coverage, schema drift, event identity, consumer parity, source freshness |
| **Generic evidence envelope** | SHA-bound evidence shared by reconciliation, MVT/DOE, recovery, review and platform adapters | Domain producers/validators | Portable evidence receipt | Required fields/status enum differ from richer domain contracts; source class/fixture identity may be absent |
| **Action → effect correlation** | Measure whether an actionable discussion/review event is followed by a tree effect and validation | GitHub issue comments/reviews/review comments plus PR commit ranges | Action-effect ledger and effectiveness deltas | Temporal association is not causality; attribution and head-SHA freshness must remain explicit |
| **Agent throughput / ATES** | Observe task start/completion, active windows, tool calls/retries/handoffs, run duration and task boundary | Completed-run observer for explicitly admitted agent workflows; runtime emitters | ATES JSONL, TCV/WTCV/TPV/RPI and related reducers | Missing baseline/complexity/token metrics remain null; admitted workflows are not all agents |
| **ATES orchestrator trace** | Observe orchestration boundaries and parent/child spans for matched benchmark cohorts | Runtime trace wrappers and bounded benchmark workflow | `ates.orchestrator.trace.v1`, deterministic reduction, optional MLflow adapter | Runtime adoption coverage, async parent propagation, trace completion and cohort comparability |
| **Agent/contributor provenance** | Attribute source, agent, task, provider, run, SHA, environment and artifact | Contributor provenance proposal and runtime manifest builders | Provenance records and graph edges | GitHub actor ≠ agent identity; inference confidence and private identity linkage need policy |
| **Context Relationship Graph (CRG)** | Link issues, PRs, commits, files, reviews, comments, events, runs and outcomes | Historical event corpus, repository metadata, graph build/backfill | Verified/derived/inferred/candidate graph and context index | Temporal corpus completeness, stale graph roots, inferred edge handling, no unsupported causal claims |
| **SHE (Self-Healing Engine)** | Normalize incidents and govern recovery/verification/learning/attestation/promotion | Actions run/job ingestion, incident state, recovery plans and gate results | Incident records, recovery plans, validation receipts, learning records | Recovery authority must stay downstream of evidence; observer failure must not disappear |
| **Lane-events ledger** | Record cross-lane workflow/run outcomes durably and idempotently | Reusable `lane-event` action; `workflow_run` recorder for Help-Wanted/SHE | Append-only Postgres ledger when configured; readback count | Writer intentionally no-ops without credentials; configured/unconfigured state must be visible |
| **Help-Wanted / tribute lifecycle** | Track discovery → eligibility → claim/stake → implementation → validation → upstream acceptance → independently verified effect | Candidate audit, issue/PR changes, validation runs, realization-evidence JSONL | Stage-specific audit ledger and generated report | Merge/comment/test alone is not realized effect; external verifier and evidence required |
| **Provider/model catalog and quota telemetry** | Observe catalog/pricing/access/quota/reset, invoke outcomes and route availability | Scheduled catalog sync/pollers, headers/status responses, quota registries, provider workflows | Catalog snapshots, quota windows, route decisions, cadence summaries | Public entitlement ≠ account balance; rate limit ≠ zero work; no silent provider substitution |
| **Decision tree / workflow inventory** | Declare which workflow runs for an event and which permissions/capabilities apply | Workflow YAML + generator `scripts/ci/automation_docs.py` | Generated Markdown/JSON catalog, decision tree and overview | Catalog can drift from active GitHub workflow IDs or runtime runs; workflow file ≠ live run |
| **Proposal governance and RFP/Delphi** | Register proposals, collect marked intake, evaluate RFP issue lifecycle and emit selected signals | Proposal path filters; issue/comment/repository_dispatch/workflow_run/push/schedule/manual dispatch | Registry validation, Delphi issue ledger, signal events, run artifacts | One lane among many; per-proposal run/result receipts must be independently established |
| **Research / foresight / procurement signals** | Track source-backed technology signals, horizons, evidence status, decisions and procurement consequences | Research registries, resource/radar JSONL, source updates and validator workflows | Foresight registry, daily briefs, procurement/radar projections | Source freshness, evidence-status drift, duplicate identities, unsupported certainty |
| **Runtime/environment provenance** | Capture what executed, source SHA, environment/tools, artifacts and result | Runtime manifest builder and execution harness | Deterministic runtime manifest/AIBOM-compatible evidence | Environment capture and tool inventory need real runtime integration; static manifests do not prove execution |
| **Ops/Gource event stream** | Compact append-only temporal operation events with seek/readback and optional visualization | Evidence-envelope bridge and event conversion scripts | OPS event JSONL, SeekLog semantics, Gource projection | Gource-compatible actor/path semantics must not become authority; round-trip and timestamp tests |
| **External evaluators/analytics** | Compare agent/tool/manager cohorts using canonical evidence | Hex/Moneyball, Grafana, Langfuse/Phoenix/benchmark adapters and local cohorts | Derived metrics, dashboards, experiments, scores | Adapter is observational; cohort schema, source freshness, reproducibility and exportability required |
| **Legacy/local telemetry** | Capture local Termux/multi-agent sessions and run history | `src/telemetry.py`, nested multi-agent telemetry and JSONL histories | Local log streams and historical records | Multiple similar files/log formats risk divergent semantics; map to canonical events without destroying source history |

---

## 4. Intent vocabulary and trigger taxonomy

A repository-wide map must distinguish **intent**, **source event**, **trigger delivery**, **execution state**, **observed effect**, **validation**, and **promotion**. They are related but not interchangeable.

### 4.1 Intent classes

| Intent class | Typical declaration | Expected telemetry |
|---|---|---|
| Governance / registration | Proposal manifest, registry entry, issue/PR scope | Stable intent ID, registry revision, requested gates and status |
| Review / human decision | Review request, ballot or explicit attestation | Review/ballot ID, eligibility, decision, timestamp, source SHA |
| Code mutation | PR/commit, agent task or bounded writer action | Before/after SHA, changed-tree summary, action ID, validation |
| Runtime execution | Workflow dispatch, agent invocation, tool/API operation | Run/session/trace IDs, attempt, start/end, state and outcome |
| Source observation | Poll, API fetch, catalog read, external signal | Source URI/ID, observed-at time, cursor/window, status, response hash |
| Experiment / evaluation | Frozen task, cohort, fixture, rubric and treatment | Experiment/cohort/task ID, factor hashes, repetition, result and evaluator |
| Incident / recovery | Failed/timed-out workflow, incident, recovery plan | Incident fingerprint, source run, classification, action/effect, verification |
| Realized effect | Independently verified downstream outcome | Canonical PR/effect URL, verifier, method, timestamp, reproducible evidence |
| Resource / quota decision | Observed pricing, access, remaining quota, reset or rate limit | Provider/model, source, status/header, reset semantics, decision and reason |
| Relationship / historical inference | Candidate graph edge, temporal correlation, backfill | Stable endpoint IDs, edge class/confidence, history window and derivation |
| Promotion / authorization | Required gates and explicit operator decision | Current SHA, gate receipts, reviewer/approver, decision and residual risk |

### 4.2 Trigger families to enumerate

- **GitHub object events:** `push`, `pull_request`, `pull_request_review`, `pull_request_review_comment`, `issues`, `issue_comment`, `discussion` where configured.
- **Actions lifecycle events:** `workflow_run`, workflow job/artifact retrieval, completion observers, rerun attempts.
- **Explicit dispatch:** `workflow_dispatch`, `repository_dispatch`, reusable `workflow_call`, custom signals and bounded event payloads.
- **Time-based observation:** schedules and cadence windows; schedule execution is not guaranteed to occur at the exact requested minute.
- **Filesystem/path filters:** proposal, registry, schema, generated catalog, source config, provider or lane-specific path changes.
- **External data refresh:** GitHub API/GraphQL snapshots, public catalog polling, provider response/quota headers, research source refresh.
- **Runtime instrumentation:** spans/events emitted by agents, tools, local baselines and orchestration boundaries.
- **Human-attested evidence:** independent verifier, explicit review/approval, accepted/merged upstream outcome, ballot/decision record.
- **Recovery/control triggers:** incident fingerprints, retry/reset windows, stale SHA, missing receipt, validation failure and explicit promotion request.

For every trigger, record both the **expected mapping** and the **observed result**. A trigger definition is not proof that the event was delivered; a dispatch API success is not proof that a run began; a run completion is not proof that the requested task succeeded.

---

## 5. Canonical identifiers and joins

The repository already specifies a useful orchestration identity chain:

`orchestration_id → cycle_id → attempt_id → action_id → event_id → evidence_id`

This should be joined to GitHub's immutable/native identifiers and domain IDs:

| Entity | Preferred identity | Join edges |
|---|---|---|
| Repository | `owner/name` | All source/evidence records |
| Ref/commit | Full ref + 40-hex SHA | Workflow run, proposal version, diff, validation, artifact |
| Issue / discussion | Number + node ID / comment ID | Intent, intake, decision, later PR/commit/run |
| Pull request | Number + head/base SHA | Reviews, commits, checks, run, artifacts, effect |
| Review/comment | Review ID/comment ID + PR + path/SHA when known | Follow-up commits, finding disposition |
| Workflow | Stable workflow ID + path/name | Run event, catalog mapping, active/disabled state |
| Workflow run | Run ID + attempt + head SHA/ref | Jobs, steps, artifacts, observer receipts |
| Job/step | Job ID + stable step name/index where available | Runtime, failure, timing, artifact output |
| Artifact | Artifact ID/name + run ID + digest/retention | Receipt, task result, reproduction |
| Agent/session | Declared agent ID + session/trace ID | Task, provider/model, tool operations, run |
| Task/experiment | Task ID/fingerprint + cohort/repetition | Fixture, treatment, evaluator, outcome |
| Proposal/term | Stable proposal ID + revision SHA + term/round ID | Intent, source class, dispatch, receipt, decision |
| Provider/model | Provider route + model ID/version when known | Catalog/quota/invocation outcome |
| External realization | Canonical effect URL + independent verification ID | Upstream PR, release/benchmark, verified impact |

Do not use display names as identity when a stable ID exists. Preserve the distinction between an event's creator, triggering actor, code author, executor/agent, provider/model, reviewer, verifier, and approver.

### Correlation quality classes

- **Verified:** direct immutable ID or artifact evidence.
- **Derived:** deterministic join over verified identifiers.
- **Inferred:** plausible temporal/semantic relationship with uncertainty.
- **Candidate:** discovered relationship awaiting validation.
- **Missing/ambiguous:** no defensible join; do not fill by fuzzy matching unless the contract explicitly permits a candidate-only fallback.

The Context Relationship Graph contract explicitly prohibits silently promoting inferred edges to verified and treats temporal relationships as non-causal absent additional evidence.

---

## 6. Event and evidence contracts: overlap map

| Contract | Primary grain | Strength | Integration risk / mapping requirement |
|---|---|---|---|
| `EPS-EVENT.schema.json` (`eps.v1`) | Normalized source event | Event ID/type/time, repo, SHA, run/attempt, entity, status, provenance, bounded attributes | Status vocabulary differs from other schemas; attributes can carry domain fields but need named mappings and validation |
| `EVIDENCE-ENVELOPE.schema.json` | Experiment/reconciliation evidence | Required experiment/source/source ID, commit/baseline SHA, observed time, status/outcome, provenance, confidence | Required commit/baseline SHA can be awkward for non-code observations; lacks some run-attempt, source-class, fixture, privacy and explicit missingness fields |
| `ACTION-EFFECT-EVENT.schema.json` | Action-to-follow-through observation | Temporal event-to-commit and validation linkage | Must preserve “followed by” rather than causal attribution; specialized lifecycle statuses need mapping |
| `OPS-EVENT-GOURCE.schema.json` | Compact append-only operation | Seekable time/actor/op/path and optional lane/SHA/status/meta | Visualization-friendly operation model is not a replacement for richer event/evidence schema |
| `AGENT-THROUGHPUT-EVENT.schema.json` | Agent task/runtime observation | Start/completion/active window, task fingerprint, complexity/timing fields | Throughput metrics depend on valid task boundary and comparable cohorts; absent baseline stays null |
| `ATES-ORCHESTRATOR-TRACE.schema.json` / `ates.orchestrator.trace.v1` | Span/trace in a benchmarked orchestration | Parent/child execution trace, cohort/task factors | Must preserve async parent propagation, trace uniqueness and completed-span semantics |
| `AGENT-EVIDENCE-CONTRACT.md` | Vendor-neutral agent/tool event | agent/task/provider/model/tool/protocol/status and parent event | Must map to EPS without storing prompts/completions or collapsing protocol-specific event classes |
| Runtime manifest | Environment/run artifact manifest | Source SHA, runtime/tool/environment identity, artifacts | Needs actual execution-bound evidence; a generated manifest alone does not establish which binary ran |
| Lane-event SQL record | Cross-lane workflow/run subject outcome | Durable append-only DB row with idempotency key when configured | Optional DB credentials mean no-op mode; must expose configuration/receipt state |
| Help-Wanted realization record | Independently verified realized effect | External PR/effect/verification URLs, independent verifier and method | Cannot be synthesized from merge, comments, self-report or test alone |
| Delphi `delphi-result/v1` | Proposal term/source-class result | Source class, term/run, fixture/proposal SHA, dependency cluster, response hash, redaction status | Lane-specific; must adapt into canonical event/evidence without losing human-vs-model distinctions |

### Audit determination

These contracts should not necessarily be collapsed into one giant schema. A sound design can keep a **small canonical envelope plus versioned domain extensions**, but must publish and test the mappings. At minimum, the repository needs a machine-readable compatibility map that names each producer schema, canonical identity fields, state conversion, required fields, privacy rules, target schema, and lossiness.

Potential semantic mismatches to validate explicitly:
- `completed` (lifecycle) versus `passed` (task outcome);
- `skipped` versus `no data`;
- `partial` versus `failed`;
- `deferred` versus `queued`;
- `observed` versus `validated`;
- `source_id` versus `actor_id` versus `agent_id`;
- `run_id` versus `run_attempt` versus `trace_id`;
- `confidence` as correlation confidence versus model/evaluator confidence;
- event time versus observation time versus collection time;
- no receipt because not expected versus no receipt because collection failed.

---

## 7. Trigger → observer → receipt matrix

This matrix is the repository-wide test target. Exact workflow triggers must be read from current YAML/catalog during implementation; rows below identify the required observable mapping and named known surfaces.

| Source/intent | Trigger/observer surface | Expected receipt / result | Important non-equivalence |
|---|---|---|---|
| Proposal registry/package changed | Proposal lifecycle workflow path filters | Head-SHA registry validation result and PR check | Proposal CI is not proposal experiment execution |
| PR workflow completes | Agent-throughput observer for explicitly admitted agent workflows | Task-boundary ATES JSONL and reducer/receipt artifacts | Workflow runtime is not task success |
| Continuous agent ops completes | ATES run-receipt observer | Metadata-only receipt artifact with run/SHA/outcome | Observer artifact is not full task attribution if task boundary is missing |
| Any Actions run completes | Actions Run Watcher / SHE ingestion; other observers by allowlist | Normalized state; incident only for configured conclusions | Notification filter is not the full event ledger |
| Historical scan scheduled/dispatched | Historical event correlation workflow | Dated correlation artifact with query windows and cursor/coverage | A partial page is not a complete historical corpus |
| PR production ledger event | `pr-production-ledger.yml` EPS producer | EPS NDJSON artifact keyed to PR/SHA | Projection is not source of truth |
| Provider/catalog poll | Catalog sync workflow and quota reader | Snapshot, observed-at, access/pricing/quota evidence | Public plan/price does not prove remaining credits or invocation success |
| Lane workflow completes | Lane event recorder reusable action via workflow_run | Idempotent lane/run/attempt event if configured | Missing DB credential leads to no-op; do not count it as stored |
| Help-Wanted candidate audit | Scheduled/bounded candidate audit | Stage counts, evidence gaps, source PR/check references | Discovery/claim/merge is not verified realization |
| Independent realized effect verified | Append-only realization-evidence JSONL | Validated independent attestation and effect/verification URLs | Self-report cannot certify itself |
| Delphi RFP/issue changes | Delphi intake/gate/signal bridge | Issue ledger, decision/feedback signal and gate run references | Delphi is a single lane, not a global telemetry router |
| Orchestrator benchmark task runs | Runtime spans + benchmark reducer | Trace IDs, cohort/task/treatment factors, result receipt | Instrumentation alone is not a benchmark result |
| CRG graph/backfill runs | Historical corpus and graph build workflow | Graph/build manifest, source window, verified/derived/inferred/candidate edges | Graph projection cannot establish causality or current lineage if stale |
| External analytics query | Hex/Moneyball/Grafana/MLflow/other adapter | Versioned aggregate/query with source evidence references | External score/dashboard cannot promote or replace canonical evidence |
| Recovery/incident action | SHE incident→plan→execute→verify lifecycle | Incident key, action/effect evidence, validation and authorization | A recovery command/API success is not verified recovery |
| OPS/Gource conversion | Evidence-envelope-to-OPS event converter | Round-trippable append-only operation event | Rendered visualization is not canonical telemetry |
| Human review/approval | GitHub review or explicit authorization record | Reviewer/approver, current SHA, decision and required-gate links | Review text/comment volume is not automatically an approval or ballot |

---

## 8. State semantics and absence semantics

### 8.1 Keep the state dimensions orthogonal

The repository’s orchestration contract distinguishes:
- **Execution state:** DISPATCHED, QUEUED, RUNNING, WAITING, STEERED, RETRYING, COMPLETED, FAILED, CANCELLED.
- **Task outcome:** TASK_PASS, TASK_FAIL, UNKNOWN.
- **Promotion:** PROMOTABLE, NOT_PROMOTABLE, UNKNOWN.

Other contracts add `partial`, `skipped`, `blocked`, `superseded`, `deferred`, `emitted`, `failed`, and domain-specific values. These should be represented as separate dimensions or mapped by an explicit state table—not forced into one enum where semantics are lost.

Recommended dimensions:
1. trigger delivery: expected / accepted / rejected / unknown;
2. execution lifecycle: queued / running / completed / cancelled / timed out / unknown;
3. task outcome: pass / fail / inconclusive / unknown;
4. evidence state: valid / partial / invalid / missing / redaction-failed;
5. attribution: verified / derived / inferred / candidate / ambiguous;
6. decision: accept / reject / defer / park / require human / unknown;
7. promotion: authorized / not authorized / not applicable / unknown.

### 8.2 Missing is a first-class outcome

The repository’s telemetry audit contract is explicit: every eligible source workflow should produce a validated receipt or an explicit skip/partial receipt. Missing metrics are not zero. Rate limits are deferred, not zero work. Unmapped workflows produce skipped receipts. Optional task-boundary artifacts missing from a run lower attribution quality rather than justify fabricated task identity.

Every observer should classify at least:
- emitted;
- partial;
- skipped with reason;
- deferred due to rate limit/capacity;
- failed observer;
- expected but not observed;
- invalid or redaction-failed receipt;
- superseded by a newer immutable observation.

The source run ID/attempt/SHA and the observer’s own run ID/attempt should both be recorded. An observer failure must not erase the source event.

---

## 9. Metrics and evaluation surfaces

### 9.1 Operational GitHub metrics

The GitHub observability lane reconstructs versioned metrics from documented run/job, repository statistics, traffic, Projects and Discussions APIs. It explicitly does **not** claim exact parity with GitHub’s pre-aggregated Performance Metrics UI tables unless a reconciliation against UI CSV evidence establishes tolerance.

- Runtime = completed minus started timestamp.
- Queue time = started minus queued timestamp when available.
- Failure-rate denominator includes completed eligible jobs, with failure set governed by config.
- Latest attempt is the default aggregate view, while raw observations retain all attempts.
- Traffic endpoints retain only 14 days, requiring daily append-only snapshots.
- Code-frequency API can return 422 for large histories, requiring a documented fallback.

### 9.2 Agent throughput and quality

The adopted principle is quality over time. TCV is raw task velocity; WTCV weights complexity where valid; TPV/RPI and related measures add task/provenance/retry dimensions. These remain observational and must not be used as a speed-only merge gate.

The implemented Phase B observer documents Gemini Invoke, DeepSeek Termux Agent and DeepSeek CI as admitted sources. Jules dispatch is outside the execution-time ATES corpus until an attributable service/session receipt exists. Parallel yield and ATES remain null without an explicit measured sequential baseline.

### 9.3 Action-effect effectiveness

Measure the chain:
`ACTION → NEW HEAD? → TREE EFFECT? → VALIDATION? → FINDING RESOLVED? → ALIGNMENT IMPROVED?`

Keep discussion/review volume separate from implementation effect. Gross churn across all commits differs from retained base→head diff. A later commit is temporal follow-through, not proof of causal response to a comment.

### 9.4 External evaluators

The agent evaluation lane registry names repository-native development evaluation as canonical promotion evidence and external evaluators as bounded, observational adapters. Langfuse, Phoenix, GAMUT/Glama/TDQS and SWE-style suites can provide useful cohort data, but only when source evidence, task cohort, evaluator version, and exportable receipts are preserved.

### 9.5 Provider and quota telemetry

Provider availability must be measured from observed catalog/response/quota evidence. Public entitlement is not account balance; listed price is not proof of current availability; a 429/402 or retry-after is not zero work. A provider route decision should retain the policy version, observation time, route/model, observed status and reason, and any fallback decision. Silent substitution invalidates attribution.

---

## 10. Historical coverage, retention, and temporal integrity

The repository intentionally uses bounded collectors and rolling artifacts. The audit must therefore treat history as a coverage-qualified dataset, not an omniscient log.

Required metadata for every backfill/snapshot:
- query start/end and timezone;
- page bounds and pagination cursor before/after;
- total pages/items reported versus items fetched;
- rate-limit/defer state and retry-after;
- source API and API version;
- observed-at and collection-at timestamps;
- source/ref/SHA or immutable object IDs;
- excluded object types, deleted/unavailable items and reasons;
- artifact digest, retention/expiry and next checkpoint;
- coverage classification: complete for declared window / partial / stale / failed / unknown.

Known constraints documented in source:
- GitHub traffic data is retained for only 14 days by the API, so snapshots must be persisted daily.
- Historical correlation work is explicitly bounded and should retain cursor/window state; partial history is never complete history.
- Actions artifact retention is finite and differs by producer (some receipts document 30-day artifacts; Delphi documents a seven-day artifact for a particular output).
- The CRG historical-corpus explorer plan explicitly states that the explorer is not yet implemented, despite temporal-integrity validation work.
- Generated catalogs and snapshots can lag the live branch/workflow IDs; generated documentation must be refreshed and reconciled rather than trusted solely by filename.

No missing historical row should be interpreted as proof that an event never occurred. It may be outside retention, outside the query window, omitted by pagination, inaccessible, deleted, or not yet collected.

---

## 11. Privacy, security, and attribution controls

Repository-wide contracts consistently prohibit secrets and raw private content in canonical evidence:
- no prompts, completions, arbitrary message bodies, credentials, tokens, cookies, private session stores, browser profiles, or raw tool payloads;
- allowlisted metadata and bounded attributes only;
- hash/fingerprint raw text when a linkage key is genuinely needed;
- store stable object IDs and source references instead of discussion bodies;
- separate actor, code author, triggering actor, agent, provider/model, reviewer, independent verifier and approver;
- treat model/evaluator confidence as an observation, not ground truth;
- maintain explicit privacy tiers and redaction state for any restricted source;
- never treat a hashed identifier as automatically anonymous.

### Security and attribution tests required

1. Scan all emitted JSON/JSONL/artifacts for forbidden payload keys and secret-like values using synthetic fixtures.
2. Test that schema rejects unbounded/raw payload fields where prohibited.
3. Validate all source IDs and SHA/run links against the authoritative source.
4. Prove that external/provider adapters cannot alter canonical evidence or promotion status.
5. Prove observer workflows read triggering metadata but do not execute untrusted triggering commits.
6. Ensure actor/agent attribution stays unknown when ambiguous.
7. Test pseudonym linkability and retention policy separately from basic redaction.
8. Keep source data, derived relationship edges and inferred causal hypotheses distinct.

---

## 12. Repository-wide gaps and risks (prioritized)

### P0 — No single verified producer/consumer coverage matrix

The repository has a generated workflow catalog and many lane-specific contracts, but this RECON did not establish one authoritative matrix connecting every source event/intent to producer workflow, schema, ledger, validator, downstream consumer, owner, retention class and live runtime evidence.

**Closure:** generate a machine-readable surface registry and a coverage report from current YAML, schemas, source config, code entrypoints and explicit lane declarations. Unknown mappings should be visible rather than silently omitted.

### P0 — Contract plurality without a demonstrated full mapping

EPS, generic evidence envelope, action-effect, OPS/Gource, agent throughput, ATES trace, lane-event and domain-specific receipts overlap. They may serve distinct grains, but their compatibility/lossiness rules are not established by a single conformance test suite.

**Closure:** publish a schema compatibility matrix and adapter conformance fixtures. Every conversion must declare lossless/lossy fields and preserve source evidence links, state dimensions, time semantics and attribution confidence.

### P0 — Runtime evidence coverage is uneven by design

Some workflows are explicitly admitted to ATES; other services (e.g. Jules) are excluded until attributable execution receipts exist. Some lane events no-op without configured database credentials. Some runtime/graph surfaces are plans rather than complete implementations.

**Closure:** enumerate expected producers and classify each as enabled+observed, enabled+unobserved, intentionally excluded, credential-gated, planned, retired, or unknown. Do not infer coverage from docs alone.

### P0 — Trigger intent is fragmented across YAML, registries and documents

Triggers live in workflow YAML/path filters, issue labels/markers, repository_dispatch event allow-lists, workflow_run filters, schedules, and local producer scripts. The generated workflow catalog explains the control plane but cannot by itself prove live runtime coverage.

**Closure:** parse current YAML and compare to an intent-to-trigger registry; test missing paths/events, orphan workflows, disabled IDs, unregistered event names, unconsumed signals and unexpected trigger loops.

### P1 — State vocabularies are not yet proven semantically interoperable

Schemas use different status enums and some mix execution state with task outcome or evidence validity. “Completed,” “passed,” “observed,” “validated,” and “promoted” must remain distinct.

**Closure:** define a canonical multidimensional state model and explicit adapters; add table-driven conversion tests for all terminal and partial states.

### P1 — Idempotency and retry lineage differ across surfaces

Lane events have a specific hash/unique-key policy; Delphi uses input hashes and a bounded concurrency group; incident dedupe uses repository/workflow/source SHA/failure fingerprint; ATES events use their own event identity. These are reasonable local policies, but cross-lane retry semantics need a declared common minimum.

**Closure:** every producer records event ID, source event ID, source run/attempt, observer run/attempt, idempotency key, retry parent, and supersession relation. Test duplicate delivery, re-run and changed-input behavior.

### P1 — “Source of truth” boundaries are at risk of being blurred

Some systems use append-only JSONL, some GitHub artifacts/comments, some generated snapshots, some optional Postgres storage, and some external analytics. Projections can outlive source artifacts or be fresher than a stale registry.

**Closure:** for each field/entity specify the authoritative source, retention, projection regeneration method, and conflict policy. A projection disagreement must lead to source re-fetch, not projection overwrite of the source.

### P1 — Historical coverage is not self-evident

API retention, bounded batches, partial pagination, rate limits, stale generated files and unimplemented explorer surfaces can create silent blind spots.

**Closure:** standardize coverage manifests and checkpoint invariants; test page advancement, non-repeating cursor, bounded-window completeness and explicit exclusions.

### P1 — Privacy and attribution policies need cross-producer enforcement

The policies are strong, but multiple producer families mean a policy document does not prove every emitter adheres to it. GitHub identity is especially easy to overinterpret as agent identity or independent contribution.

**Closure:** common privacy conformance tests for every emitter/adapter; retain attribution confidence and unresolved ambiguity.

### P1 — Metrics can become accidental decision signals

Throughput, model/provider score, dashboard color, graph edge counts and activity volume are explicitly observational in the contracts, but they are tempting to use as promotion shortcuts.

**Closure:** machine-enforce a consumer boundary: only named gate artifacts and explicit human/operator authorization can promote; observational metrics cannot be consumed as promotion authority absent a versioned policy.

### P2 — Generated inventory can drift from live Actions state

The catalog is generated from source-controlled workflow definitions; GitHub can retain disabled/ghost workflow IDs, and source YAML may be renamed or removed.

**Closure:** scheduled/CI reconciliation of YAML path ↔ generated catalog ↔ active workflow IDs ↔ recent run observations. Retain disabled/phantom/stale records with a status rather than erasing them.

### P2 — Observability of the observer is inconsistent

The automated audit contract defines emitted/partial/skipped/deferred/failed outcomes, but the actual existence and validation of such a receipt must be checked for each observer. A failed collector can create the appearance of quiet source systems.

**Closure:** each observer reports its own health, source coverage, last successful observation, backlog, API quota/defer state and artifact publication status. Alert on observer silence separately from source failure.

### P2 — Local legacy telemetry is not visibly normalized end-to-end

Several similar `telemetry.py` paths and JSONL histories exist in the root and nested multi-agent trees. Search results alone do not establish whether they share a schema or are maintained as separate implementations.

**Closure:** inventory local log formats, classify active/reference/legacy copies, map to canonical events with compatibility tests, and preserve source histories.

---

## 13. Validation strategy and concrete gates

### Gate A — Discover and freeze the surface inventory

- Enumerate `.github/workflows/*.yml`, reusable actions, cron/dispatch/issue/PR/workflow_run triggers and path filters.
- Enumerate all JSON Schema files, event/evidence emitters, collectors, reducers, ledgers, generated catalogs and telemetry config.
- Parse explicit lane registries and source configs.
- Record owner, intent class, producer, trigger, schema, storage, consumers, retention and evidence status.
- Mark each mapping verified / derived / inferred / candidate / missing.

**Pass:** no silent orphan; every unknown has an explicit row.

### Gate B — Contract and adapter conformance

- Validate each producer output against its declared schema.
- Validate EPS and generic-envelope adapters with representative fixtures.
- Exercise all source/domain extensions, including Help-Wanted, ATES, runtime manifest, lane events, provider quota and Delphi.
- Assert field preservation, status mapping, timestamp semantics, ID linkage, and declared lossiness.
- Reject unknown required enums/fields safely without dropping source evidence.

**Pass:** deterministic conformance report, with all lossy mappings enumerated.

### Gate C — Trigger and routing coverage

For each declared intent, test:
- expected trigger fires;
- unrelated path/event does not claim a run;
- invalid/untrusted payload is rejected;
- allow-listed event dispatch creates the intended downstream run;
- downstream run ID is correlated back to trigger ID;
- permission denial/no run is an explicit result;
- replay is idempotent;
- changed source SHA/inputs cause the intended new evaluation;
- no event loop or unbounded fanout is created.

**Pass:** each declared intent has an observed trigger/run trace or explicit documented exclusion.

### Gate D — Runtime receipt integrity

- Join run → job → step → artifact → receipt → source SHA.
- Verify terminal conclusion and attempt.
- Verify artifact hash/digest and schema.
- Verify receipt publication and retention metadata.
- Test cancelled, skipped, timeout, rate-limit/defer, observer failure and missing artifact.
- Re-fetch current SHA/check state before any terminal success claim.

**Pass:** independent reconstruction from source IDs and receipts.

### Gate E — Historical and backfill integrity

- Assert cursor/page progression and stable window.
- Record rate-limit/defer events and retry windows.
- Reconcile source totals versus collected rows where APIs expose totals.
- Verify idempotent repeated backfill.
- Flag incomplete/expired source windows.
- Ensure stale graph/snapshot is not reported as current.

**Pass:** coverage manifest explicitly quantifies complete/partial/unavailable ranges.

### Gate F — Effectiveness and promotion boundary

- Distinguish comment/review from implementation effect.
- Distinguish code effect from validation and finding resolution.
- Require independent verification for realized external effect.
- Verify all promotion evidence is bound to current immutable SHA.
- Prove dashboards/metrics cannot directly authorize promotion.
- Keep all uncertainty and abstention states.

**Pass:** no promotion path bypasses declared gates or independent authorization.

### Gate G — Privacy and security

- Synthetic secret/payload fixtures fail redaction tests.
- No raw prompt/completion/tool payload enters canonical event storage.
- External adapters remain read-only and cannot overwrite canonical evidence.
- Attribution remains unknown when unsupported.
- Public/private receipt projection is tested.
- Access, retention and pseudonym policy is documented.

**Pass:** every producer has privacy conformance evidence.

---

## 14. Recommended compounding implementation order

1. **Generate the full surface registry** from source-controlled workflows, schemas, producers, collectors, reducers, ledgers and configs. This creates the first auditable denominator.
2. **Build the schema compatibility map** for EPS, evidence envelope, action-effect, OPS/Gource, ATES, runtime manifest, lane-event and domain receipts. Define the canonical core plus domain extensions rather than prematurely replacing all schemas.
3. **Implement one cross-surface conformance harness** that tests event identity, timestamp semantics, state mapping, provenance and field loss.
4. **Add coverage-aware observer receipts** to every eligible workflow: emitted/partial/skipped/deferred/failed, source IDs, observer run IDs, SHA, cursor/window, reason and artifact digest.
5. **Reconcile workflow YAML ↔ generated catalog ↔ live GitHub workflow IDs ↔ actual run observations.**
6. **Unify correlation IDs and retry lineage** across run observers, ATES, lane events, Help-Wanted, CRG and incident dedupe.
7. **Add historical coverage manifests and stale-source alarms** to backfill, traffic, catalog and graph surfaces.
8. **Harden privacy and attribution conformance** across all producers.
9. **Expose a read-only coverage dashboard/report** that shows expected vs observed events, receipt validity, lag, gaps and current-SHA alignment.
10. **Keep promotion explicitly downstream** of authoritative validation and operator approval; do not use telemetry adoption as an automatic promotion condition.

This order compounds because the surface registry and compatibility harness make every later lane cheaper to audit and integrate.

---

## 15. Source evidence map

The following repository sources were directly inspected during this RECON. They are intentionally listed by system role, not as a claim that each implementation has been runtime-tested.

### Canonical architecture and event contracts
- [Agent Evidence Substrate](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/AGENT-EVIDENCE-SUBSTRATE.md) — canonical JSONL/receipts, OTel boundary, evidence layers, promotion separation.
- [Evidence Projection Surface](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/EVIDENCE-PROJECTION-SURFACE.md) — EPS purpose, producers, envelope and consumers.
- [Evidence Envelope schema](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/EVIDENCE-ENVELOPE.schema.json) — generic SHA-bound evidence.
- [EPS event schema](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/EPS-EVENT.schema.json) — normalized event envelope.
- [OPS/Gource event schema](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/OPS-EVENT-GOURCE.schema.json) — append-only event IR.
- [Agent Evidence Contract](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/research/AGENT-EVIDENCE-CONTRACT.md) — vendor-neutral event vocabulary and privacy boundary.
- [Orchestration Contracts](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/ORCHESTRATION-CONTRACTS.md) — identity/state/treatment/adapter model.

### GitHub history, Actions and metrics
- [GitHub Observability](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/GITHUB-OBSERVABILITY.md) — source APIs, retention, normalized facts and metric policy.
- [Actions Run Observability](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/ACTIONS-RUN-OBSERVABILITY.md) — watcher/SHE ingestion and conclusion handling.
- [Actions Historical Correlation](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/ACTIONS-HISTORICAL-CORRELATION.md) — entity joins and history dimensions.
- [GitHub telemetry CLI](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/ops/github-telemetry/README.md) — collect/reduce/reconcile and scheduled snapshot workflow.
- [Automation decision tree](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/automation-decision-tree.md) and [generated workflow catalog](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/generated/automation-workflow-catalog.md) — declared trigger/control-plane map.

### Agent execution and effectiveness
- [Agent Throughput Phase B](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/AGENT-THROUGHPUT-PHASE-B.md) — admitted workflow observers and runtime receipt fields.
- [Agent Throughput Metrics](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/AGENT-THROUGHPUT-METRICS.md) — ATES semantics and metric limitations.
- [ATES orchestrator runtime adoption](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/ATES-ORCHESTRATOR-RUNTIME-ADOPTION.md) — trace adoption and optional MLflow boundary.
- [Action Effectiveness Ledger](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/ACTION-EFFECTIVENESS-LEDGER.md) — temporal follow-through and effectiveness.
- [Agent Evaluation Lane Registry](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/AGENT-EVALUATION-LANE-REGISTRY.md) — canonical vs observational evaluators.

### Provenance, graph, recovery and realization
- [Context Relationship Index](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/CONTEXT-RELATIONSHIP-INDEX.md) — relationship graph, edge confidence, context delta.
- [Context Relationship Evidence Matrix](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/CONTEXT-RELATIONSHIP-EVIDENCE-MATRIX.md) — metadata-only projection and verified/candidate distinction.
- [Automated Telemetry Audit](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/AUTOMATED-TELEMETRY-AUDIT.md) — emitted/partial/skipped/deferred/failed states and audit rules.
- [Help-Wanted realization evidence](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/HELP-WANTED-REALIZATION-EVIDENCE.md) — independent verifier and realized-effect contract.
- [Lane-events ledger](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/ops/lane-events/README.md) — durable idempotent lane/run ledger and no-op configuration behavior.
- [Runtime provenance / AIBOM](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/research/RUNTIME-PROVENANCE-AIBOM.md) — execution/environment manifest intent.

### Domain-specific lanes and cadence
- [Free quota windows](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/FREE-QUOTA-WINDOWS.md) — quota/access semantics.
- [Operations cadence](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/OPERATIONS-CADENCE.md) — UTC schedule and broad RECON loop.
- [Delphi lane contract](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/DELPHI-LANE-CONTRACT.md) — one domain-specific RFP signal lane.

### Implementation sources found by repository search
- `src/telemetry.py` and nested `termux-multi-agent/**/telemetry.py` — local telemetry implementations to inventory for schema parity.
- `she/telemetry/otel_projection.py` — optional OTel-shaped projection.
- `scripts/ci/emit_agent_throughput.py` and `scripts/ci/bridge_ates_trace_to_events.py` — agent event and trace bridges.
- `scripts/telemetry/emit_eps_event.py` — EPS event validation/emission.
- `scripts/ops/ops_event_seeklog.py` — evidence-envelope to OPS-event bridge.
- `scripts/github/historical_event_correlation.py` — historical event collector.
- `she/provenance/runtime_manifest.py` — runtime manifest builder.
- `ops/github_telemetry/` — GitHub telemetry collector/reducer CLI.
- `scripts/ops/lane_event.py` and `ops/lane-events/` — lane event writer/schema.
- `scripts/ci/help_wanted_tribute_audit.py` — Help-Wanted stage audit.

---

## 16. Final determination

The whole repository’s telemetry intent is a **source-backed, multi-lane evidence system**: collect authoritative events, normalize them without losing provenance, preserve immutable receipts, reconcile coverage and missingness, derive observational metrics and relationships, and keep decisions/promotions behind their own validation and authorization boundaries.

The strongest existing design principle is correct: **telemetry availability is infrastructure evidence, not task-quality score; a dashboard is a projection, not authority; missing evidence is not zero; and temporal correlation is not causality.**

The primary work now is not another lane-specific narrative. It is to make the whole surface enumerable and testable:
1. complete producer/consumer/trigger registry;
2. schema compatibility/conformance matrix;
3. per-lane expected-vs-observed coverage receipts;
4. common stable IDs, retry lineage and current-SHA validation;
5. retention-aware historical completeness;
6. privacy/attribution conformance;
7. read-only coverage dashboard/report;
8. promotion isolation.

**Status after this RECON:** architecture and source surfaces mapped at a substantial breadth; static findings recorded; runtime-wide completeness not established. Treat the report as a baseline for a machine-generated inventory and validation pass, not as certification that all telemetry paths are currently healthy.


---

## 17. Follow-up validation: proposal-to-Delphi workflow trigger boundary (2026-10-24)

This section records a targeted source audit performed after the repository-wide inventory. It is a concrete trigger-path finding, not a claim of a runtime execution.

### Declared workflow evidence

| Surface | Declared trigger | Observed responsibility | What it does not establish |
|---|---|---|---|
| `.github/workflows/proposal-lifecycle.yml` | `pull_request` for `docs/proposals/**`, `scripts/proposals/**`, and itself; `push` to `master`/`master-staging` for proposal/script paths; `workflow_dispatch` | Runs `scripts/proposals/validate_registry.py`; on PRs, performs advisory VOTE-line scan and may post proposal checklist | Does not itself dispatch a Delphi/RFP run or prove proposal-specific participation |
| `.github/workflows/delphi-gate.yml` | `issues`, `issue_comment`, typed `repository_dispatch`, completion of `vercel-quota-probe`, restricted `push` paths under `ops/quota` and `ops/delphi`, schedule, `workflow_dispatch` | Evaluates open issues labeled `delphi:rfp`, idempotently, and accepts bounded signal/feedback inputs | Does not declare `docs/proposals/**` as a direct pull-request or push trigger; a generic gate run is not evidence that each independent proposal was handled |
| `.github/workflows/delphi-signal.yml` | Reusable `workflow_call` | Validates a small event vocabulary and calls `gh workflow run delphi-gate.yml` | Emits a wake-up, not proof that a particular proposal identity was processed or that participation/consensus occurred |
| `.github/workflows/delphi-signal-bridge.yml` | ForeSight registry push and `delphi-gate` workflow completion | Bridges a specific registry signal and selected shadow-lane outcomes | No proposal-file trigger is declared here either |

### Gap classification

- **Confirmed from workflow source:** proposal lifecycle and Delphi gate have different event/path scopes. Proposal lifecycle validation alone is not a proposal-to-Delphi execution bridge.
- **Confirmed from workflow source:** Delphi gate's core evaluation command is invoked over open RFPs and its concurrency group is the shared `delphi-gate`; its current declared inputs do not constitute a proposal-specific run identity.
- **Not established by this static check:** whether an external automation or an uninspected downstream component creates equivalent runs; whether every independent DelphicAnonymityMethod contributor-participation proposal has a canonical registry entry; whether any qualifying run occurred for the latest candidate SHA.
- **Not inferred:** workflow execution does not prove contributor participation, anonymity, a vote, consensus, or a successful outcome.

### Required acceptance evidence

1. Identify canonical proposal IDs and paths from the registry and proposal manifests; do not substitute the AWS Strands proposal merely because PR #1611 is a useful merged lifecycle regression fixture.
2. For each eligible proposal identity, prove the exact event/path filter causes an Actions run on the candidate PR/commit SHA.
3. Preserve proposal ID/path, source PR or commit SHA, workflow/run ID, trigger event, conclusion, and a sanitized evidence receipt as distinct fields.
4. Add deterministic fixtures for at least two independent proposal IDs. Verify that changing A does not alias or suppress B and that retries remain idempotent without collapsing identity.
5. Keep this repository-only trigger test separate from paid provider inference or cloud-resource provisioning.
6. Report `triggered`, `queued`, `in_progress`, `success`, `failure`, `skipped`, `cancelled`, and `not_triggered` distinctly. Never convert absence of a run into a pass.

### Current determination

The static source audit supports a **proposal-to-Delphi trigger/identity gap** in the declared workflow graph. The next implementation step is a narrowly scoped, identity-preserving bridge plus deterministic tests and a real safe Actions run. This follow-up does not claim that implementation or runtime verification has already occurred.
