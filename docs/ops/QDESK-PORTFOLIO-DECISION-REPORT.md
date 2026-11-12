# QDesk Portfolio Decision & Delivery Report Contract

**Status:** proposal / design contract  
**Related:** #5196, #5145, #5155, #4979, #5151, #5152, #5176, #5136, #5183, #5189, #5192, #5193  
**Authority:** QDesk owns admission and portfolio decision records; QUE owns queue/dispatch state; DoE owns experimental design and outcome evaluation. This document defines a report projection over those authorities. It creates no new scheduler, registry, ledger, queue, identity plane, or execution authority.

## 1. Purpose

The report answers, from source-backed evidence:

1. What is QDesk deciding and what is in flight?
2. Which workstreams are at which lifecycle stage, and what evidence proves each transition?
3. How does work traverse admission, queue, claim, dispatch, execution, verification, and integration?
4. Are new proposals compared with incumbent work for marginal and compounding portfolio benefit?
5. What does DoE know about execution quality and decision quality, and what remains unknown?
6. Which role context is responsible for each task class, with what authority and independent review?

The report is a decision-support projection, not a new control plane. It cannot dispatch, authorize, promote, merge, deploy, provision participants, or spend provider quota.

## 2. Authority and source precedence

| Concern | Authority of record | Report behavior |
|---|---|---|
| Proposal intake / admission verdict | Existing QDesk / swarm-admission issue stamps and workflow | Read decision and evidence; never infer from a queue label alone |
| Queue and dispatch state | QUE producer feeds, dispatch state feed, event snapshots, claim receipts | Preserve source timestamp, source SHA, and freshness |
| Opportunity priority | Existing opportunity-cycle receipts and opportunity-priority feed | Explain score basis and timebox; do not treat it as a complete portfolio optimizer |
| Capacity and quota | Existing quota registry / Cadence ledger | Capacity is a feasibility constraint, not model/task quality |
| DoE design and outcome | DoE family, Questions Matrix, experiment records, evidence substrate | Preserve strata, configured-instance identity, outcome stage, and provenance |
| Participant / role identity | Existing identity and role registries and their issuance evidence | Keep participant, role, provider, and configured-instance identities distinct |
| Implementation acceptance | Repository checks, independent review, merge/deploy evidence | Docs, labels, and successful HTTP transport are not acceptance evidence |

The report must cite direct source paths, issue/PR/run URLs, source ref, and blob or commit SHA. If sources disagree, publish the conflict and its resolution state; do not silently choose one.

## 3. Lifecycle vocabulary

Use these states as separate facts, not a single overloaded status:

- **proposed** — submitted but not admitted.
- **admitted** — explicit positive admission verdict exists.
- **queued** — dispatch or queue record exists; no producer claim is implied.
- **claimed** — a valid producer claim / mutex exists.
- **executing** — a concrete workflow or execution run has started.
- **blocked** — a named prerequisite or policy condition prevents progress.
- **deferred** — admission or dispatch decision explicitly postpones work.
- **completed** — execution terminated; correctness is not implied.
- **verified** — acceptance evidence and independent validation are present.
- **merged / deployed / adopted** — separate integration and operational lifecycle facts.
- **measured** — a defined outcome observation exists with provenance.
- **superseded** — a newer canonical work item replaces this one.
- **unverified** — a claim or transition lacks sufficient evidence.

A report may show multiple lifecycle facts concurrently (for example, admitted=true and claimed=false). Never derive claimed or executing from admitted/queued labels. A failed, cancelled, skipped, timed-out, or never-invoked run must retain its actual state.

## 4. Admission and traversal model

Represent the path as explicit evidence-bearing transitions:

`proposal → classification → dependency ordering → opportunity/timebox → merit/readiness → capacity gate → admission verdict → queue → claim → dispatch → execution → verification → integration → outcome measurement`

For each transition record: input references, decision owner, decision time, output state, policy/contract version, source SHA, and reason. The sequence is explanatory; the implementation's actual ordering must be re-fetched and reconciled before a report claims exact behavior.

### Hard gates versus ranking signals

Hard gates include authorization, security/safety policy, license/provenance constraints, required prerequisites, and capacity feasibility. A score cannot override them.

Ranking signals include expected direct value, cross-lane reuse, dependency unlock, time sensitivity, risk reduction, cost reduction, evidence confidence, and opportunity cost. Report the component values and evidence, not only a composite.

Capacity/quota is a constraint and must not be misrepresented as quality. Missing evidence is null / unknown, never zero. A score is not an admission verdict.

### Queue fairness and liveness

Report queue depth and age by tier, lane, and lifecycle state. Include:
- feed generation time, age, watermark, and freshness threshold;
- collector run and outcome;
- pagination coverage, fallback use, rate-limit/error class, and partial-picture behavior;
- tier thresholds and exemptions;
- dependency chain and parallelism constraints;
- claim identity, claim age, heartbeat, watchdog threshold, and escalation receipt;
- deferred/admitted aging and starvation indicators;
- counts excluded as stale/wedged, with their separate listing.

The canonical QUE producer feed remains the queue projection. Do not add a second collector or queue ledger. When the feed is stale or incomplete, report the affected coverage as unknown and name the fallback/error. T1/T2 protections and T3/T4 queue-relief rules must be read from the current canonical dispatch-tier policy, not copied as permanent assumptions.

## 5. Compound-benefit portfolio model

### Decision unit

Rank a candidate against the **current feasible portfolio**, not against an empty baseline. The unit is an initiative or dependency-linked work package when benefits accrue across multiple issues. Individual issues remain execution units; they are not necessarily independent value units.

### Evidence-bearing dimensions

Each candidate should expose, where evidenced:

- direct user/project benefit;
- reuse breadth and number/type of downstream consumers;
- dependency unlocks and critical-path acceleration;
- recurring cost, quota, maintenance, and operational toil reduction;
- reliability, security, and failure-risk reduction;
- research value and improvement to future decision quality;
- time sensitivity and opportunity decay;
- implementation, integration, and maintenance effort;
- capacity feasibility and dependency readiness;
- evidence confidence, reversibility, and uncertainty;
- expected compounding horizon;
- displaced incumbent value and switching cost.

A conceptual marginal portfolio value is:

`ΔV(candidate | portfolio) = V(portfolio ∪ candidate) − V(portfolio)`

A practical score may be used only when each component has a defined scale, weight, provenance, and calibration history. It must not hide hard-gate outcomes or missing data. Publish component values and sensitivity ranges. If weights or evidence are not calibrated, report a structured comparison and mark composite score NOT_ESTABLISHED.

### Incumbent preservation and refresh

A candidate does not displace an incumbent solely because one point estimate is higher. Require:
1. same decision horizon and comparable evidence;
2. explicit opportunity cost and dependency impact;
3. sensitivity analysis / uncertainty interval;
4. a recorded decision reason and displaced-work reference;
5. a re-evaluation trigger (new evidence, changed dependency, capacity, timebox, or material scope change).

Preserve the incumbent when evidence is insufficient or candidate improvement is within uncertainty. Record overrides with actor, rationale, and review.

## 6. DoE and QDesk decision-quality evaluation

Use the existing DoE Questions Matrix (40 dimensions / six clusters) and Agent Evidence Substrate as canonical methodology. Do not invent a competing experimental schema.

Required strata:
- subject: provider, model@version, configured instance, manager/policy, team, selection path, arm history;
- task: family, instance, complexity, novelty, scope stability, stakes;
- treatment: prompt, tools, context budget/composition, sequence, concurrency, decoding, recovery;
- environment: dispatch route, quota/capacity, time window, substrate, dependency state;
- measurement: outcome stage, oracle, validation independence, corroboration, stratum, accumulation, provenance;
- adaptation: generation/cohort, variation, selection pressure, culling, retry, policy update.

Configured-instance identity is not model identity. Preserve the instance key or full tuple of prompt/tool references and hashes, role, moniker, and context. Do not pool unlike strata without an explicit pooling rule.

### Outcome chain

`execution status → task outcome → correctness → integration → regression → resource cost`

No invocation is not a model failure. HTTP success is not task success. Build completion is not accepted implementation. Missing or unverified outcomes remain missing.

### Experimental discipline

Record treatment definition, task cohort, baseline, randomization/blocking, repetition count, provider rotation, environment, run IDs, acceptance oracle, independent verifier, and attribution confidence. Preserve failed and negative observations. Do not select a manager from a single run. Use no_selection when evidence is insufficient, strata are incomparable, or quality gates fail. Efficiency is secondary to correctness, validation, and integrated outcome.

### QDesk decision-quality measures

Candidate metrics (publish only when denominators exist):
- admission precision/recall and false-admit / false-defer rates;
- admitted-to-claim and claim-to-execution conversion;
- time-to-claim, time-to-first-execution, time-to-verified-outcome;
- admitted-but-unclaimed aging and starvation rate;
- dependency unlock yield and downstream adoption;
- portfolio marginal value delivered versus displaced;
- estimate calibration and uncertainty calibration;
- rework, regression, duplicate-work, and integration yield;
- cost/quota per verified outcome;
- independent-review disagreement and evidence completeness.

Every metric needs a numerator, denominator, cohort definition, observation window, source refs/SHA, coverage, and null semantics. Report censored/incomplete cohorts and prevent survivorship bias. Do not invent baselines or savings.

## 7. Role-context routing

Role selection is a capability/authority contract, not a provider label. Map task needs to existing role definitions for:
- scientific governance and domain research;
- mathematics, statistics, and formal methods;
- DoE design and experiment operation;
- measurement and reproducibility;
- ML research, evaluation, and MLOps;
- validation, scientific red-team, and QA;
- optimization and control systems;
- graph science and complex systems;
- implementation assurance and integration.

For each assigned role record role-contract version, participant identity, authority ceiling, competency evidence, tools/data permissions, required outputs, acceptance tests, independent reviewer, abstention/escalation behavior, and reproducibility/performance measures. A candidate specialist role is not a qualification or assignment. A manager cannot independently verify its own work.

## 8. Report schema and publication

The machine-readable shape is defined in `qdesk-portfolio-report.schema.json`. The report generator should consume current canonical source surfaces and emit:
- one Markdown report for operators;
- one JSON record with source and metric provenance;
- an explicit no-material-change report when nothing changed;
- explicit stale, missing, blocked, partial, and NOT_ESTABLISHED source coverage.

Do not store secrets, raw prompts, private tool payloads, account identifiers, or credential values. Use references and hashes only where the existing policy permits them.

## 9. Phased implementation and gates

| Phase | Scope | Exit evidence |
|---|---|---|
| P0 | Current-master source census, status reconciliation, report contract | Source manifest with SHA/freshness and unresolved conflicts |
| P1 | Existing QUE feed freshness/coverage and admission evidence | Tests for fresh/stale feed, fallback error, partial picture |
| P2 | Admitted→claim→dispatch liveness | Exactly-once claim/fire proof, complete dispatch stamp, watchdog evidence |
| P3 | Lane, participant, role, configured-instance projection | Identity and stage joins with null-preserving tests |
| P4 | Portfolio comparison and incumbent preservation | Reproducible decision record with component evidence and uncertainty |
| P5 | DoE and QDesk outcome capture | Repeated cohort evidence, independent verification, metric denominators |
| P6 | Report generation and review | Deterministic Markdown/JSON, schema tests, self-review receipt, independent review |

Dependencies and current order must be revalidated against #4979, #5151, #5152, #5176, #5136, #5183, #5189, #5192, #5193 and successors. No phase may silently replace an existing owner surface.

## 10. Self-review and release discipline

Before publication, the report author must:
1. re-fetch current master and every cited issue/PR/run;
2. bind claims to exact source ref/SHA and timestamp;
3. distinguish source facts, inference, and unknowns;
4. reconcile conflicting sources and stale feeds;
5. verify each metric's numerator, denominator, cohort, and coverage;
6. verify lifecycle-state distinctions;
7. check no duplicate registry/ledger/collector/scheduler is introduced;
8. remove secrets and sensitive payloads;
9. record unsupported claims as unknown;
10. request independent review.

Self-review is not self-approval. Merge, deployment, production scheduling, participant provisioning, provider routing, and paid inference remain subject to their separate existing authorization and gates.

## Current implementation boundary

This contract is documentation and schema only. It does not assert that the report generator, portfolio optimizer, automatic admission-to-execution conversion, or all role assignments are implemented. Those claims require separate implementation and runtime evidence.
