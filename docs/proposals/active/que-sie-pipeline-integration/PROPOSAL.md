# QUE SIE — Research → RFP → Delphi → DoE → Implementation Claim

**Status:** proposal in review · **Priority:** P0 · **QUE filing:** #5389  
**Related:** qdesk-self-repair · QUE #5283/#5286 · migration #5113 · Siglary #5116 · QDesk RFP #5145 · package digest #5156

## DO

Connect existing queue, watchdog, self-repair, research, proposal-generation, adjudication, experiment and execution systems into one observable lifecycle. Preserve every domain's current authority and source of truth.

OBSERVE → TRIAGE → RESEARCH → RFP → DELPHI → DESIGN → CLAIM → IMPLEMENT → VERIFY → PROMOTE → LEARN

## 1. Current foundation

| Existing component | Current role | Integration |
|---|---|---|
| QUE task rank #5283 | Wall/tier/age/state score and claim-order proposal | Supplies rank and reason components |
| QUE auto-claim #5286 | Typed claims, lease, reclaim and stall closure | Supplies claim receipt and placement result |
| Dispatch watchdog | Aging, tier escalation and heartbeat observation | Supplies queue and stall events |
| QDesk self-repair | Failure intake, candidate PR promotion and role weights | Becomes the SIE orchestrator |
| Oracle Method | Research-backed proposal generation | Produces versioned research/RFP packages |
| Delphi | Independent ballots, signed award and outcome ledger | Adjudicates package and authorizes design entry |
| DoE family | Pre-registered design, treatment identity and EXPERIMENT records | Evaluates candidate arms |
| ATES | Outcome evaluation and metric reduction | Supplies deterministic outcome metrics; independent verification remains a separate authority |
| SWE reference adapter | Optional mini-SWE benchmark context | Manual, one-instance reference run; repository development performance remains primary and benchmark resolution remains unconfirmed until a reviewed scorer exists |
| DSPy DoE lane | Prompt/optimizer experiment design | Consideration/design lane; runtime extraction remains future work and optimizer artifacts stay outside production weights until gated |
| Lean Batteries | Pinned Lean library and pre-proofing research substrate | Experimental research dependency; pin toolchain/revision, compile locally and retain provenance before promotion |
| CEEL / ForeSight | Capability discovery and research evidence | Supplies opportunity and source lineage |
| Observatory / Desk | Existing feeds and dashboard projections | Shows lifecycle and performance |

Current code already includes scripts/que/self_repair.py, .github/workflows/qdesk-self-repair.yml, scripts/dispatch/dispatch_watchdog.py, scripts/dispatch/auto_claim.py, scripts/que/task_ranking.py and ops/que/feeds/stall-gap-feed.json. This proposal completes their stage handoffs; it introduces no second scheduler, queue, RFP ledger, experiment ledger or dashboard database.

## 2. Lifecycle contract

Every stage emits a versioned receipt using docs/schemas/que-sie-stage-v1.schema.json. The initial deterministic validator lives at scripts/que/sie_pipeline.py.

| Stage | Entry signal | Output | Owner |
|---|---|---|---|
| OBSERVE | workflow failure, regression, queue stall, lease event, stale feed, Desk filing, CEEL opportunity | idempotent source event and receipt | source producer |
| TRIAGE | observation accepted | failure class, blast radius, owner room, rank, duplicate/supersession links | QUE |
| RESEARCH | triage admitted | diagnosis, logs, history, prior fixes, baseline, source evidence, unknowns | Research / CEEL |
| RFP | research packet ready | versioned brief, acceptance criteria, replay recipe, risk/cost envelope, package manifest | Oracle Method |
| DELPHI | complete RFP package | independent ballots, signed award and package digest | Delphi |
| DESIGN | award verified | pre-registered factors, levels, cohort, baseline, assignment, sample and stop rules | DoE |
| CLAIM | design and authorization ready | rank-ordered typed claim, claimant, lease, queue receipt | QUE |
| IMPLEMENT | claim acquired | isolated candidate branches/PRs and run artifacts | Swarm |
| VERIFY | candidate implementation ready | independent replay, task outcome, regression, cost and dual-gate receipts | ATES / independent verifier |
| PROMOTE | verification complete | exact-SHA promotion disposition | FA-ADE / existing gate |
| LEARN | outcome terminal | append-only result, failure-class and role-weight delta | SIE / DoE |

The state model keeps execution state, task outcome, promotion state and stage state distinct. A claim resolves a queue stall; it does not resolve the task. A workflow completion records execution; the evaluator establishes task outcome.

## 3. Trigger matrix

| Trigger | Source | Signal | Initial route |
|---|---|---|---|
| Workflow failure | GitHub Actions workflow_run/checks | run ID, attempt, job, step, SHA, conclusion, fingerprint | SIE intake |
| Queue delay | QUE queue feed | p50/p90/p95 wait, oldest age, tier depth, claim latency | QUE triage |
| Stall / lease | dispatch-state + stall-gap feed | stall class, breach, placement failure, lease expiry/release | QUE + SIE |
| Feed freshness | producer commit/feed timestamps | expected cadence, age, parity, schema result | owning feed room |
| Desk filing | project-task/QDesk | requested outcome, owner, claim class, acceptance | QUE |
| Research opportunity | CEEL / ForeSight | candidate identity, source URL/revision, capability and evidence | research intake |

Reuse existing cadence and event producers. Add event adapters to existing workflows. Keep the current QDesk self-repair schedule as bounded reconciliation; queue watchdog remains the short-cycle stall monitor. Use a final sweep after bursts to capture events arriving during an active run.

## 4. Research and RFP generation

Research packet fields:

- trigger and idempotency identity;
- exact repository, ref, SHA, workflow/run/attempt/job/step or feed event;
- concise failure fingerprint and raw-source links;
- related files, commits, PRs, issues and prior repair attempts;
- baseline queue, reliability, cost and quality metrics;
- confirmed facts, hypotheses, unknowns and missing evidence;
- owner room, dependencies, risk class and allowed execution scope;
- reproduction/replay recipe and acceptance tests.

The packet builder is `scripts/que/sie_research_packet.py`; its contract is `docs/schemas/que-sie-research-packet-v1.schema.json`. It validates the source SIE receipt, checks evidence-item hashes and per-item freshness, preserves the baseline/history/replay/risk envelope, and separates supported facts from stale or missing claims. Its output includes a deterministic package digest, a structured Oracle Method brief and fresh-only evidence sets.

Feed that brief and evidence sets to the existing deterministic `scripts/delphi/generate_proposal.py` generator. The generator emits MANIFEST.md, ITEMS.md, RFP.md and PROVENANCE.json; it makes zero external calls and records zero human ballots. The package manifest binds the generated documents and source evidence hashes. The shared Delphi #5156 verifier is implemented, but award-time binding in the live Delphi gate and authenticated consumer-time verification in the live QDesk work-packet path remain pending. Content drift must return the RFP to review and hold consumer authorization.

## 5. DoE and implementation

Each candidate patch is a treatment with frozen task, base SHA, evaluator, dataset/cohort, tool manifest, configured-instance key, provider/model version, prompt hash, runtime and cost envelope.

Candidate families include:

- queue policy: priority, wall proximity, specialist fit, least-loaded, parallel fan-out and staged escalation;
- recovery: retry, repair, quarantine, alternate provider and rollback;
- research: source selection, retrieval depth, diagnosis method and RFP generation;
- implementation: repository-native contracts and performance tasks; optional manual mini-SWE reference runs (one instance/one worker); DSPy prompt/optimizer designs as candidate DoE treatments; Lean/Batteries pre-proofing experiments against the pinned revision/toolchain.

Treat SWE reference results as context rather than repository-level proof; treat DSPy as design-only until its runtime lane lands; treat Batteries results as research evidence until a pinned Lean compile verifies the candidate. Require N ≥ 2 candidate arms where the task supports meaningful comparison. Use randomization or blocking where feasible. Record one EXPERIMENT record per dispatched run. Keep repeated measures distinct from independent task replication. Independent evaluators retain failed arms and report uncertainty.

## 6. QUE routing and formal planning

QUE owns admission, rank, claim class, lease, reclaim and queue state. Routing consumes:

- rank and component reasons;
- dependency readiness from the canonical Kahn/dependency-phase engines;
- claim class and seat capacity;
- provider capability, fresh quota and availability;
- risk class, cost envelope and required verifier independence.

Keep admission priority, wall urgency, queue age, claim state, lease state, execution state, task outcome and promotion state as separate dimensions.

**PDDL ⊂ Siglary.** PDDL is the formal-planning subdomain. Siglary governs the notation system; the PDDL register supplies typed objects, predicates, actions, preconditions, effects and goals. New chords and terminology remain under Linguist/Matrice custody. Planner output is advisory until a named planner validates the domain/problem pair and QUE authorizes the claim.

Use HTN for hierarchical decomposition, CP-SAT/MILP for bounded resource scheduling, BPMN for human/process interchange and Mermaid for visual projections. Each adapter carries a version and source digest.

## 7. Performance and DoE

Primary outcomes:
- verified task correctness and acceptance;
- integration success and regression;
- queue wait and time-to-claim;
- time-to-first-useful-result and MTTR;
- escalation and lease-reclaim rates;
- retry, duplicate-work and conflict rates;
- latency, token/credit cost and resource use;
- human intervention and attribution confidence;
- maintenance burden and security findings.

Report distributions, confidence/credible intervals where appropriate, missingness, sample size, assignment integrity and cost-normalized outcomes. Small samples remain descriptive. Promotion requires a held-out or repeated confirmation appropriate to the design.

## 8. Governance and authority

- QUE admission and governor thresholds remain Cadence-owned.
- Delphi reviewers, builders and verifiers remain distinct.
- The candidate-generation loop never adjudicates its own output.
- Paid spend, credentials, destructive history operations, protected production actions and external-repository writes follow existing human-only permissions.
- Routine authorized repository work follows FA-ADE and dual-gate policy.
- PDDL plans, MiroFish scenarios and model judgments remain hypotheses until independently verified.
- Data records use schema nulls for unknown values; chat-only epistemic shorthand stays out of feeds and ledgers.
- Siglary A2A uses operators and plain words per the current token-cost evidence; display-register chords/glyphs remain human-facing unless Linguist rules otherwise.

## 9. Acceptance and delivery

QSI-001–QSI-010 in ITEMS.md define the delivery contract. Initial implementation adds the stage receipt schema, deterministic idempotency keys, forward-only transition validator, regression tests, and validation in the existing QDesk self-repair workflow.

Subsequent slices wire live triggers, Oracle Method/Delphi package binding, DoE design, QUE claim/lease transitions, evaluation adapters and Observatory projections. Each slice lands with a receipt and current-SHA gate evidence.

## 10. Promotion rule

Promotion requires the existing repository dual gates on the same immutable SHA, independent review/verifier evidence, accepted task outcome, package/provenance integrity, and the applicable owner authorization. QUE rank or claim, Delphi award, PDDL plan, workflow success and dashboard status each retain their own meaning.
