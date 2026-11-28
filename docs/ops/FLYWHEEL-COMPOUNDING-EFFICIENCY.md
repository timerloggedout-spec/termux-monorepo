# Flywheel Compounding Efficiency (FCE) — Evidence Contract

**Method:** flywheel-compounding-efficiency/v1  
**Status:** PROPOSED · SHADOW-ONLY · NOT EXECUTED · NOT COUNTERSIGNED  
**Control:** que-task-rank/v1, dispatch admission, leases, auto-claim, and existing promotion authorities remain unchanged.

## Purpose

FCE measures whether a coordinated agent workflow produces more verified, reusable, downstream value per normalized unit of total effort. It is an evidence metric, not a claim about intelligence, a model leaderboard, a merge gate, or a production routing weight.

The existing task-ranking v3 shadow candidate is upgraded by extracting its efficiency calculation into a reusable reducer and carrying the observation into ATES, Action→Effect, DoE/MVT, replay, Moneyball, and SHE through explicit references. Existing records remain authoritative; no parallel scheduler, task ledger, Delphi weights ledger, or 3L0 contract is introduced.

## Formula

| Benefit dimension | Weight |
|---|---:|
| Direct verified outcome | 20 |
| Downstream unlock | 20 |
| Recurrence eliminated | 20 |
| Reuse / leverage | 15 |
| Reliability / risk reduction | 15 |
| Evidence confidence | 10 |
| **Total** | **100** |

B = Σ(weight × normalized_dimension)

B_realized = B × confidence_adjusted_realization

The denominator includes seven normalized cost dimensions, each scaled against a frozen, versioned cohort budget: execution effort; elapsed delay; context consumption; feedback cycles; conflicts/retries; human intervention; provider cost.

C_total = Σ(normalized_cost_dimension)

FCE_raw = 100 × B_realized / C_total

Every normalized input is in [0, 1]. cost_normalization_id identifies the frozen normalization basis. Missing, malformed, boolean, non-finite, out-of-range, or zero-total-cost evidence is ineligible; it is never zero-imputed and never protected by an epsilon denominator. Raw components and costs remain in the output.

## What makes it compounding

A single FCE value is an efficiency observation. Compounding is established only by a matched comparison against a source-pinned baseline with the same cohort ID, task ID/task-contract hash, environment fingerprint, validation-suite hash, cohort-manifest hash, and cost-normalization ID.

FCE_vs_baseline = FCE_candidate / FCE_baseline

FCE_delta = FCE_candidate − FCE_baseline

A ratio above 1 indicates higher measured efficiency for that matched observation; it does not independently prove causal improvement. Unmatched baselines are labeled INCOMPARABLE, not coerced into a ratio. The baseline itself must carry an observation ID, method, source SHA/ref, timestamp, and evidence references.

For manager/policy decisions, aggregate repeated observations within the pre-registered cohort and report sample size and uncertainty. Percentile ranks are cohort-local; they are not absolute scores and must not be compared across cohort snapshots.

## Evidence and identity

Each immutable observation records observation/cohort/task/manager-policy identity; source ref and full SHA; timestamp; task-contract, validation-suite, and cohort-manifest fingerprints; environment fingerprint and normalization ID; six benefit dimensions; seven cost dimensions; confidence-adjusted realization; and hashed evidence references.

The reducer validates the shape and provenance envelope. It does not authenticate external evidence or independently establish outcome correctness. Outcome truth remains with the fixed verifier, tests/checks, and Action→Effect realization evidence.

## Integration map

| Existing component | FCE use | Authority boundary |
|---|---|---|
| ATES / throughput | Join FCE by observation ID and cohort; keep TCV/WTCV/TPV/RPI/ATES separate | Observational; no speed-only gate |
| Action→Effect | Link FCE observation to verified effect and realization evidence | Temporal correlation is not causal attribution |
| DoE / MVT | Secondary outcome on cohort × task × arm × repetition | Pre-register factors, assignment, decision rule, and stop conditions |
| Evolutionary replay | Preserve raw FCE inputs and compare replay candidates | Online validation remains mandatory |
| Moneyball / Hex | Optional fce_observation dataset keyed by observation ID | Existing 3l0.moneyball.v1 contract unchanged |
| SHE snapshot | Project FCE, matched baseline ratio, cohort/sample size, method, evidence ref | Missing/unverified values remain absent or explicitly unverified |
| QUE task rank v3 | Shadow-only ordering signal; eligible and v1-fallback populations remain disjoint | No claim-order, dispatch, admission, lease, or auto-claim binding |

## DoE acceptance protocol

1. Register hypothesis, task-family blocks, treatment factors, repetitions, primary outcome, secondary FCE outcome, exclusions, decision rule, quota/cost cap, and stop conditions.
2. Freeze task-contract, environment, validation-suite, cohort-manifest, normalization, and scorer versions.
3. Randomize assignment within predeclared task-family blocks where practical; retain unexecuted assignments and deviations.
4. Execute baseline and treatment under the same fixed validation suite; preserve every failure, retry, skip, and censored observation.
5. Validate outcome/effect evidence before deriving FCE. Report components, costs, sample size, and uncertainty.
6. Promote no candidate from FCE alone. Require existing correctness, integration, security, dual-gate, and DoE/owner decisions.

This PR adds scorer/contracts only. It does not admit a DoE campaign, initiate an L5 replay, execute provider calls, or claim measured gains.

## Adaptive feedback / wait cycle

OBSERVE → CHOOSE → ACT → VERIFY → RECORD → REPEAT_OR_STOP

During long-running work, use WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY; continue only while fresh evidence or measurable progress is arriving. Preserve terminal states success, clean_noop, blocked, approval_required, exhausted, and stagnated. An error, timeout, missing artifact, or exhausted budget is never success. Do not rerun failures merely to improve a scorecard.

## refTemplates research inputs

This implementation uses existing metadata-only references rather than installing upstream software:

- refTemplates/15_Research_Repo_Templates/dicklesworthstone-agentic-flywheel/ — Agent Mail / Beads / triage / memory capability map and upstream core-loop profile; no wholesale installer or new scheduler.
- refTemplates/15_Research_Repo_Templates/jogyo-research-lab/ — hypothesis → experiment → finding → adversarial review.
- refTemplates/11_Evaluation_Quality/ — quality gates and benchmark methodology.

refTemplates remains metadata-first. No recursive clone, installer execution, new gitlink, external daemon, or Termux compatibility claim is introduced.

## Validation

python -m pytest scripts/que/test_flywheel_compounding_efficiency.py scripts/que/test_task_ranking_v3.py -q

**Promotion state:** shadow-only until a separately admitted, executed, reviewed, and countersigned DoE cohort establishes comparable evidence.
