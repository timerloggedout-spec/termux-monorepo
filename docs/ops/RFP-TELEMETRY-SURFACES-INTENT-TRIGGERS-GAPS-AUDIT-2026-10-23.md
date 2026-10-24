# RFP/Delphi Lane Telemetry Notes — Narrow-Scope Supplement

> **Scope correction (2026-10-23):** this document covers only the RFP/Delphi lane. It is not the repository-wide telemetry audit and must not be read as the whole telemetry surface. The comprehensive cross-repository audit is [REPOSITORY-WIDE-TELEMETRY-SURFACES-INTENT-TRIGGERS-GAPS-AUDIT-2026-10-23.md](./REPOSITORY-WIDE-TELEMETRY-SURFACES-INTENT-TRIGGERS-GAPS-AUDIT-2026-10-23.md). That report maps the broader GitHub, Actions, EPS, ATES, evidence/provenance, action-effect, context-relationship, SHE, lane-events, Help-Wanted, quota/provider, historical-correlation, analytics and visualization surfaces. RFP/Delphi is one domain-specific lane within that ecosystem.

---

# RFP Telemetry Surfaces, Intent Mappings, Triggers, and Gaps — RECON / Validation Audit

**Audit date:** 2026-10-23 (Pacific; GitHub API observations may appear on 2026-10-24 UTC)  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Default-branch snapshot observed:** `767eea1c372bce592e9380fe22b3ad4a7b393959`  
**Relevant merged change:** PR [#1611](https://github.com/timerloggedout-spec/termux-monorepo/pull/1611), AWS Free Tier + Strands Decider Delphi Oracle RFP  
**Working documentation PR:** [#1612](https://github.com/timerloggedout-spec/termux-monorepo/pull/1612)  
**Audit type:** repository-source RECON and contract review; not a production certification, not a complete historical event replay, and not proof that every proposed contributor workflow has run.

---

## 1. Executive determination

### 1.1 Architectural interpretation

**The RFP is a telemetry plane.** It should preserve the observable lifecycle and evidence of independent proposal/contributor participation; it is not merely a Markdown request, scheduler, or trigger wrapper.

The architecture has four logically separate responsibilities:

1. **Intent/control plane** — defines the proposal/term, permitted action, eligibility, event policy, required gates, and approval boundary.
2. **Execution plane** — GitHub Actions workflows/jobs and any local/provider experiment that actually executes.
3. **Telemetry plane (RFP-facing)** — correlates intent, event, dispatch, run/job, contributor participation, lifecycle state, and result.
4. **Evidence plane** — stores verifiable receipts, immutable source/commit/run references, hashes, validation results, and explicit missingness.

These are logical planes, not a claim that four independently deployed services exist. Current implementation is distributed across proposal documents, issue events, Actions workflows, issue-comment ledgers, JSONL registries, schemas, and artifacts.

### 1.2 High-confidence findings

- **A generic proposal lifecycle trigger exists.** `.github/workflows/proposal-lifecycle.yml` runs on PRs touching `docs/proposals/**` or `scripts/proposals/**`, pushes to `master`/`master-staging` touching those paths, and manual dispatch. Its primary automated job validates the registry; a second PR-only job performs vote-hygiene/checklist behavior. This is not a proposal-specific experiment dispatcher.
- **A separate, established Delphi RFP event loop exists.** `.github/workflows/delphi-gate.yml` is event-driven around issues labelled `delphi:rfp`, selected comments, repository dispatch events, selected quota-registry pushes, completion of `vercel-quota-probe`, a bounded schedule heartbeat, and manual dispatch. It processes open RFP issues and uses an input hash for idempotency.
- **The intake path is marker-gated.** `.github/workflows/delphi-intake.yml` listens to issue comments but runs its intake job only when the comment contains `<!-- request-delphi-intake -->`, or on manual dispatch. It creates/finishes an RFP issue; this is not the same as independent contributor execution.
- **The internal signal bridge and reusable emitter exist.** `delphi-signal-bridge.yml` converts selected ForeSight registry pushes and selected completed shadow-lane runs into signal events; `delphi-signal.yml` validates event names/payload fields and calls `gh workflow run delphi-gate.yml`. This is the existing event-to-gate bridge for its declared signal types.
- **The proposal’s telemetry-acquired Delphi contract is documented but not fully evidenced as implemented end-to-end.** The AWS/Strands proposal’s `DEBATE.md` defines `delphi-result/v1`, source classes, deduplication key, dependency clustering, fixture/proposal SHA linkage, redaction, and explicit missing/failure states. The audited workflow/schema surfaces do not yet demonstrate a single canonical production contract carrying all those fields from every independent contributor proposal through run/job to a validated receipt.
- **The exact token `DelphicAnonymityMethod` did not return a match in default-branch GitHub code search during this audit.** The active proposal directory names matching Delphi/anonymity/contributor/participation searches were `agent-contributor-provenance` and `aws-free-tier-strands-delphi-oracle`; this is not proof that no differently named or external proposal exists. It means the exact canonical set of “independent DelphicAnonymityMethod contributor-participation proposals” could not be established from the searched default-branch identifiers.
- **A run receipt is not a participation receipt, and neither is a vote.** Existing proposal/Delphi documents explicitly prohibit converting generated rubric scores, model agreement, comments, emoji reactions, author count, or dispatch events into independent human ballots or consensus.
- **This audit did not dispatch workflows, provision AWS resources, call paid inference providers, or claim a proposal-specific run was executed.** The report records static configuration findings; runtime coverage must be verified separately against actual run IDs and receipts.

### 1.3 Overall audit verdict

**Partially implemented / contract fragmentation / trigger coverage unproven for the named independent proposal set.**

There is meaningful event-driven Delphi infrastructure and repository-wide proposal CI. The critical gap is the join between the *specific independent proposal intent* and *actual attributable execution/result telemetry*. A generic registry-validation run does not prove that each independent proposal has its own intended workflow trigger, and a Delphi gate run does not prove that a model/provider/human contributor participated.

---

## 2. Scope, evidence basis, and confidence rules

### Sources inspected

- [`proposal-lifecycle.yml`](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/.github/workflows/proposal-lifecycle.yml)
- [`delphi-gate.yml`](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/.github/workflows/delphi-gate.yml)
- [`delphi-intake.yml`](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/.github/workflows/delphi-intake.yml)
- [`delphi-signal.yml`](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/.github/workflows/delphi-signal.yml)
- [`delphi-signal-bridge.yml`](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/.github/workflows/delphi-signal-bridge.yml)
- [Delphi Oracle RFP Gate contract](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/DELPHI-ORACLE-RFP-GATE.md)
- [Delphi lane contract](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/DELPHI-LANE-CONTRACT.md)
- [AWS/Strands RFP](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/proposals/active/aws-free-tier-strands-delphi-oracle/RFP.md)
- [AWS/Strands experiment matrix](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/proposals/active/aws-free-tier-strands-delphi-oracle/EXPERIMENT-MATRIX.md)
- [AWS/Strands debate and telemetry-acquired Delphi contract](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/proposals/active/aws-free-tier-strands-delphi-oracle/DEBATE.md)
- [AWS/Strands manifest](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/proposals/active/aws-free-tier-strands-delphi-oracle/MANIFEST.md) and [items](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/proposals/active/aws-free-tier-strands-delphi-oracle/ITEMS.md)
- [Proposal registry](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/proposals/registry.yaml)
- [Action-effect event schema](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/ACTION-EFFECT-EVENT.schema.json)
- [Evidence envelope schema](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/EVIDENCE-ENVELOPE.schema.json)
- [Agent Evidence Substrate](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/AGENT-EVIDENCE-SUBSTRATE.md)
- [Generated automation workflow catalog](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/generated/automation-workflow-catalog.md)
- [Actions run observability](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/ACTIONS-RUN-OBSERVABILITY.md)

### Evidence labels used here

- **Observed in source:** directly present in a fetched file or API response.
- **Documented design:** a contract or intention written in repository docs; not necessarily implemented or exercised.
- **Inference:** a conclusion from comparing multiple surfaces; should be validated by a targeted test.
- **Not established:** no adequate source/run/receipt was found in the audited evidence. This does not mean the event never occurred.

The default-branch workflow catalog is generated documentation (it reported 178 catalogued workflow files at the inspected SHA); it is useful as an index but does not replace inspecting workflow YAML or checking live workflow runs. Repository workflow files, registered workflow IDs, and historical run records can diverge.

---

## 3. Telemetry surfaces inventory

| Surface | Primary intent | Trigger / input | Output / evidence | Audit interpretation |
|---|---|---|---|---|
| Proposal registry `docs/proposals/registry.yaml` | Register proposal identity, state, reviewers, related issues/PRs/branches, required gates | Committed registry edit | Structured proposal metadata | Identity/control index; not a run ledger |
| Proposal package `active/<id>/RFP.md`, `MANIFEST.md`, `ITEMS.md`, optional `DEBATE.md` | State scope, acceptance, lifecycle, review and work items | Human/agent authored proposal change | Versioned Git content and commit SHA | Intent source; should be correlated to execution |
| `proposal-lifecycle.yml` | Validate registry/package consistency and add PR hygiene checklist | PR path filter; master/master-staging push path filter; workflow_dispatch | Validation job and PR checklist comment | Generic governance CI, not independent experiment execution |
| Delphi issue intake `delphi-intake.yml` | Turn a marked issue comment or manual input into a completed Delphi RFP issue | `issue_comment.created` plus exact HTML marker; workflow_dispatch | RFP issue/comment/report | Intake receipt; not evidence that panel/experiment ran |
| Delphi gate `delphi-gate.yml` | Score/process open `delphi:rfp` issues, record decisions, manage cadence/feedback | `issues`, `issue_comment`, `repository_dispatch`, selected `workflow_run`, selected `push`, schedule, workflow_dispatch | Signed issue-comment ledger, labels, ForeSight/HindSight/3L0 records, run artifact | Main Delphi decision and lifecycle surface; mostly RFP-issue keyed |
| Reusable signal emitter `delphi-signal.yml` | Normalize/validate an allowed signal and request gate execution | `workflow_call` from sibling workflow | `gh workflow run delphi-gate.yml` | Dispatch bridge; its notice is not proof downstream processing completed |
| Signal bridge `delphi-signal-bridge.yml` | Convert selected upstream events into Delphi feedback/radar signals | ForeSight resource-registry push; completion of `delphi-gate` | Emits radar/outcome events when its conditions match | Narrow adapter, not a universal contributor completion observer |
| Delphi contracts `DELPHI-LANE-CONTRACT.md`, `DELPHI-ORACLE-RFP-GATE.md` | Define event names, issue labels, awards, cadence, feedback and records | Repository/issue events | Normative operational contract | Design is more specific than generic evidence schemas |
| Telemetry-acquired Delphi `DEBATE.md` | Normalize human, provider/model, local-baseline, automation-gate and driver-synthesis results | Intended collection of attributable completed results | `delphi-result/v1` example and sanitized receipt | Strong target contract; implementation coverage is not demonstrated by documentation alone |
| Generic evidence envelope `EVIDENCE-ENVELOPE.schema.json` | Portable evidence across reconciliation/MVT/recovery/review/platform adapters | Any conforming producer | SHA-bound evidence envelope | Useful common core but not sufficient alone for the full Delphi result/participation contract |
| Action-effect event `ACTION-EFFECT-EVENT.schema.json` | Correlate discussion/review events to later code effects | Issue comments/reviews and commit-range analysis | SHA-anchored temporal follow-through evidence | Useful for review-to-effect analysis; not a ballot/participation ledger |
| Agent Evidence Substrate | Preserve repo/ref/SHA/run/attempt, lifecycle, action-effect and provenance graph | Events/receipts from many lanes | JSONL/receipts and linked provenance | Architectural guidance; every producer must still implement the contract |
| Generated workflow catalog and Actions observability docs | Inventory workflow triggers and observe runs/jobs/checks | Workflow YAML refresh and Actions API observations | Catalog, status snapshots, artifacts and job evidence | Inventory/observer surfaces; do not assume complete event coverage from catalog alone |

### Key boundary

These surfaces answer different questions:

- **Registry:** “What is this proposal and what gates does it require?”
- **Workflow trigger:** “What event asked GitHub Actions to start a workflow?”
- **Workflow run/job:** “What did this workflow attempt, and what was its conclusion?”
- **Contributor participation receipt:** “Which declared source class submitted which attributable result for which frozen term/fixture?”
- **Decision ledger:** “What did the gate decide, using which inputs and policy?”
- **Experiment receipt:** “What test/experiment actually ran, against which fixture/configuration, and what did it observe?”
- **Promotion/approval record:** “Who or what authorized the next lifecycle state, under which gate?”

A single event or green check must not be treated as answering all seven questions.

---

## 4. Intent-to-trigger mappings

### 4.1 Proposal registration and validation

**Intent:** introduce or change a proposal, registry record, lifecycle metadata, or proposal helper.

**Observed trigger:** `proposal-lifecycle.yml` listens to `pull_request` changes in `docs/proposals/**`, `scripts/proposals/**`, or its own workflow file; it listens to pushes on `master`/`master-staging` touching `docs/proposals/**` or `scripts/proposals/**`; it supports `workflow_dispatch`.

**Observed action:** `validate-registry` checks out the source, installs PyYAML, executes `python3 scripts/proposals/validate_registry.py`, and emits an active-proposals summary. The PR-only `vote-hygiene` job scans title/body for VOTE lines and uses GitHub Script to post checklist behavior.

**What this proves:** a path-matching proposal change can cause registry/package validation and PR hygiene work.

**What it does not prove:** that a proposal’s own experiment, human review, provider/model run, or contribution workflow is launched; that every proposal receives an isolated run; that the checklist items have been completed; or that the proposal is accepted.

### 4.2 Delphi RFP issue intake

**Intent:** file a new RFP from an issue comment or explicit manual input.

**Observed trigger:** `delphi-intake.yml` listens to `issue_comment: created` and `workflow_dispatch`. The job condition requires the marker `<!-- request-delphi-intake -->` for comments. The parser accepts fields such as `surface`, `lane`, `quota`, `reset`, `auth` (secret name only), `lock-in`, and failure modes.

**Next expected event:** a filed issue labeled `delphi:rfp` should wake `delphi-gate.yml`.

**Gap to guard against:** intake completion and issue creation are separate from downstream gate execution. Each boundary needs its own observed run/issue ID and status. A missing marker or surface is an explicit non-filed intake result, not a successful RFP.

### 4.3 Delphi gate issue lifecycle

**Intent:** score, re-evaluate, park, award, or recheck an open RFP.

**Observed trigger families in `delphi-gate.yml`:**
- `issues`: opened, edited, labeled, reopened, gated to issues labelled `delphi:rfp`.
- `issue_comment`: created; non-bot comments on an RFP can wake the gate; supported operator feedback commands can submit confirmed/miss outcomes.
- `repository_dispatch`: `delphi-rfp`, `delphi-tick`, `quota-registry-changed`, `foresight-radar-hit`, `hindsight-forecast-miss`, `delphi-feedback`, `tribute-outcome`.
- `workflow_run`: completion of `vercel-quota-probe`.
- `push`: `master` changes under `ops/quota/registry.json` or `ops/delphi/**`.
- `schedule`: a three-day liveness heartbeat.
- `workflow_dispatch`: manual reason/depth/feedback/signal inputs.

**Observed protections:** concurrency group `delphi-gate`, `cancel-in-progress: false`; a 15-minute job timeout; no provider credentials passed to the rubric-only panel; comments from bots are excluded from the normal comment wake path; input-hash checks skip unchanged RFPs; the documented cadence chain is bounded.

**Output surfaces documented:** signed ledger comments, labels such as `delphi:converged`, `delphi:shadow`, `delphi:parked`, `delphi:needs-access`, `delphi:promoted`, ForeSight/HindSight/3L0 records and `delphi-records-<run>` artifacts.

**Interpretation:** this is a real event-driven RFP decision loop, but its unit of work is currently the open Delphi RFP issue/its input hash. That is not yet synonymous with an independent contributor-participation proposal or an independently attributable model/human result.

### 4.4 Reusable signal dispatch and bridge

**Intent:** wake the Delphi gate without requiring a personal access token in every sibling workflow.

**Observed mapping:** a caller invokes reusable `delphi-signal.yml` with an allow-listed event name. The emitter validates the event name, normalizes selected fields, validates `tribute-outcome` payload shape/size/weight, then runs `gh workflow run delphi-gate.yml` on the current ref.

**Observed bridge inputs:** `delphi-signal-bridge.yml` reacts to a push changing `data/foresight/resource-registry.jsonl` and to completed `delphi-gate` runs. The shadow-outcome path only emits when the mapped workflow/run conditions match; the documented example is three consecutive successes for confirmation or a success-to-failure transition for a miss.

**Gap:** a dispatch command can succeed while downstream execution is queued, cancelled, blocked, or absent. The emitter’s notice and the downstream run receipt must be correlated separately. Current bridge mappings are selective, so “all contributor workflows emit signals” is not established.

### 4.5 Telemetry-acquired independent contributor results

The proposal’s `DEBATE.md` defines these source classes:

- `HUMAN_COLLABORATOR`
- `MODEL_PROVIDER`
- `LOCAL_BASELINE`
- `AUTOMATION_GATE`
- `DRIVER_SYNTHESIS`

It requires completed, attributable results; deduplication by `term_id + source_id + run_id`; fixture-set hash; proposal commit; result state; evidence references; dependency cluster; timestamps; response hash; and redaction status. Missing, skipped, timed-out, invalid, rate-limited, and failed results must remain explicit rather than disappearing or becoming negative votes.

**Audit finding:** this is the right intent/result mapping, but a fully wired dispatch/collector/validator/receipt loop for each independent proposal was not demonstrated by the source and run evidence examined. The contract itself explicitly says its example is illustrative and that no provider outputs, human ballots, confidence values, or consensus have been fabricated.

---

## 5. Trigger matrix and expected telemetry

| Intent / event | Trigger surface | Expected execution | Minimum receipt | Common false positive to reject |
|---|---|---|---|---|
| Proposal file changed | `pull_request` path filter | proposal registry validation + PR hygiene | PR number, head SHA, workflow ID/run ID, job conclusions | “CI passed, so experiment ran” |
| Proposal merged/updated on default branch | `push` path filter | registry validation on resulting commit | commit SHA, run URL, registry validator result | “merged means accepted/promoted” |
| RFP intake requested | marked `issue_comment` or manual dispatch | intake parser and issue filing | comment ID, intake run ID, parse state, resulting issue number | “comment exists, so RFP filed” |
| RFP issue enters gate | issue label/event or signal dispatch | Delphi gate evaluates current RFP inputs | issue number, event/action, input hash, gate run ID | “label means gate completed” |
| Contributor/provider task dispatched | proposal-specific dispatch (not established generically) | one independently identified task/run per source/term | term ID, proposal ID, source class/ID, dispatch correlation ID | “dispatch command is a participant result” |
| Workflow/job starts | Actions run/job events or poller | actual job execution | run ID, attempt, job ID, started timestamp | “queued means started” |
| Workflow/job ends | completion event/API observation | normalized result state and conclusion | run/job IDs, conclusion, timestamps, logs/artifact refs | “green parent means all matrix jobs passed” |
| Human ballot submitted | approved ballot channel | ballot validation and registrar receipt | reviewer identity under access policy, ballot ID, term, timestamp, eligibility state | “comments/reactions/LLM rankings are ballots” |
| Model/provider result completed | provider-batch/adapter callback or artifact | schema validation, attribution, redaction and dedupe | provider/model version, run ID, fixture hash, response hash, result state | “provider catalog entry or API key means inference happened” |
| Local baseline completed | deterministic test harness | baseline result | source SHA, fixture hash, runtime/config, exit/result, artifact hash | “test definition means test ran” |
| Shadow lane outcome | mapped `workflow_run` sequence | confirmed/miss signal and reweighting | mapping ID, source run IDs, transition rule, emitted event/run ID | “one success proves promotion criterion” |
| Promotion requested | lifecycle/approval record | required gates and explicit approval | gate receipts on same immutable SHA, approver/authority, decision | “a score/label automatically authorizes deployment” |
| Retry/re-run | Actions attempt or explicit retry | new attempt linked to original run | original run ID, attempt number, retry reason, dedupe key | “retry is an independent contributor” |
| No run / blocked / rate limited | expected trigger has no valid run or is rejected | explicit missingness/blocked receipt | expected event ID, query window, status, reason, last observation | “no row means no event/no failure” |

---

## 6. Intent vocabulary and lifecycle state model

### 6.1 Keep intent separate from observation

Recommended conceptual records:

- **Proposal intent:** `proposal_id`, immutable `proposal_commit`, purpose, acceptance contract, source cohort, policy, required gates.
- **Term/round intent:** `term_id`, round, candidate/experiment set, frozen fixture/rubric hashes, opened/closed times, registrar.
- **Trigger intent:** expected event type, source, target workflow/ref, trigger correlation ID, permission decision.
- **Execution observation:** workflow ID, run ID, attempt, job ID, event name, head SHA/ref, queued/start/end timestamps, status/conclusion.
- **Participation observation:** source class, source ID, eligibility/attribution method, result ID, dependency cluster, participation state.
- **Result/evidence receipt:** schema version, fixture hash, proposal SHA, result, response/evidence hashes, redaction status, confidence/limitations.
- **Decision/promotion record:** policy version, evaluated evidence IDs, decision, authorizer, timestamp, gate disposition, supersession link.

These can be stored in different systems, but need stable join keys and a documented source of truth.

### 6.2 Suggested state machine

`PROPOSED → REGISTERED → ELIGIBILITY_CHECKED → DISPATCH_REQUESTED → DISPATCH_ACCEPTED → QUEUED → RUNNING → RESULT_COLLECTED → RECEIPT_VALIDATED → REVIEWED → DECIDED → PROMOTED / PARKED / REJECTED`

Terminal/exception states must remain explicit: `BLOCKED`, `NO_RUN`, `SKIPPED`, `CANCELLED`, `TIMED_OUT`, `RATE_LIMITED`, `INVALID_RESULT`, `REDACTION_FAILED`, `DUPLICATE`, `SUPERSEDED`, `UNKNOWN`.

This is a recommended state model, **not a claim that the repository currently implements this exact enum**. The current generic `EVIDENCE-ENVELOPE` status enum is narrower (`observed`, `running`, `passed`, `failed`, `skipped`, `blocked`, `superseded`) and does not include several states required by the Delphi contract.

---

## 7. Validation audit: what exists versus what remains unproven

| Control | Evidence found | Status | Validation needed |
|---|---|---|---|
| Proposal registry/package validation | `proposal-lifecycle.yml` calls `validate_registry.py` | Implemented as a workflow definition | Run on each relevant PR/head SHA; inspect complete check result |
| Generic proposal path triggers | PR/push path filters cover `docs/proposals/**` and `scripts/proposals/**` | Implemented for generic CI | Test independent proposal paths and ensure no ignored path or event-type hole |
| RFP intake marker | `delphi-intake.yml` marker gate and manual inputs | Implemented as workflow definition | Test marker present/missing, malformed/missing surface, duplicate comment, and downstream issue creation |
| Delphi gate events | issue/comment/repository_dispatch/workflow_run/push/schedule/dispatch triggers | Implemented as workflow definition | Verify one run per event family and correlation to expected issue/input hash |
| Signal event allow-list | `delphi-signal.yml` validates known event types and bounded tribute payload | Implemented as workflow definition | Negative tests for unknown events, invalid weights, invalid IDs, oversized arrays, and downstream run absence |
| Gate idempotency | docs and workflow describe concurrency + input hash skip | Documented/partly implemented | Replay identical event and prove no duplicate decision/result; replay changed inputs and prove new evaluation |
| Contributor source-class separation | `DEBATE.md` specifies source classes and no-vote boundaries | Documented contract | Test all classes and ensure human quorum excludes model, baseline, gate and driver synthesis |
| Result envelope | `DEBATE.md` shows `delphi-result/v1` example | Documented target | Find/validate canonical schema and writer/reader in code; contract test every required field |
| Generic evidence envelope | `EVIDENCE-ENVELOPE.schema.json` exists | Implemented generic schema | Extend/compose with term, proposal, source class, fixture hash, dedupe key, dependency cluster and explicit exception states |
| Run/job telemetry | Agent Evidence Substrate and Actions observability docs define linkage | Design and existing observers present | Prove run/job/attempt IDs and artifact digest are joined to each proposal and result |
| Result receipt storage | Delphi docs describe signed issue comments and run artifacts; evidence spine describes JSONL | Partially implemented across surfaces | Verify stable artifact name/retention/digest, sanitized receipt availability and cross-run queryability |
| Anonymity/privacy | Delphi docs require anonymous outlier reasons; contributor provenance prohibits raw prompt/context/secrets | Policy intent documented | Define what “anonymous” means, linkability risk, pseudonym rotation, access/retention, redaction tests and public/private projections |
| Exact independent proposal set | Search for exact `DelphicAnonymityMethod` returned no default-branch code result | Not established | Obtain canonical proposal IDs/paths and map each to its own trigger, expected workflow and receipt |
| Per-proposal actual execution | No complete source-to-run-to-receipt chain was established in this audit | Not established | Trigger safe offline runs and capture run IDs/URLs plus validated receipts for each canonical proposal |
| PR #1611 regression | Merged proposal/RFP files, matrix, manifest/items and registry entry exist; experiment matrix says hypotheses only | Available regression fixture; experiment execution not claimed | Test that its proposal changes invoke registry validation and that no experiment is falsely recorded as run |
| Independent human ballots | Debate term explicitly says zero ballots, no consensus, registrar unassigned | Not received/recorded in the cited proposal snapshot | Require eligible ballot receipts before any quorum or consensus claim |
| Paid/cloud safety | RFP explicitly defers account creation/resources/paid invocations; gate panel is rubric-only | Guardrails documented | Keep trigger regression tests local/repo-only; assert zero cloud calls and no secret values in logs/artifacts |

---

## 8. Gaps and risks — prioritized

### P0 — Canonical identity gap

The request refers to “each independent DelphicAnonymityMethod contributor-participation proposal,” but the exact token is not found in default-branch code search and the matching directory listing did not identify a canonical set. Without stable IDs/paths, “each” cannot be verified and path filters cannot be tested exhaustively.

**Required closure:** publish a canonical manifest with one row per independent proposal: `proposal_id`, path, owning term/round, expected workflow, source class(es), required gate(s), receipt location, and current status. Do not merge independent proposal records merely to simplify dispatch.

### P0 — Trigger-to-run correlation gap

Workflow definitions provide event subscriptions and the emitter invokes `gh workflow run`, but a trigger request and a downstream run are separate events. The audit did not establish a complete, per-proposal trace from original event through accepted dispatch, queued run, job completion, receipt validation and result.

**Required closure:** create a correlation ID at intent/dispatch time; carry it through workflow inputs or event payload, run/job summary, and sanitized receipt. Verify against GitHub run IDs and current-head SHA.

### P0 — Intent, participation, execution, and result are conflated easily

Registry validation, an issue label, an intake comment, a dispatched run, a green check, and a valid experiment result are different facts. Current docs already warn against these conflations, but the end-to-end schema and tests must enforce the distinctions.

**Required closure:** explicit lifecycle enum and state-transition tests; forbid transition to `RESULT_COLLECTED` from dispatch-only evidence; forbid `PROMOTED` without its required independent gates/authorization.

### P1 — Schema fragmentation

The Delphi result example includes `term_id`, `source_class`, `source_id`, `run_id`, `fixture_set_hash`, `proposal_commit`, `dependency_cluster`, `response_hash`, and `redaction_status`. The generic evidence envelope has `experiment_id`, `source`, `source_id`, commit/baseline SHA, timestamps, status, outcome, provenance and confidence, but does not require the Delphi term/source class/fixture/dependency/redaction fields. Its status enum also omits some required exception states.

**Required closure:** define a canonical `delphi-result/v1` JSON Schema (or a versioned composition with the generic evidence envelope) and validate both writer and collector against the same schema. Keep compatibility and migrations explicit.

### P1 — Trigger intent mapping is not exhaustive

`proposal-lifecycle.yml` has broad path filters, while `delphi-gate.yml` is mostly issue/event keyed. The signal bridge only maps selected upstream events/workflows. This architecture can be correct if the proposal registry declares the intended trigger per proposal; that declaration-to-workflow mapping was not established for the requested independent set.

**Required closure:** machine-readable intent-to-trigger registry plus test that enumerates every proposal and asserts its required trigger and target workflow. Detect orphan proposals, stale workflow names, unmatched path filters, and trigger loops.

### P1 — Missingness and terminal failure states

The Delphi proposal contract says missing, skipped, timed-out, invalid, rate-limited and failed results must remain explicit. The generic evidence envelope does not express all these states, and absence of a receipt can be mistaken for “no participation” or success if a collector only sees returned records.

**Required closure:** emit explicit expected-but-unobserved/blocked/no-run receipts with query window, last observation time and reason. Do not treat missingness as a negative ballot or as zero-quality evidence.

### P1 — Identity, anonymity and independence need separate dimensions

A GitHub actor is not necessarily the model/provider that produced output. A pseudonym does not by itself guarantee anonymity. Multiple model calls from one family are repeated measures, not independent voters. The debate contract documents these distinctions but the collector must validate them.

**Required closure:** record source class, attribution method, source ID, dependency cluster and privacy tier independently. Public receipts should use approved pseudonymous identifiers; private identity linkage, if needed, should be separately access-controlled. Define retention, pseudonym scope/rotation, re-identification threat model and redaction tests.

### P1 — Re-run and duplicate semantics

Actions reruns may repeat jobs, while dispatches may be retried. The proposal contract’s dedupe key `term_id + source_id + run_id` is useful but does not by itself define whether a new run, a new attempt of the same run, or a changed fixture constitutes a new observation.

**Required closure:** specify event idempotency key, run attempt identity, retry lineage, source/fixture/version identity, supersession rules, and whether repeats count as repeated measures versus independent source participation.

### P2 — Cross-surface queryability and retention

Delphi gate documentation mentions signed issue comments and seven-day artifacts; other evidence surfaces use append-oriented JSONL and hashed receipts. These may be complementary, but a reviewer needs a stable index and must know whether a missing artifact expired, never existed, or was inaccessible.

**Required closure:** retain a durable sanitized receipt/index with immutable IDs and artifact digests; state the retention class and source of truth for each payload. Keep sensitive raw output separate from public evidence.

### P2 — Generated inventory drift

The generated workflow catalog is useful but can be stale relative to YAML or live Actions workflow registrations; the ops inventory notes historically that API registry totals can include phantom entries for deleted workflow files. A catalog row is not runtime proof.

**Required closure:** CI checks that regenerate and diff the catalog, enumerate workflow files, compare active GitHub workflow IDs, and flag deleted/disabled/stale entries without silently dropping them.

---

## 9. Intent mapping model recommended for implementation

Use a registry-driven mapping rather than ad hoc path names:

| Field | Purpose | Validation |
|---|---|---|
| `proposal_id` | Stable independent proposal identity | Unique, immutable or versioned with explicit alias |
| `proposal_path` | Canonical package location | Exists and is registered |
| `proposal_commit` | Exact proposal version under test | 40-hex SHA; matches run head or declared source SHA |
| `term_id` / `round_id` | Decision/participation context | Explicitly frozen before dispatch |
| `intent_type` | review, ballot, provider observation, baseline, validation, promotion gate | Allow-listed enum |
| `source_class` | human/provider/model/baseline/gate/synthesis | Must not collapse across classes |
| `trigger_event` | pull_request, issue, issue_comment, repository_dispatch, workflow_dispatch, workflow_run, push, schedule | Matches workflow event declaration |
| `target_workflow` | Intended Actions workflow path/ID | Exists, enabled, permitted on ref |
| `trigger_correlation_id` | Links intent to dispatch and run | Unique/idempotent |
| `fixture_set_hash` / `rubric_hash` | Locks evaluation input | Same across comparable runs |
| `permission_decision` | Why dispatch is allowed/blocked | Explicit result, no implied authority |
| `expected_receipt` | Receipt type and storage locator | Schema known and testable |
| `required_gates` | Validation/approval conditions | Results tied to same proposal SHA |
| `privacy_tier` | Public sanitized, restricted, or private raw | Redaction/access policy enforced |

The registry is a declaration of intent; it does not itself prove a run. A separate collector must reconcile expected dispatches with actual workflow-run records and receipts.

---

## 10. Recommended validation plan

### Phase A — Static mapping audit

1. Enumerate every canonical independent proposal ID and package path.
2. Parse all workflow `on:` declarations and path filters from YAML.
3. Parse the intent-to-trigger manifest.
4. Assert every proposal has exactly the expected trigger(s) and workflow(s).
5. Assert no stale workflow path, missing manifest entry, duplicate ID, or orphan proposal.
6. Assert no event type can trigger a provider/cloud experiment unless the proposal’s policy explicitly allows it.
7. Run the proposal registry validator and schema tests.

**Pass condition:** deterministic test output enumerates every proposal and its mapped workflow/event with zero unexplained orphans.

### Phase B — Offline trigger contract tests

Use synthetic events and fixtures only; do not call AWS, Bedrock, or any inference provider.

Test at minimum:
- proposal PR changes under each independent proposal path;
- unrelated docs changes do not claim proposal-specific execution;
- missing/malformed proposal ID;
- marker present and absent for Delphi intake;
- duplicate issue/comment/dispatch event;
- unknown repository_dispatch event type;
- valid and invalid signal payloads;
- same event replayed twice;
- changed proposal SHA/fixture hash;
- run queued but cancelled, skipped, failed, timed out, rate limited or not found;
- result with missing source class, dependency cluster, response hash or redaction status;
- duplicate run/attempt and superseding run;
- one human ballot plus model outputs, confirming model outputs cannot satisfy human quorum;
- PR #1611 regression path;
- no credentials and no external provider invocation.

**Pass condition:** each fixture yields the expected lifecycle state and a schema-valid receipt or an explicit, reasoned missingness state.

### Phase C — Safe GitHub Actions runtime proof

1. Use a repository-only branch/PR that changes a designated test fixture/path.
2. Observe the actual Actions run URL, workflow ID, run ID, attempt, head SHA, jobs and conclusions.
3. Verify receipt contains the same immutable SHA and correlation ID.
4. Fetch the receipt/artifact and validate its schema/digest.
5. Repeat a duplicate trigger to prove idempotency and retry lineage.
6. Confirm no provider call, AWS resource, paid invocation, secret value or raw private prompt/completion appears in logs/artifacts.
7. Report the actual run states; do not convert cancelled/skipped/queued/unknown into success.

**Pass condition:** the full trace is independently reconstructible from GitHub event/PR/commit, workflow run/job, and receipt references.

### Phase D — Independent contributor validation

For each registered source:
- verify source class and eligibility;
- verify attribution method and dependency cluster;
- verify frozen term/fixture/rubric;
- validate completed result and redaction;
- deduplicate exact repeats;
- publish sanitized receipt;
- preserve failed/missing/abstained states;
- keep human ballots and model/provider observations in separate aggregation paths.

**Pass condition:** the collector can explain every expected participant as completed, pending, blocked, skipped, failed, invalid, or missing with evidence.

---

## 11. PR #1611 as regression fixture

PR #1611 is a useful fixture because it introduced the AWS Free Tier/Strands Decider Delphi Oracle RFP and associated `RFP.md`, `EXPERIMENT-MATRIX.md`, `DEBATE.md`, `MANIFEST.md`, `ITEMS.md`, and registry entry.

Use it to test **proposal lifecycle telemetry**:
- the PR/merge event is tied to exact base/head/merge commit SHAs;
- proposal-lifecycle validation is observable on the relevant proposal changes;
- manifest/items and registry metadata can be reconciled;
- the experiment matrix remains explicitly “hypotheses only” unless separate execution receipts prove runs occurred;
- the debate term’s zero-ballot/no-consensus state remains zero until valid independent ballot receipts are recorded;
- AWS account/resource/paid invocation authorization remains false unless a separate explicit gate changes it.

Do **not** use PR #1611 as evidence that a provider/model panel ran. The RFP/experiment matrix says no experiment has run; PR merge and green CI do not override that statement.

---

## 12. Privacy, anonymity and attribution guardrails

1. **Anonymity is a property to assess, not a field to assume.** A pseudonymous reviewer/source ID may still be linkable through timestamps, public PRs, repeated behavior, provider metadata or small cohort size.
2. Keep public provenance sufficient to reproduce the result while limiting identity disclosure. Separate restricted identity linkage from public sanitized receipts.
3. Never store secret values, tokens, cookies, raw private prompts/completions, browser profiles, or raw session context in Git, public issue comments, or artifacts.
4. Keep GitHub actor, triggering actor, code author, model/provider source, and human ballot identity as separate concepts.
5. Preserve the attribution method and uncertainty. If provider/model identity or model version is unknown, record unknown/null rather than infer it from an API key, account, comment, commit or workflow actor.
6. Preserve dissent, abstention, incomplete ballots, conflicts and nonresponse. Do not silently omit them from the denominator.
7. Redaction failure is a blocking result state, not a warning to ignore.
8. Do not publish a raw response merely because a hash exists. Hashes provide integrity correlation, not confidentiality.

---

## 13. Operational dashboard and query requirements

A useful telemetry view should allow filtering by proposal, term/round, source class, trigger type, workflow, commit SHA, run state, result state and time window. At minimum, show:

- proposals registered / mapped / orphaned;
- expected trigger count versus observed dispatch count;
- accepted dispatches versus actual workflow runs;
- runs by status and conclusion;
- jobs/attempts and cancellation/retry counts;
- results collected / schema-valid / redaction-valid / deduplicated;
- source-class coverage and dependency clusters;
- independent human ballots invited / received / abstained / incomplete (separate from model/provider runs);
- expected participants with no run/receipt and the last reasoned state;
- experiment results by fixture/rubric version;
- gate decisions and promotion authorizations with exact SHA;
- receipt/artifact availability and retention status.

Use explicit unknown/missing values rather than zeros. A dashboard row with no receipt must expose whether no trigger was expected, the trigger was blocked, the API was unavailable, the artifact expired, or the collector has not observed it.

---

## 14. Acceptance criteria for closing this audit

The audit can be marked **validated** only when all of the following are evidenced:

- [ ] Canonical manifest names every independent DelphicAnonymityMethod contributor-participation proposal by stable ID/path.
- [ ] Every proposal maps to explicit intent type, trigger event, target workflow, permission policy, required gates and expected receipt.
- [ ] Static tests enumerate all proposals and verify trigger/path-filter coverage without collapsing independent identities.
- [ ] A versioned, schema-validated Delphi result/participation receipt is implemented and consumed by the collector.
- [ ] Run/attempt/job IDs, proposal SHA, term/fixture hash and correlation ID survive from dispatch to receipt.
- [ ] Missing, blocked, queued, skipped, cancelled, timed-out, rate-limited, invalid, failed and superseded states are explicit and test-covered.
- [ ] Duplicate delivery and rerun semantics are deterministic and do not inflate independent participation.
- [ ] Human ballots, provider/model observations, deterministic baselines, CI gates and driver synthesis remain separate.
- [ ] Privacy/redaction and dependency-cluster checks are enforced by tests.
- [ ] PR #1611 regression proves lifecycle/telemetry behavior without inventing experiment execution or consensus.
- [ ] A safe repo-only Actions run provides a verifiable run URL/ID, job conclusions, immutable head SHA and valid receipt.
- [ ] Evidence proves no AWS resources or paid inference calls were made by the trigger test.
- [ ] Current workflow catalog and live workflow IDs have been reconciled; stale/deleted/disabled workflows are visible.
- [ ] Independent reviewer accepts the evidence and the operator authorizes any promotion separately.

---

## 15. Final RECON conclusion

The repository already has a substantial foundation: proposal registry validation; issue-based Delphi intake and gate; event dispatch; quota-aware/idempotent processing; a selected workflow signal bridge; signed issue-comment decision ledgers; ForeSight/HindSight/3L0 evidence integrations; generic evidence schemas; and cross-workflow observability guidance.

The missing proof is **not simply “does a YAML trigger exist?”** The decisive question is whether each independent proposal’s intent is mapped to the correct event/workflow and whether its expected participation produces a traceable, validated, privacy-safe result receipt tied to the exact proposal/term/fixture and actual Actions run.

Until the canonical independent proposal set is identified and the dispatch → run → result → receipt chain is demonstrated for each one, report the state as **partially implemented; per-proposal execution/participation coverage not established**. Do not claim all proposals were triggered, all contributors participated, any independent ballots were received, a consensus exists, or experiments ran based on registry CI or PR #1611 alone.
