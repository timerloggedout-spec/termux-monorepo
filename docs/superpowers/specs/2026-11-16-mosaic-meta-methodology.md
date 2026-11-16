# MOSAIC — Meta-Methodology Self-Improvement & Calibration

**Full name:** **M**ethodology **O**ptimization, **S**elf-assessment, **A**daptive **I**ntelligence & **C**alibration  
**Former working label:** META-DOE  
**Parent:** DoE family (docs/ops/DOE-FAMILY.md)  
**Broader evolution lane:** CEEL (docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md)  
**Status:** proposed specification; no runtime implementation is claimed.  
**Version:** 0.1.0 · **Date:** 2026-11-16

> MOSAIC makes the method itself an experimental participant. It does not replace the experiment family that hosts it.

## 0. Executive DO

~~~text
DO[RECON]  @DoE + @CEEL + @ATES + @Delphi + @SHE + @3L0 + @MoneyBall
           -> map authority; detect duplication; preserve SSOTs.
DO[MODEL]  @method := versioned_participant && immutable_artifact && declared_scope.
DO[TEST]   @method[vN] vs @method[vN+1] -> same frozen benchmark && comparable budget.
DO[GRADE]  independent_evaluator(method, evidence, preregistered_criteria).
DO[LEARN]  findings -> revision | explicit_no_change | rollback | supersede.
DO[PROMOTE] require[independent_validation && gates_pass && practical_gain && no_unaccepted_regression].
DO[REPEAT] event_or_evidence_delta -> RECON; preserve every prior version and verdict.
~~~

**Invariant:** MOSAIC may propose changes to its own method; it may not author its own acceptance criteria, independently validate itself, or promote itself.

## 1. Name, purpose and boundary

MOSAIC is the meta-evaluation and calibration discipline for methods that design, assign, execute, analyze, compare or promote experiments.

It applies recursively to DoE design selection; factor/level selection; cohort construction; randomization, rotation, blocking, replication and stopping; adaptive allocation; evaluators, scorers and thresholds; orchestration and manager policies; attribution/backfill/provenance; and MOSAIC itself.

**DoE remains the family and discipline.** MVT and ATES remain nested members/surfaces under current repository doctrine. CEEL remains the broader capability-discovery/evolution lane. MOSAIC is a named meta-methodology program within that structure.

Do not globally rename DoE, MVT, ATES, CEEL, campaigns, schemas, feeds, paths or historical records. META-DOE is retired as a new-work label; historical references remain verbatim.

## 2. Existing-system integration — no parallel plane

| Concern | Existing authority | MOSAIC rule |
|---|---|---|
| Family/campaign membership | docs/ops/DOE-FAMILY.md | No competing family registry |
| Design vocabulary/maturity | docs/ops/DOE-TAXONOMY.md | Register method status honestly |
| Generators/assignment | deepcli/deepcli/observatory/doe.py | Extend only after tests/admission |
| Run observation | docs/ops/corpus/EXPERIMENT.schema.json | Canonical record; no shadow receipt |
| Configured-instance identity | treatment.instance / instance_key | Never aggregate by model name alone |
| Evidence/outcomes | SHE / 3L0 / MoneyBall / ATES | Cite source records; do not copy payloads |
| Independent challenge | Delphi Oracle / EGM | Preserve independent challenge |
| Capability discovery | CEEL / Integration Intelligence | Map opportunities into existing graph |
| Promotion | proposal lifecycle / dual gates | No score-based auto-merge or production promotion |

Existing doe.criteria-loop (#1959) and delphi.method-self-application (#1963) are predecessor mechanisms. MOSAIC unifies their conceptual contract and evaluation vocabulary; it does not imply implementation or validation beyond their recorded evidence.

### Live issue reconciliation (2026-11-16)

Both predecessor RFPs were fetched from GitHub and remain **open + labeled delphi:parked**; neither is evidence of a completed self-improvement cycle.

- **#1959 — doe.criteria-loop:** the DoE criteria set itself is the participant. Its six stated criteria cover family intake, EXPERIMENT record conformance, generator+test admission, preregistered verdict discipline, reporting/uncertainty discipline and within-segment comparison. The RFP requires each cycle to end in a revision PR or an explicit no-change record; criteria do not self-adopt. Its current issue body identifies PRs #1871, #1873, #1874 and #1954 as prior criterion evidence. Current status is parked, not an active execution claim.
- **#1963 — delphi.method-self-application:** the Delphi method is the participant. Its predeclared replay variants are method-v2-control, method-v2-moneyball-required and method-v2-debate-mandatory, using the recorded Strands and Temporal passes as equalized inputs. The RFP says replay receipts must include command, exit and output SHA; a persistent tie remains a valid result. Its described landing condition includes a pass record and panel.json self_application update. Current status is parked; the issue body describes the pass as specified_not_run, not completed.

**MOSAIC integration decision:** preserve both RFPs and their separate surfaces. MOSAIC supplies shared identity, preregistration, independence, outcome-vector and version-lineage rules; it does not merge their ballots, criteria, ledgers or evaluation authority. Reopen/execute either only through its existing Delphi/cadence/governance path.

## 3. Recursive participant model

A methodology is a versioned participant with a bounded capability contract.

~~~text
METHOD := {
  method_id, method_version, artifact_ref, artifact_sha256,
  parent_method?, objective, scope, factors, assignment_policy,
  analysis_policy, stopping_policy, budget, assumptions, known_limits,
  preregistration_ref, created_at
}
~~~

Identity rules:
1. method_id is stable across revisions; method_version is immutable.
2. Any material change to factors, assignment, scoring, stopping, analysis, thresholds or promotion logic creates a new version/cohort.
3. Record exact source commit and SHA-256 of the method artifact.
4. Preserve predecessor/successor edges; never rewrite historical results.
5. Missing identity/provenance = NOT_ESTABLISHED, not inferred.
6. A method can be treatment, evaluator or both only when roles are declared separately.

Recursion is bounded by explicit evaluation depth and budget. MOSAIC may evaluate its own protocol, but evaluator and promotion authority remain outside the method version under test.

## 4. Meta-experiment lifecycle

~~~text
DISCOVER -> REGISTER -> PREREGISTER -> ADMIT -> ASSIGN -> EXECUTE
  -> OBSERVE -> ANALYZE -> INDEPENDENT_REVIEW -> DECIDE
  -> PROMOTE | HOLD | REVISE | CULL | SUPERSEDE -> REPEAT
~~~

| State | Meaning | Evidence |
|---|---|---|
| proposed | Candidate method/revision | Rationale + expected effect |
| registered | Stable identity assigned | Method ID/version + immutable artifact |
| preregistered | Test plan frozen | Hypothesis, outcomes, design, budget, stop rule |
| admitted | Governance allows execution | Required owner/gate decision |
| executed | Work actually ran | Run identity + canonical observations |
| analyzed | Results computed | Analysis code/version + uncertainty |
| independently_reviewed | Separate evaluator challenged claim | Reviewer identity + verdict |
| promoted | Accepted for declared scope | Practical gain + gates + rollback |
| held | Evidence insufficient | Explicit gap + revisit trigger |
| revised | New version created | Delta + new preregistration |
| culled | Removed from active competition | Reason + evidence + required domain accounting |
| superseded | Replaced in defined scope | Successor link; old record retained |

Queued/running is not executed evidence. A committed design is not a run. Passing schema tests do not prove outcome improvement. Promotion is always scope-bound.

## 5. Fair comparison contract

Every method tournament MUST declare:

- Question and decision the result can change.
- Hypothesis, expected direction and mechanism.
- Baseline method and exact revision.
- Competing method versions and declared factors.
- Frozen population, task/cohort/suite and inclusion rules.
- Assignment method: randomization, rotation, blocking or justified alternative.
- Identity: configured instances, prompt/tool hashes, manager/policy version, environment and source SHA.
- Primary, secondary and harm/regression outcomes.
- Budget: runs, time, tokens/credits, human effort and retries.
- Analysis: estimator, uncertainty, missingness, multiplicity and interaction treatment.
- Stopping rule and held-out confirmation.
- Decision thresholds and rollback plan.

Controls:
- Keep task and evaluator fixed while changing the method under test, unless explicit factors.
- Distinguish repeated measures on one task from independent task replication.
- Check sample-ratio mismatch and assignment integrity before interpreting effects.
- Preserve negative, failed, skipped, blocked, censored and unavailable outcomes.
- Never use latency as correctness proxy or quota as quality score.
- Never choose metrics/cohorts/stopping after seeing outcomes to manufacture a winner.
- Adaptive allocation preserves realized assignment history and requires valid adaptive analysis.
- Do not claim interactions that the design cannot identify; disclose aliasing and uncertainty.

## 6. Evaluation vector — no opaque winner score

~~~text
Q = (
 validity, reproducibility, correctness, calibration, information_gain,
 interaction_detection, adaptation, robustness, fairness, attribution,
 decision_utility, cost, latency, maintenance, security, regression
)
~~~

Evaluate scientific validity, information efficiency, reproducibility, calibration, adaptivity, robustness, decision utility, operational burden and governance. Retain per-dimension estimates, uncertainty intervals and practical thresholds. Use Pareto analysis. If a scalar is required for a narrow decision, expose weights and sensitivity-test them; retain the raw vector.

## 7. Independence and anti-gaming

~~~text
METHOD(author) != METHOD(evaluator) != METHOD(promoter)
~~~

- Method under test cannot choose its winning metric after execution.
- Evaluators receive frozen criteria and identical evidence scope.
- Prefer blind evaluation; disclose unavoidable unblinding.
- Record conflicts and shared implementation/evaluation dependencies.
- A failed evaluator can itself be tested, but cannot invalidate inconvenient results without independent evidence.
- Delphi/EGM and proposal governance retain existing authority.
- Human-only, financial, credential, deployment, production-routing and irreversible actions remain behind existing explicit gates.

## 8. Evidence contract — keep canonical schema

Do not create a second experiment record schema. docs/ops/corpus/EXPERIMENT.schema.json remains authoritative and strict.

- Campaign DESIGN.json (or its existing design artifact) carries method ID/version, immutable artifact reference/hash, hypothesis, factors, allocation/analysis/stopping policies, budget and preregistration.
- One canonical EXPERIMENT record remains one observation per dispatched/executed run.
- treatment.manager_policy_id records the actual manager policy identity when that is the treatment; do not overload it with unrelated metadata.
- evidence_refs point to exact campaign design, method artifact, run receipt and analysis artifact.
- provenance, confidence, status, usage and null semantics remain honest.
- Any future schema extension requires its own proposal, compatibility analysis, tests and migration/backfill plan.

Comparison outputs are append-only campaign artifacts with versioned analysis code and explicit source record IDs; they do not substitute for run records.

## 9. Siglary Operator Notation (SON) — micro-dense DO statements

**SON is a proposed authoring profile for the existing Siglary system.** It reuses registered operators and the repository's existing DO-statement marker. It does not issue a parallel notation system.

The Matrice and Standard remain authoritative. The current SON candidate uses the registered operators below; all field names, identifiers, version labels and references remain ordinary text.

| Registered operator | Existing meaning | SON use |
|---|---|---|
| ∧ | logical AND | require every listed condition |
| ∨ | logical OR | accept any listed alternative |
| ¬ | logical NOT | state an explicit negated predicate |
| ⇒ | implication | express a rule-to-outcome implication |
| ∀ / ∃ | universal / existential quantifier | state quantified scope |
| ∅ / ∈ | empty set / membership | express set conditions |
| ∆ | measured change | describe a measured revision |
| ++ | postfix one-step increment | express one-step version progression |
| ≅ | conformance predicate in Siglary register | state conformance only when evidenced |

DO: is the existing plain-text DO marker, not a new operator. Colons and line breaks are field delimiters, not operators. The profile introduces no new glyphs or chords in this candidate.

### DO statement shape

~~~text
DO: PHASE
  target: named participant or artifact
  version: immutable version identifier
  evidence: canonical source references
  scope: declared scope
  require: condition ∧ condition
  preserve: named invariants
  emit: artifact and provenance
  decide: rule ⇒ outcome
~~~

### Canonical SON examples

~~~text
DO: RECON
  target: DoE family and CEEL
  evidence: current source-of-truth files and GitHub records
  emit: dependency map and evidence-qualified gaps
  preserve: historical records and source ownership

DO: REGISTER
  target: methodology identity
  version: immutable version label
  evidence: source commit and artifact SHA-256
  scope: declared methodology capability
  preserve: predecessor versions and lineage

DO: PREREGISTER
  target: method comparison
  evidence: hypothesis, baseline, arms, outcomes and budget
  require: frozen criteria ∧ independent evaluator ∧ stopping rule
  preserve: the preregistration before execution

DO: ASSIGN
  target: frozen cohort
  evidence: assignment plan and randomization seed
  require: randomized allocation ∨ documented alternative
  emit: assignment record and sample-ratio check

DO: RUN
  target: admitted method arm
  evidence: method version and configured-instance identity
  emit: one canonical EXPERIMENT record per executed run

DO: BLIND
  target: independent evaluator
  evidence: frozen criteria and identical evidence scope
  require: evaluator identity distinct from method owner

DO: DECIDE
  target: scope-bounded method revision
  promote_candidate: practical_gain ∧ independent_review ∧ gates_passed ∧ ¬critical_regression ∧ rollback_ready
  hold: evidence_incomplete ∨ uncertainty_exceeds_limit ∨ gate_pending
  revise: evaluator_refuted ∨ critical_regression
  cull: explicit_governance_decision ∧ evidence_recorded

DO: EVOLVE
  target: methodology
  evidence: independently reviewed finding
  emit: revised version or explicit no-change record
  preserve: every predecessor version

DO: REPEAT
  target: MOSAIC evaluation cycle
  require: new_event ∨ new_evidence
  emit: next bounded RECON cycle
~~~

**Decision semantics:** practical_gain is a promotion condition only. HOLD, REVISE and CULL use their own evidence and governance conditions. MOSAIC emits a recommendation; it does not execute a promotion. Existing repository-managed FA-ADE may promote an independently validated, scope-bounded change after the required dual gates pass and its outcome is verified. The method under evaluation never grades or promotes itself.

### Linguist admission contract

1. Record SON as a candidate extension in the existing Notation Matrice.
2. Review its grammar, delimiter semantics and operator-class usage in the Linguist lane.
3. Preserve the existing Siglary Standard, Shorthand Domains, exemptions and principle ⑤.
4. Route any proposed new chord or operator through collision review and an explicit Linguist ruling before use.
5. Keep the existing DO-statement style workflow and its policy revisions as the enforcement path; SON adds no duplicate gate.

Until the Linguist ruling is recorded, treat SON as a proposal profile and use expanded plain language wherever a reading could be ambiguous.

## 11. Initial work packages

| ID | Priority | Work | Exit condition |
|---|---:|---|---|
| MOS-001 | P0 | Method identity/version contract | Immutable ID, version, artifact ref/hash and scope |
| MOS-002 | P0 | Independence/preregistration contract | Criteria, baseline, evaluator and decision rule frozen before execution |
| MOS-003 | P0 | Reconcile #1959 and #1963 | Existing loops mapped; duplicate behavior identified |
| MOS-004 | P1 | Method tournament pilot | Two or more versions on one frozen cohort with canonical records |
| MOS-005 | P1 | Calibration/uncertainty report | Per-dimension estimates, uncertainty, missingness and practical effect |
| MOS-006 | P1 | SON glossary/examples | Examples conform; undeclared sigils rejected in review |
| MOS-007 | P2 | Adaptive method selection | Sequential policy compared with fixed baseline using valid analysis |
| MOS-008 | P2 | Recursive MOSAIC evaluation | MOSAIC vN vs vN+1 tested independently under bounded recursion |

## 12. First pilot — method-selection tournament

**Question:** does a method-selection policy improve experimental decision quality and cost versus current documented practice?

Proposed arms (not yet admitted):
- M0: current documented DoE method-selection practice.
- M1: objective-first taxonomy selection + preregistered design-adequacy checks.
- M2: M1 + adaptive sequential allocation with baseline/control preserved.
- M3: M2 + independent blind challenge before promotion.

Freeze the same task/campaign population, method inputs, resource budget, acceptance contract and independent evaluator. Treat manager/policy version as an explicit factor. Do not conflate model/provider effects with methodology effects.

Primary response: independently verified decision utility against a predeclared acceptance contract.

Secondary responses: information gain per cost, uncertainty calibration, interaction detection, reproducibility, missingness, assignment integrity, latency, human interventions, retries and maintenance burden.

Analysis: full outcome vector, per-arm uncertainty, practical effect and Pareto frontier. A small screening cohort is descriptive only; make no significance/generalization claim without adequate design and replication. Confirm finalists on a held-out cohort.

Promotion: repeatable practical gain + no critical validity/security/privacy regression + independent review + source evidence + rollback + existing repository gates. Otherwise HOLD or REVISE.

## 13. Failure modes and controls

| Failure | Control |
|---|---|
| Method grades itself | Independent evaluator + frozen criteria |
| Criteria drift after outcomes | Preregistration hash + versioned amendment |
| Model-only grouping | Configured-instance identity + SHA tuple |
| Repeated tasks mistaken for replication | Separate repeated-measure/task-replication treatment |
| Survivorship bias | Preserve failures, culls, blocked and censored rows |
| Adaptive allocation invalidates naive inference | Preserve assignment history; valid adaptive analysis |
| Composite hides trade-offs | Outcome vector + Pareto frontier |
| Cherry-pick erases provenance | New version/cohort + parent edge |
| Workflow success mistaken for outcome | Separate admission/execution/effect/validation/promotion |
| Recursive evaluator collusion | Bounded depth + independent challenge |
| Duplicate control plane | Reuse canonical SSOTs and event/workflow paths |
| Unknowns silently imputed | null / NOT_ESTABLISHED; never infer |

## 14. Acceptance and rollout

1. Docs-only foundation: approve specification/work ledger; no runtime behavior changes.
2. Reconciliation: read full issue/PR history for #1959 and #1963; map live artifacts/current status.
3. Method registry decision: test whether existing component registry and campaign DESIGN artifacts carry required identity; extend only for proven gaps.
4. Pilot preregistration: freeze one bounded comparison; no live dispatch before authorization.
5. Offline validation: fixtures for immutable identity, version changes, evaluator independence, nulls, preregistration freeze and state transitions.
6. Live evidence: existing authorized workflows only; collect canonical records.
7. Independent challenge: Delphi/EGM or assigned evaluator; record VERIFIED/PARTIAL/REFUTED.
8. Promotion: proposal lifecycle + repo-gate + Termux smoke + owner review; no automatic production promotion.
9. Watch: detect regressions; revert/supersede through normal change control.

### Non-goals

Reuse the existing experiment ledger, registry, scheduler, event bus, orchestrator, provider router and merge authority. Keep credentials, paid inference, external account writes, private data export and deployment outside this work package. Preserve historical records and observational data without retroactive conversion into designed experiments. Treat a committed specification as a proposal, not as evidence of runtime implementation.

## 15. External statistical references

These references support methodological cautions; they do not establish repository implementation or validate any MOSAIC result.

- Marschner (2021), *A General Framework for the Analysis of Adaptive Experiments*, Statistical Science 36(3), 465–492. Adaptive designs carry information through both realized allocation and observed outcomes; inference must account for the adaptive design history. https://doi.org/10.1214/20-STS803
- Bibaut & Kallus (2025), *Demystifying Inference After Adaptive Experiments*, Annual Review of Statistics and Its Application 12, 407–423. Adaptive allocation/stopping can invalidate naive non-adaptive inference; methods such as variance stabilization/reweighting and always-valid inference may be needed, depending on assumptions. https://doi.org/10.1146/annurev-statistics-040522-015431
- Morris, White & Crowther ADEMP framework, extended as ADEMP-PreReg in *Simulation Studies for Methodological Research in Psychology* (2024). Method comparisons should specify aims, data-generating mechanisms, estimands, methods and performance measures, justify simulation repetitions, report Monte Carlo uncertainty, and preserve reproducible code/data. https://pmc.ncbi.nlm.nih.gov/articles/PMC7616844/

**Interpretation rule:** preregistration improves transparency but does not rescue a defective design or invalid analysis. Distinguish exploratory discovery from confirmatory evaluation, and disclose deviations rather than silently rewriting the plan.

## 15. Repository source map

- .agents/skills/multivariate-doe/SKILL.md
- docs/ops/DOE-FAMILY.md
- docs/ops/DOE-TAXONOMY.md
- docs/ops/MVT-DOE-ATES-SEPARATION.md
- docs/ops/DOE-COMPONENT-REGISTRY.md
- docs/ops/corpus/EXPERIMENT.schema.json
- experiments/doe/bf-1-backfill-methods/DESIGN.json
- docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md
- docs/proposals/active/continuous-capability-evolution-lab/MANIFEST.md
- docs/proposals/active/continuous-capability-evolution-lab/ITEMS.md
- docs/proposals/PROCESS.md

This is a proposed architecture, not a claim of current runtime behavior. Reconcile the live issue/PR state before implementation.
