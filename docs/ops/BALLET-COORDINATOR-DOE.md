# Ballet Coordinator — DoE Tournament Registration

**Experiment family:** manager-policy / orchestration choreography  
**Policy:** ballet-coordinator  
**Policy version:** ballet.choreography.v1  
**Score version:** ballet.moneyball.v1  
**Tournament contract:** ballet.doe-tournament.v1  
**Status:** candidate experiment design; not production dispatch authorization

## Purpose

Compare choreography policies on the same task cohort using the repository's existing DoE full-factorial generator and Observatory tournament/leaderboard. Planning output is not performance evidence: every arm requires an online evaluation receipt.

## Factors

| Factor | Levels | Interpretation |
|---|---|---|
| strategy | sequential / parallel / adaptive | wave-construction policy |
| max_parallel | 1 / 2 / 4 | controlled treatment capacity for experiment only |

The initial design has nine arms. max_parallel is not a permanent scheduler limit. Production admission remains manager-, quota-, dependency- and platform-governed.

## Arm identity

{strategy}-cap{max_parallel}

Observation identity SHOULD extend manager experiment identity:

manager + policy_version + cohort + task_family + task_instance + arm_id + repetition + history_revision + head_sha

## Required online receipt

Each arm supplies accepted (boolean), integrated_correctness (boolean), time_to_integration_ms, cost_usd, retries, conflicts, duplicate_actions and human_interventions (all non-negative). Optional baselines specify time_to_integration_ms and cost_usd.

Missing fields are rejected. Missing evidence is not zero. Preserve raw receipts and failed/censored arms.

## Score v1

Default overrideable weights, normalized and returned in receipt:
- correctness 0.35
- acceptance 0.25
- time 0.15
- cost 0.15
- coordination 0.10

Coordination penalty = min(1, (retries + 2×conflicts + duplicate_actions + human_interventions) / 10).

Time/cost scores use explicit baselines. This score is a comparative index, not a correctness substitute or universal intelligence metric. Publish raw dimensions and run weight/baseline sensitivity analysis.

## Existing framework integration

- DoE arm generation: deepcli.deepcli.observatory.doe.full_factorial
- Tournament persistence/ranking: deepcli.deepcli.observatory.tournament.campaign
- Leaderboard: existing role/task/provider/model record keys; Ballet recorded under role ballet-coordinator.
- Existing evaluator and promotion rules remain authoritative.

## Promotion gates

1. At least three pilot repetitions per arm; increase if variance requires.
2. Fixed task contract, cohort, environment and evaluator versions.
3. No hard safety-gate failure.
4. Report confidence intervals, failure/censoring and sensitivity.
5. Candidate wins a fresh holdout cohort.
6. Existing correctness/integration gates pass.
7. Explicit operator promotion; never automatic.

## Invocation

From the deepcli package environment, call run_doe_tournament(tasks, observations, leaderboard=...) in deepcli.observatory.ballet. The function creates plans and consumes collected online observations; it does not dispatch work or call providers.
