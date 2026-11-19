# PCDOE-008 — Compounding Production Prioritization

**Status:** proposal / design-only  
**Parent workstream:** Pit Crew / DoE oversight  
**Work item:** PCDOE-008  
**Integration:** parallel companion to the existing Pit Crew proposal and its 20-seed tournament  
**Authority:** existing Operator, QUE/QDesk, DoE, and repository governance contracts remain authoritative

## 1. Purpose

Define and compare production-prioritization policies that select the next valuable task under real capacity, dependency, risk, and evidence constraints. Treat prioritization as a policy treatment inside the existing production system. Keep the execution chassis invariant while DoE compares policy variants.

The intended compounding effect is a measurable improvement in validated production value per constrained unit of effort, with quality, safety, reliability, and ownership obligations preserved.

This proposal adds a decision contract and policy treatments. Existing systems continue to own task admission, ranking integration, dispatch, claims, leases, execution, evidence storage, review, merge, release, and promotion.

## 2. System boundaries and integration

| Concern | Canonical owner | PCDOE-008 integration |
|---|---|---|
| Task intake, mandate, scope, admission and queue lifecycle | QUE / QDesk | Consume admitted task facts and return a recommendation or rank annotation through an approved seam |
| Claim, lease, dispatch, executor and completion evidence | QUE / QDesk | Observe lifecycle transitions; issue no dispatch or claim side effects |
| Pit Crew Chief responsibilities and 20 architecture seeds | Pit Crew proposal / PCDOE-001+ | Hold the Chief chassis invariant; evaluate prioritization as a separable policy factor |
| Experiment design, randomization, blocking, replication and analysis | DoE family | Preregister policy treatments and analyze outcomes independently |
| Canonical run observations | DoE/MVT EXPERIMENT schema | Emit or reference one canonical record per actual run |
| Manager cohort and policy identity | MANAGER-TOURNAMENT schema | Stamp policy version/hash, task contract hash, environment fingerprint and cohort |
| Cognition, intent, context and planning | Brain / ORBIT / SHIELD ownership | Consume bounded decision context; retain their existing authority boundaries |
| Dependency choreography | Ballet ownership | Consume dependency constraints and produce choreography through its existing seam |
| Production value and prioritization inputs | Existing MoneyBall / 3L0 ownership | Reference canonical value inputs; do not create a duplicate value ledger |
| Approval and promotion | Existing Operator / repository gates | Enforce explicit approval boundaries; recommendations remain advisory until admitted by existing policy |

**Integration invariant:** PCDOE-008 contributes policy variants and a versioned decision contract. QUE/QDesk remains the sole task lifecycle and dispatch authority. DoE remains the independent experiment designer and evaluator. The Operator retains promotion authority.

## 3. Prioritization decision contract

Each candidate decision consumes a timestamped snapshot of admitted work and returns a reproducible ordered recommendation.

Required input dimensions:

- **Value:** expected validated user, product, reliability, or strategic outcome; source and confidence accompany each estimate.
- **Effort:** estimated constrained work, elapsed lead time, and scarce specialist capacity.
- **Urgency:** deadline, time sensitivity, service impact, and delay cost.
- **Dependencies:** prerequisite count, critical-path position, and downstream work unlocked.
- **Risk:** operational, security, privacy, correctness, and rollback exposure.
- **Uncertainty:** evidence quality, estimate dispersion, and unresolved assumptions.
- **Reversibility:** recovery cost and blast radius.
- **Ownership:** accountable owner, approval class, and task mandate.
- **Age and interruption cost:** waiting time and context-switch burden, used as explicit policy factors rather than hidden tie-breakers.

Every input carries value, unit, source_ref, observed_at, and confidence where applicable. Missing evidence is represented as unknown with a reason. Policies preserve unknowns as unknowns and expose their effect on confidence.

Every recommendation returns:

- policy_id, policy_version, and immutable policy_sha256;
- snapshot_ref and evaluated_at;
- ordered task IDs and per-task component contributions;
- decision_reason and confidence;
- constraint and eligibility results;
- unknown inputs and evidence references;
- recommendation_only state and the existing owner for the next lifecycle action.

A policy recommendation is not a claim, dispatch, execution receipt, validation, review, approval, merge, release, or promotion.

## 4. Competing policy treatments

The first comparison keeps the candidate set, task contracts, execution chassis, evidence requirements, and environment constant. It varies only the prioritization policy.

| Policy ID | Treatment | Primary hypothesis | Main trade-off |
|---|---|---|---|
| priority-incumbent | Existing QUE/QDesk rank, captured as control | Existing ranking provides a strong operational baseline | Baseline behavior may leave value or dependency gains unrealized |
| priority-value-density | Confidence-adjusted validated value and effort-efficiency composite | Selects high-return work efficiently | Can defer urgent or enabling work |
| priority-critical-path | Deadline and dependency criticality first, with risk and effort constraints | Reduces end-to-end completion time | Can underweight standalone high-value work |
| priority-unlock | Downstream dependency unlock and portfolio unblock value first | Increases parallel throughput and reduces blocked work | Can favor infrastructure with weak direct outcomes |
| priority-risk-adjusted | Expected value discounted by uncertainty, exposure, and recovery cost | Improves reliable value and reduces costly reversals | Can become overly conservative |
| priority-balanced | Prespecified weighted combination of value, urgency, unlock, effort, uncertainty, and risk | Balances portfolio value and operational flow | Weight sensitivity and interaction effects require measurement |

The treatment definitions, weights, normalization, missing-data behavior, tie-breaks, and version hashes are frozen before assignment. Each policy is a distinct immutable treatment. A policy change creates a new version and a new treatment identity.

### Initial balanced-policy definition

Use normalized inputs in [0,1], with direction documented per factor:

    score = 0.30 × value_confidence_adjusted
          + 0.20 × urgency
          + 0.20 × dependency_unlock
          + 0.15 × effort_efficiency
          + 0.10 × reversibility
          + 0.05 × age

Risk is an eligibility constraint and a separately reported outcome in the initial version, rather than a compensating positive score. A high-risk task remains subject to its existing approval class regardless of score. Unknown critical inputs reduce confidence and can make a task ineligible for automatic low-risk handling.

These weights are a preregistered candidate, not an adopted production policy. DoE may reject or replace them based on the experiment design before execution.

## 5. Reusable DO-statement contract

A DO statement is a compact, machine-checkable task mandate. It gives every task a stable scope, action, constraints, expected output, and lifecycle state.

Canonical form:

> **⌖scope → ▶action → ⊗constraints → ⤵output → ~state**

Required fields:

- statement_id: stable unique identifier.
- scope: bounded target and included resources.
- action: positive-form imperative describing the requested work.
- constraints: safety, authority, budget, time, quality, and dependency rules.
- output: observable artifact or evidence contract.
- state: one of proposed, admitted, claimed, executing, completed, verified, promoted, blocked, cancelled.
- owner_ref: accountable owner or canonical owner role.
- acceptance: testable acceptance predicates.
- evidence: required evidence types and canonical evidence references.
- approval_class: preauthorized_low_risk, review_required, operator_required, or security_required.
- created_at, updated_at, and version.

Statements use positive, testable directives. Constraints state the required boundary and the authorized path. A task statement cannot grant authority beyond its owner, approval class, or parent mandate.

## 6. Bounded AutoApprove policy

AutoApprove is a policy for executing explicitly pre-authorized, low-risk actions within a finite allowlist. It is separate from GitHub review approval and from merge, release, credential, and production approval.

### 6.1 Eligibility

All conditions must hold:

1. The task is admitted by QUE/QDesk under its existing mandate and scope.
2. The exact action and resource pattern match a versioned allowlist entry.
3. The task has approval_class=preauthorized_low_risk.
4. Risk, blast radius, reversibility, and uncertainty fall within the allowlist thresholds.
5. Required inputs and evidence are present and fresh.
6. The actor identity, policy version, task ID, and action target are attributable.
7. The action is idempotent or has a tested compensating action.
8. Existing repository and organization policy grants the execution permission.
9. The action budget, rate limit, and time window remain within the declared bounds.
10. The result is recorded through the existing evidence path.

### 6.2 Initial allowlist candidates

The following are candidates for pre-authorization after owner review and tests:

- Read-only repository inspection and metadata collection.
- Deterministic local lint, formatting checks, schema validation, and unit tests.
- Regeneration of explicitly designated derived documentation or diagrams from canonical sources.
- Creation or update of draft artifacts on an isolated feature branch, within a task-specific path allowlist.
- Cancellation of a superseded, queued, idempotent read-only workflow where the existing queue policy already authorizes cancellation.

Each allowlist entry specifies action ID, resource pattern, actor class, maximum scope, maximum cost, timeout, idempotency proof, rollback/compensation, evidence contract, owner, and expiry/review date.

### 6.3 Approval-controlled actions

These retain their existing formal approval paths:

- GitHub pull-request review approval, request-changes, and review dismissal.
- Merge, branch protection changes, release publication, deployment, and production promotion.
- Credential creation, rotation, disclosure, secret access, permission grants, and identity changes.
- Destructive data operations, irreversible migrations, and broad resource deletion.
- Security policy changes, supply-chain trust changes, and changes to approval or governance rules.
- External financial commitments, paid usage beyond an explicitly approved budget, and legal or contractual commitments.
- Any action whose authority, scope, risk, provenance, or reversibility is unresolved.

AutoApprove can prepare evidence and request the formal gate. It cannot substitute for the authorized reviewer or Operator decision.

### 6.4 Decision and audit record

Every evaluation records decision_id, task_id, statement_id, policy_id, policy_sha256, action_id, resource_scope, actor, eligibility, reason_codes, risk_assessment, budget, evaluated_at, expiry, evidence_refs, and the canonical lifecycle result.

The outcomes are eligible, ineligible, expired, executed, execution_failed, and compensation_required. eligible records authorization under the bounded policy; executed requires an observed execution receipt. These states remain distinct.

## 7. DoE evaluation design

### 7.1 Research question

Which prioritization policy produces the greatest validated production value under equal task cohorts and execution capacity while preserving quality, safety, reliability, and ownership constraints?

### 7.2 Design

- Control: captured incumbent QUE/QDesk rank.
- Treatments: the five candidate policies above.
- Experimental unit: a comparable admitted task cohort within a fixed evaluation window.
- Blocking: task family, risk class, effort band, dependency depth, and operating window.
- Randomization: assign eligible cohorts to policy arms using the existing DoE assignment mechanisms and preserve the assignment seed and run manifest.
- Replication: preregister repetitions based on variance and power analysis; report the chosen design and assumptions.
- Holdout: reserve a fresh cohort for confirmation after screening.
- Chassis: hold Pit Crew seed, QUE/QDesk admission, executor, tool configuration, environment, acceptance contract, and evidence collection constant unless one is explicitly preregistered as a factor.
- Analysis: report uncertainty intervals, effect sizes, missingness, deviations, censored observations, and interactions. Preserve inconclusive outcomes.

DoE owns the design, randomization, analysis, and independent recommendation. The production operator authorizes any live treatment assignment that changes execution. A separate Operator decision governs adoption or promotion.

### 7.3 Outcomes

Primary outcome: validated production value per constrained effort unit, sourced from existing value-of-record evidence.

Secondary outcomes:

- task acceptance and correctness;
- end-to-end lead time and time-to-unblock;
- dependency throughput and blocked-time reduction;
- rework, regression, rollback, and incident rate;
- cost and resource use with provenance;
- owner intervention and approval latency;
- estimate calibration and decision confidence;
- fairness across task families and owner classes.

Quality and safety are guardrails, not compensating terms in a scalar score. A treatment that violates a guardrail is ineligible for promotion regardless of throughput.

### 7.4 Evidence rules

- One actual executed run maps to one canonical EXPERIMENT record.
- Use treatment.manager_policy_id for the policy identity and treatment.arm for the treatment arm.
- Stamp configured-instance identity using the existing treatment.instance contract where a configured model instance executes the work.
- Use the canonical manager tournament schema for cohort, policy version, task contract hash, environment fingerprint, evaluation contract, and provenance.
- Preserve baseline and candidate SHAs, status, provenance, confidence, and evidence references.
- A queued, admitted, claimed, or executing task is not a completed observation.
- A completed task is not independently verified until its acceptance evidence is present.
- A measured result is not a promotion decision.

### 7.5 Offline shadow evaluator

The companion implementation at `scripts/pcdoe/shadow_prioritizer.py` evaluates the six policy treatments against a frozen JSON snapshot whose mode is `read_only_shadow`. It produces ranked recommendations, component contributions, unknown-input annotations, risk eligibility, policy hashes, and a snapshot hash. Its result declares `recommendations_only=true` and an empty `side_effects` list.

Run the fixture evaluation with:

```bash
python scripts/pcdoe/shadow_prioritizer.py \
  --policies docs/ops/pcdoe/PRIORITIZATION-POLICIES.json \
  --snapshot tests/pcdoe/fixtures/shadow-snapshot.json \
  --output /tmp/pcdoe-shadow-result.json
```

The fixture is synthetic and verifies deterministic policy behavior, catalog-driven factor weights, unknown-input confidence, missing-risk handling, and risk eligibility. Missing factors remain null; the evaluator scores the known weighted factors and reports factor-coverage confidence. It is a software test, not a production observation or a DoE result. Live canonical snapshots require their existing owner to authorize access and supply the snapshot through an approved read-only seam.

The companion `scripts/pcdoe/autoapprove_shadow.py` evaluates the allowlist, actor, resource, scope, budget, timeout, expiry, identity, permission, risk, freshness, idempotency, compensation, and evidence predicates. It returns an eligibility decision only. Its tests assert that formal review, merge, release, promotion, and credential classes remain routed to formal approval and that the evaluator performs no requested action.

The compatibility suite validates a six-policy manager cohort against the existing `MANAGER-TOURNAMENT.schema.json` and validates a policy identity mapped to `treatment.manager_policy_id` against the existing `EXPERIMENT.schema.json`. These are in-memory schema fixtures only; the test emits and persists no experiment observation or tournament result.

## 8. Rollout sequence

| Stage | Deliverable | Gate |
|---|---|---|
| P0 | Contract, policy definitions, allowlist schema, fixtures and validator | Static validation and boundary tests |
| P1 | Shadow recommendations against read-only snapshots | Reproducible outputs; zero lifecycle side effects |
| P2 | Preregistered offline/replay DoE | Comparable cohorts, power/variance plan, independent review |
| P3 | One bounded live cohort | Explicit Operator authorization, existing QUE/QDesk execution, stop and rollback evidence |
| P4 | Fresh holdout and replication | Guardrails pass; independent DoE recommendation |
| P5 | Policy adoption proposal | Separate Operator decision and existing production gates |

## 9. Acceptance criteria

1. The policy set contains the incumbent control and five immutable candidate treatments.
2. Each policy produces deterministic, explainable recommendations for the same frozen snapshot.
3. The DO-statement schema validates required mandate, owner, acceptance, evidence, and approval fields.
4. AutoApprove fixtures prove allowlist matching, bounded scope, expiry, budget, identity, idempotency, and evidence requirements.
5. Formal review, merge, release, credential, security, destructive, and production-promotion actions always route to their existing approval owner.
6. Shadow evaluation produces recommendations with zero queue, claim, dispatch, execution, review, merge, or promotion side effects.
7. Experiment manifests and results conform to the existing canonical DoE and manager-tournament contracts.
8. Exact policy versions, task cohorts, environment, provenance, and confidence remain reconstructible.
9. The proposal creates no second scheduler, queue, router, ledger, experiment store, scoring service, or promotion authority.
10. Production adoption remains a separate, evidence-backed Operator decision.

## 10. Work ledger

| ID | Work item | Status |
|---|---|---|
| PCDOE-008.1 | Prioritization policy and decision contract | Proposed in this companion |
| PCDOE-008.2 | DO-statement contract | Proposed in this companion |
| PCDOE-008.3 | Bounded AutoApprove policy and approval boundary | Proposed in this companion |
| PCDOE-008.4 | DoE design and outcome contract | Proposed in this companion |
| PCDOE-008.5 | Static validators, canonical-schema compatibility fixtures and tests | Implemented on companion branch; exact-head CI pending |
| PCDOE-008.6 | Catalog-driven offline evaluator and shadow contract | Implemented on companion branch; canonical snapshot integration pending owner authorization |
| PCDOE-008.7 | Preregistered experiment and independent analysis | Pending DoE review |
| PCDOE-008.8 | Live cohort and adoption recommendation | Pending explicit Operator authorization |

**Current state:** design artifact only. This document does not assert that a policy has run, that AutoApprove has executed an action, that validation has passed, or that production policy has changed.

## 11. Source-of-truth references

- docs/ops/DOE-FAMILY.md
- docs/ops/MVT-DOE-ATES-SEPARATION.md
- docs/ops/corpus/EXPERIMENT.schema.json
- docs/ops/MANAGER-TOURNAMENT.schema.json
- docs/ops/QUE-AUTO-CLAIM.md
- docs/ops/DECISION-ENGINES.md
- Pit Crew proposal PR #5531 and operationalization issue #5532
