# Compounding Production Prioritization — system proposal

**Status:** proposed design extension to Pit Crew / DoE oversight  
**Work item:** PCDOE-008  
**Authority:** existing proposal lifecycle, dependency-phase engine, DoE Family, repository dual gates and Agentic Permissions remain authoritative  
**Scope:** operating convention, prioritization policy candidates, DO-statement practice, AutoApprove boundaries and preregistered evaluation design  
**Runtime effect:** none in this design slice; no live dispatch, ranking mutation, provider routing, workflow permission change, merge, release or production policy activation

## Executive decision

Adopt **Compounding Production System** as the name of the operating model, not as a new department, scheduler or control plane. Treat production prioritization as a capability that composes existing intake, proposal, dependency-phase, dispatch, evidence, DoE, ATES / MoneyBall / 3L0 and promotion surfaces.

Use **Production Value Portfolio** as the governance view and **AutoApprove** as a bounded execution policy. Neither becomes a new source of truth:

- The portfolio view reads registered work and current dependency/evidence state; it does not own task state.
- AutoApprove admits only actions already authorized by the existing scope, permissions and phase contract; it does not manufacture a GitHub review, merge approval, release authorization or human consent.
- DoE evaluates prioritization methods independently; it does not dispatch production work or promote a winner.
- The existing dependency-phase engine remains the authority for readiness, claims and lifecycle.
- Existing evidence and scoring contracts remain authoritative; no new experiment ledger, score store, scheduler, queue, router, lease manager or promotion authority is introduced.

The objective is **verified integrated production value compounded over time**, not activity, commit count, raw model throughput, nominally free inference or a single weighted score optimized without calibration.

## 1. Naming and organizational conventions

“Department” is not selected. It implies a permanent org chart, staffing boundary and parallel ownership structure that this repository does not need.

| Convention | What it means | Strength | Risk | Disposition |
|---|---|---|---|---|
| Compounding Production System | End-to-end operating model for selecting, executing, integrating, verifying and learning from work | Describes system behavior without inventing a team | Can be mistaken for a new runtime | **Recommended name**, explicitly an operating model |
| Production Value Portfolio | Read-only portfolio view over existing registered work | Makes trade-offs, dependencies and investment visible | Could become a duplicate backlog if it stores task state | **Recommended governance view**, derived only |
| Compounding Production Operations | Practice for day-to-day execution and improvement | Clear operational language | May sound like a new organization | Optional role/practice name |
| Production Value Office | A small coordination/governance function | Clear accountability for portfolio review | “Office” can recreate the department problem | Not selected unless a real accountable human owner is later named |
| Production Prioritization Council | Deliberation forum for cross-lane trade-offs | Useful for contested P0/P1 choices | Adds meetings and consensus latency | Reserve for genuinely cross-owner decisions |
| Production Value Control Plane | Formal policy/decision component | Precise architecture language | High duplication risk with QUE, phase engine, Pit Wall and existing control plane | Reject as a new component |
| Compounding Production Program | Time-bounded improvement initiative | Good for a finite rollout | Poor fit for a continuous operating capability | Use only for a bounded implementation phase |

**Naming rule:** CPS is the operating model; Production Value Portfolio is its derived view; AutoApprove is a permission/admission policy; DoE is the independent evaluation method. These names describe different concerns and must not be used as synonyms.

## 2. System boundary and composition

The proposed flow composes current repository authorities:

~~~text
Human intent
    ↓
Existing proposal / issue intake
    ↓
DO statement + bounded work item
    ↓
Existing dependency-phase readiness and claims
    ↓
Existing QUE / QDesk admission and approved specialist route
    ↓
Existing execution adapters and Pit Crew roles
    ↓
Integrated artifact
    ↓
Independent correctness / regression / integration verification
    ↓
Existing evidence records + ATES / WTCV / TCV / MoneyBall / 3L0
    ↓
DoE oversight of candidate prioritization policies
    ↓
Portfolio recommendation
    ↓
Existing dual gates + existing promotion authority
    ↓
Measured outcome feeds the next BIUDL cycle
~~~

The portfolio is a **projection**, not a database. It may rank or group references to issues, proposals, phase records and PRs, but the owning source remains authoritative. A generated dashboard or report must show its source revision and observation time.

The system MUST preserve these distinctions:

- proposal priority ≠ dependency readiness;
- readiness ≠ permission to perform every action;
- dispatch ≠ execution;
- execution ≠ correctness;
- correctness ≠ successful integration;
- integration ≠ promotion;
- promotion ≠ measured compounding benefit.

The current P0/P1/P2 vocabulary in the proposal registry remains the coarse priority band. This proposal adds a transparent within-band ranking method; it does not redefine the repository-wide priority taxonomy.

## 3. Compounding value model

A task has compounding value when its verified result creates reusable capability, removes a dependency bottleneck, lowers future cost/risk, improves the evidence system, or enables multiple downstream outcomes.

Evaluate each work item on separate dimensions before ranking:

| Dimension | Operational question | Evidence examples |
|---|---|---|
| Outcome value | What verified user or production outcome changes? | Acceptance evidence, defect prevention, service reliability, user-visible capability |
| Reuse breadth | How many independent future work units can reuse the result? | Consumer references, adoption records, shared adapter/test/template use |
| Dependency unlock | Which blocked or constrained downstream work becomes ready? | Existing dependency DAG and phase evaluation |
| Risk reduction | Which failure modes, security exposures or operational risks are reduced? | Reproductions, threat model, incident evidence, regression coverage |
| Time to value | How soon can the outcome be integrated and verified? | Observed cycle timestamps, not estimates presented as facts |
| Effort / resource cost | What engineering, reviewer, provider, quota and context resources are consumed? | Actual run usage where measured; otherwise null / not established |
| Confidence | How strong and current is the evidence behind the estimate? | Source quality, freshness, independent verification, attribution |
| Reversibility | How cheaply can the change be rolled back or retired? | Change scope, migration effects, rollback evidence |
| Maintenance burden | What recurring cost or new operational surface is introduced? | Ownership, tests, workflows, service and dependency obligations |

**Do not collapse unknown values to zero.** Missing evidence remains null / not established in narrative or schema-supported nulls. Do not convert a low-confidence estimate into a precise return-on-investment claim.

### Priority bands and overrides

- **P0 — protect production:** verified security, correctness, availability, data integrity or critical delivery blockers. The override must cite concrete evidence and an owner.
- **P1 — compound foundations:** reusable capabilities, high-leverage dependency unlocks, durable automation, evidence quality and cross-lane improvements.
- **P2 — valuable improvements:** bounded efficiency, observability, maintainability, documentation and quality improvements.
- **P3 — explore:** optional experiments, speculative ideas and low-confidence opportunities.

These are proposed operating descriptions for the existing priority vocabulary, not a replacement registry schema. A P0 safety override outranks a high numeric score. Within a band, use the evaluated policy. Do not promote an item solely because it is old, easy, popular, cheap or produces many commits.

## 4. Competing prioritization policy versions

The following are **design candidates**, not measured winners. Each has a stable treatment identity for the proposed DoE. The incumbent control is the exact currently observed selection practice captured at experiment freeze; it must not be reconstructed from memory.

### Version A — Leverage Density

**Question:** Which bounded action creates the most verified reusable value per unit of total effort?

Rank using normalized, predeclared measures for expected outcome value, reuse breadth, dependency unlock and evidence confidence, relative to observed effort and resource cost. Apply hard risk and authority gates before ranking.

- Strength: rewards reusable foundations and high-value small changes.
- Weakness: estimates of reuse and effort can be biased; a simple ratio can starve large but necessary infrastructure.
- Guardrail: P0 overrides, effort floor, uncertainty band and explicit dependency criticality.
- Best fit: platform foundations, shared tests, adapters and automation.

### Version B — Critical-Path Unlock

**Question:** Which action most reduces the time or risk on the verified dependency critical path?

Rank by blocker severity, number and importance of dependent work units, critical-path reduction, readiness and the cost of leaving the blocker unresolved. Dependency edges must come from the existing phase engine or cited authoritative records.

- Strength: attacks bottlenecks and unlocks parallel work.
- Weakness: can overvalue central infrastructure and underweight independent user-facing value.
- Guardrail: require verified dependency edges; candidate/heuristic edges do not count as facts.
- Best fit: blocked releases, foundational integration and cross-lane dependencies.

### Version C — Risk-adjusted Expected Value

**Question:** Which action has the strongest evidence-adjusted expected outcome after accounting for downside and execution cost?

Rank with predeclared outcome, probability/confidence, downside severity, time-to-value and total cost dimensions. Preserve distributions and uncertainty; do not present subjective estimates as measured values.

- Strength: makes uncertainty and risk visible.
- Weakness: probability estimates can create false precision and reward conservative under-investment.
- Guardrail: independent rating, calibrated scales, sensitivity analysis and a separate P0 override.
- Best fit: uncertain research, security remediation and investment decisions with asymmetric downside.

### Version D — Pareto Portfolio

**Question:** Which portfolio of work gives the best balanced frontier across outcome, reuse, critical-path unlock, risk, time and cost?

Keep dimensions separate. Identify dominated items and a Pareto frontier; choose a portfolio that preserves critical work and avoids concentrating all capacity in one objective. Apply existing admission and capacity rules after portfolio selection.

- Strength: avoids hiding trade-offs inside one arbitrary weight vector.
- Weakness: a large frontier may be difficult to operationalize; tie-breaking still needs a declared policy.
- Guardrail: transparent tie-breaks, capacity constraints from live sources and diversity checks.
- Best fit: mixed roadmaps and cross-domain portfolios.

### Version E — Hybrid gate + Pareto + leverage tie-break

**Question:** Can a simple, explainable hybrid outperform each single policy without compromising safety or starving necessary work?

1. Apply existing authority, P0 safety and dependency-readiness gates.
2. Identify dominated candidates and the Pareto frontier.
3. Rank frontier candidates using Leverage Density as a tie-break only.
4. Re-evaluate after verified outcomes or material dependency changes.

- Strength: combines safety, balance and operational decisiveness.
- Weakness: more moving parts; must prove it is better than the simpler candidates.
- Guardrail: immutable policy version per run; no mid-run policy changes; explicit tie-break and starvation audit.
- Best fit: candidate successor only after comparative evidence.

**Recommendation:** use Version D as the design reference and Version E as the leading hypothesis, not as a declared winner. Retain A, B and C as real competing treatments. The DoE may reject the hybrid or show that a simpler policy is superior.

## 5. AutoApprove — bounded authority policy

AutoApprove means **automatic admission of a pre-authorized action inside a verified scope**. It does not mean an agent can grant itself authority, create a formal review approval, bypass branch protection or approve its own work.

| Class | Examples | AutoApprove posture |
|---|---|---|
| Read-only | Fetch current state, inspect diffs/checks, compare evidence, produce reports | ALLOW within connected read scope |
| Reversible low-risk | Documentation, tests and isolated branch changes explicitly covered by an accepted work item | ALLOW only when scope, owner, branch and acceptance evidence are explicit |
| Workflow / permission surface | Changes under .github/workflows/**, app permissions, branch protection, repository settings | Require the repository's designated authority and tool permission; never infer from broad user wording |
| External side effect | Send messages, create third-party resources, publish external content, consume paid quota | Require the specific existing authorization and budget; record the effect |
| Production / irreversible | Merge where policy requires explicit authorization, deployment, destructive changes, history rewrite, credential rotation, data deletion | BLOCK pending the applicable human-only or explicit approval boundary |
| Formal review | GitHub APPROVE review, required independent reviewer decision | Never self-approve; only a valid independent reviewer may submit it |

AutoApprove MUST be evaluated against the exact action, not the task title. It MUST re-fetch current state immediately before a consequential write, verify the applicable proposal/phase authorization, check path and write ownership, and record a receipt. If authority, scope, owner, budget or evidence is ambiguous, it returns approval-required or blocked.

**Auto-promote is separate:** the repository's existing policy may promote a candidate only when the named dual gates pass on the exact candidate SHA, the task outcome is verified, mergeability and required review conditions are satisfied, and no higher-level permission boundary blocks the action. A green check alone is insufficient. This proposal does not change that policy.

## 6. DO statements — action-first work contracts

Use the existing DO Phrasing and Framing Framework. A DO statement is a concise work instruction, not a new lifecycle schema or a second task database.

Canonical form:

> **DO** [action] [target] ⇒ [observable outcome]. Scope: [bounded paths / issue / phase / cohort]. Preserve: [invariants]. Do not: [prohibited actions]. Accept when: [tests / independent evidence / exact state]. Record: [receipt references]. Stop when: [named stop or escalation condition].

A substantial DO statement MUST specify the fields that materially affect safe execution. Unknowns remain unknown. The statement should map to an existing proposal ITEM, issue or dependency phase; it must not create a competing source of lifecycle state.

### Reusable DO statements

**Portfolio recon**

> DO re-fetch the registered proposal, issue, PR and dependency-phase state for the named portfolio ⇒ produce a source-linked ranking candidate. Scope: the named work items and their verified dependency edges. Preserve: P0 safety overrides, ownership and existing priority bands. Do not: infer missing evidence, rewrite source records or dispatch work. Accept when: every ranked item has a current source reference, confidence and stated unknowns. Record: observation time, source refs and baseline SHA. Stop when: the source is stale, ambiguous or outside the read scope.

**Prioritization policy evaluation**

> DO score the frozen matched cohort with each preregistered policy ⇒ produce blinded rankings and outcome measures. Scope: the declared cohort and immutable policy versions. Preserve: identical item facts, authority gates and task definitions across arms. Do not: tune weights after seeing treatment results or silently exclude failures. Accept when: all eligible cases have preserved dispositions, missingness is reported, and independent evaluators complete the declared rubric. Record: experiment, arm, run, SHA and evidence refs. Stop when: assignment integrity fails or the cohort cannot support the declared comparison.

**Bounded implementation**

> DO implement the accepted work item on an isolated branch ⇒ deliver the smallest integrated change that satisfies its acceptance contract. Scope: named files and dependencies only. Preserve: canonical source ownership, tests, secrets and authority boundaries. Do not: merge, deploy, rotate credentials or widen scope. Accept when: focused tests, repository gates and exact-SHA evidence pass. Record: commit, PR, run and artifact receipts. Stop when: ownership conflicts, an approval boundary is reached or validation fails.

**Adaptive continuation**

> DO re-fetch current state ⇒ choose the highest-value non-conflicting authorized action, execute one bounded increment, validate it, record the result and repeat while measurable progress remains. Preserve: all prior observations and immutable attempt identity. Do not: treat queued/running as success or retry a failure without diagnosis. Accept when: the outcome is verified or a named terminal state is reached. Stop on: success, clean no-op, blocked, approval-required, exhausted or stagnated.

### Siglary conformance

For machine-facing dispatch and status, use the repository's Siglary A2A skill and its existing classes: OPERATORS plus plain words in the machine register; do not invent CHORDS or GLYPHS. The existing dispatch stamp is:

~~~text
dispatch {from}→{to} · {task} · gate: {scope} · receipt {refs} · ∆ ask: {ask}
~~~

State claims carry an adjacent receipt. Use ∆ with a magnitude for a quantitative change. The not-established marker is chat-only; structured records use schema-supported nulls. If a compressed form can be misread, expand it. Accuracy > compression.

Example status shape (replace placeholders only with actual receipts):

~~~text
{live|degraded|down|blocked} {task} · verified receipt {PR/SHA/run} · owner action: {act ∨ none}
~~~

Do not label a planned action live, a queued workflow success, or a recommendation approved.

## 7. DoE preregistration — priority policy comparison

**Campaign identity:** compounding-priority-policy-001  
**State:** design-only / proposed / not admitted to the DoE Family  
**Control:** incumbent selection practice, frozen and documented before assignment  
**Treatments:** Version A, B, C, D and E  
**Execution:** offline historical replay / blinded evaluation first; no live dispatch or production reordering in this design slice

The design record is paired with experiments/doe/compounding-priority-policy-001/DESIGN.json. It is not an EXPERIMENT run record. The DoE Family intake rule still requires a committed design record **and** actual run evidence before the campaign is represented as an admitted family member.

### Hypothesis

At least one explicit compounding-priority policy will improve independently assessed priority quality and downstream verified value relative to the frozen incumbent, without increasing critical-risk misses, starvation, unauthorized actions, integration defects or total effort.

The hybrid is a candidate hypothesis, not the presumed winner. The null outcome is valid: no candidate is demonstrably better, or evidence is insufficient.

### Units, cohort and assignment

- Unit: one frozen, historically grounded work item with enough evidence to evaluate its priority at the decision time.
- Cohort: matched items sampled from task families represented in the available repository evidence. Exact cohort size is not established until the historical evidence census and power analysis are complete.
- Blocks: task family, priority band, evidence completeness and relevant time window.
- Assignment: randomized policy ordering per item; each eligible item is scored by every arm under identical frozen facts.
- Blinding: opaque policy IDs and item IDs for independent evaluators where feasible; provenance remains protected and is unblinded only after evaluation.
- Replication: repeated scoring/evaluation by independent raters and a later holdout cohort. Rater disagreement is preserved and reported.
- Incumbent: reconstruct only from actual dated decisions; if not reconstructable, mark control unavailable rather than inventing a baseline.

### Outcomes

**Primary:** blinded independent assessment of priority-order quality against the declared rubric, with agreement and uncertainty reported.

**Secondary:**
- verified outcome value per total effort;
- downstream dependency unlocks attributable to selected work;
- time from selection to integrated verified outcome;
- first-pass acceptance and rework;
- critical-risk misses and false P0 overrides;
- starvation / age distribution across work classes;
- conflict, duplicate work and human intervention;
- cost and usage only where measured, with null for unavailable values;
- sensitivity of rankings to plausible weight and confidence changes.

**Hard guardrails:** zero authority bypass; zero self-approval; no missing P0 safety work; no silent exclusion of failed/censored items; no data loss; no unreviewed production dispatch; no treatment mutation after assignment.

### Analysis and decision rules

1. Validate cohort completeness, provenance and assignment integrity before looking at outcomes.
2. Report per-arm distributions, effect sizes, uncertainty, missingness and task-family interactions; do not report a single-run winner.
3. Compare the incumbent and each candidate on the same matched cohort.
4. Separate screening from confirmation. A promising arm must be replicated on a fresh holdout before recommendation.
5. Run sensitivity analysis on weights, confidence and missing-data treatment.
6. Retain failures, unavailable arms, censored cases and inconclusive outcomes.
7. Recommend reject, inconclusive, confirm or candidate-for-review; DoE does not promote.
8. A policy becomes eligible for production consideration only through the existing proposal, phase, review, dual-gate and promotion authorities.

### Stop conditions

Stop or defer the campaign if the incumbent cannot be reconstructed, cohort facts are not frozen, assignment is compromised, independent evaluation is unavailable, the power/precision target cannot be justified, or any arm requires an unauthorized side effect. A lack of statistical power is inconclusive, not a pass.

## 8. Implementation sequence

| Increment | Deliverable | Exit evidence |
|---|---|---|
| 0 — register | PCDOE-008 in the existing proposal work ledger | Current branch and item receipt |
| 1 — specify | This proposal and design-only preregistration | Link/contract consistency |
| 2 — inventory | Frozen cohort candidate inventory with explicit dispositions | Evidence completeness and unknowns |
| 3 — calibrate | Rubric, raters, power/precision and analysis plan | Agreement and feasibility evidence |
| 4 — screen | Offline matched comparison of incumbent and A–E | Valid assignment and preserved run receipts |
| 5 — confirm | Replication on fresh holdout | Reproducible effect and uncertainty |
| 6 — recommend | Independent DoE report | Explicit retain/revise/reject recommendation |
| 7 — consider | Existing proposal/phase/promotion process | Exact-SHA dual gates and applicable approvals |

Concurrent work is permitted only across non-conflicting documentation, cohort inventory and analysis preparation. Do not run the same item through competing writers or mutate production ranking while the experiment is design-only.

## 9. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Duplicate control plane | Compose existing proposal, phase, QUE, Pit Crew, DoE and evidence owners |
| False precision | Calibrate scales; show uncertainty; keep unknowns null |
| Popularity or cheapness dominates value | Rank verified outcomes and integration above raw activity or nominal price |
| P0 safety work is crowded out | Hard override before all candidate scores |
| Critical-path policy over-centralizes | Compare against Pareto and leverage policies |
| Portfolio view becomes a second backlog | Derived projection only; link to canonical records |
| AutoApprove becomes permission escalation | Exact action/scope checks; deny ambiguous or protected operations |
| DoE becomes a rubber stamp | Independent evaluator, frozen cohort, holdout, preserved null/failure |
| Agent attribution is wrong | Preserve provider, model, role, adapter, workflow and provenance dimensions independently |
| More metrics create more work than value | Measure collection cost and remove metrics that do not change decisions |

## 10. Decision requested from the proposal process

The design recommendation is:

1. Adopt Compounding Production System as the operating-model name.
2. Use Production Value Portfolio as a derived governance view.
3. Define AutoApprove as bounded pre-authorized admission, not formal review approval.
4. Carry the four explicit candidate policies plus the hybrid into DoE screening against a frozen incumbent.
5. Keep this work design-only until cohort, rubric, authority and evaluation readiness are evidenced.
6. Preserve existing DoE, phase, evidence, scoring, dual-gate and promotion authorities.

This proposal does not claim the policy has been implemented in runtime, that an experiment has run, that a candidate has won, or that production prioritization has changed.

## Receipts and source contracts

- Pit Crew proposal and work ledger: docs/proposals/active/pit-crew-doe-oversight/ITEMS.md — PCDOE-008.
- Existing proposal process: docs/proposals/PROCESS.md.
- Existing permission boundaries: docs/proposals/AGENTIC-PERMISSIONS.md.
- DO phrasing: docs/ops/DO-PHRASING-FRAMING-FRAMEWORK.md.
- Siglary standard: docs/proposals/active/notation-sets/SIGLARY-STANDARD.md.
- Siglary A2A: .agents/skills/siglary-a2a/SKILL.md.
- DoE family: docs/ops/DOE-FAMILY.md.
- DoE scoring intake: docs/ops/DOE-SCORING-INTAKE.md.
- Experiment record schema: docs/ops/corpus/EXPERIMENT.schema.json.
- DoE method rules: .agents/skills/multivariate-doe/SKILL.md.
- Blind evaluation: .agents/skills/blind-agent-evaluation/SKILL.md.
- Agent team orchestration and MoneyBall / 3L0: docs/ops/AGENT-TEAM-ORCHESTRATION.md.
- Current proposal PR: https://github.com/timerloggedout-spec/termux-monorepo/pull/5531

**Evidence boundary:** this is a design proposal committed on the Pit Crew branch. Runtime prioritization, AutoApprove enforcement, live DoE execution and production promotion remain unimplemented until separately itemized, authorized and verified.
