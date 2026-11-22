# DoE Tournament Contract

**Extension contract:** doe.design.v1  
**Canonical cohort contract:** manager.tournament.v1  
**Status:** proposed extension; existing schema remains authoritative.

## 0. Authority and reuse

The monorepo already defines:
- docs/ops/MANAGER-TOURNAMENT.schema.json — strict manager.tournament.v1 cohort envelope.
- docs/research/MANAGER-TOURNAMENT-CONTRACT.md — same-cohort manager comparison, judge hierarchy and anti-gaming rules.
- deepcli/deepcli/observatory/doe.py — full factorial, Taguchi L9 and seeded random assignment.
- deepcli/deepcli/observatory/trial.py and tournament.py — trial and campaign orchestration.
- docs/ops/EVOLUTIONARY-REPLAY.md — deterministic replay and incumbent-preserving evolutionary policy screening.

This document specifies the missing design-management layer: immutable experiment versions, factor-level definitions, treatment assignments, adaptive-allocation decisions and promotion lineage. It does not introduce a competing manager cohort schema.

## 1. Experiment preregistration

Every tournament begins with an immutable design record containing objective and decision question; hypothesis and null/alternative where statistically meaningful; task population and cohort inclusion criteria; factors, levels, controls and constraints; randomization/blocking/assignment method; outcome metrics and evaluator versions; sample-size rationale and stopping rule; resource budget and safety limits; promotion criteria and owner.

Changing the design creates a new experiment_version. Record deviations as events with reason and actor.

The design record references a canonical manager.tournament.v1 record by tournament_id and cohort_id. It carries the task_contract_hash, environment_fingerprint, manager policy hashes, evaluation_contract and repository provenance from that canonical record.

## 2. Factor model

| Factor | Example levels |
|---|---|
| Manager policy | sequential, hierarchical, blackboard, hybrid |
| Topology | DAG, blackboard, pipeline, hybrid |
| Execution provider | local, Actions, MCP peer, container |
| Model family | catalog snapshot entries |
| Prompt strategy | prompt version IDs |
| Review policy | single judge, dual judge, adversarial |
| Retry policy | none, bounded retry, repair loop |
| Environment | Termux, container image digest, runner image |

Do not hardcode model IDs as architecture. Resolve eligible providers from a dated catalog snapshot and retain that snapshot with each treatment.

## 3. Cohorts and assignment

- Use the same task definitions and acceptance criteria across treatments.
- Block by task complexity, language, scope, risk and dependency shape where possible.
- Randomize treatment assignment within blocks.
- Use paired or repeated runs when deterministic equivalence is feasible.
- Freeze a control treatment for longitudinal comparison.
- Keep exploration and exploitation cohorts identifiable.
- Prevent leakage of hidden evaluator answers into worker context.
- Record all exclusions and incomplete assignments.

Reuse the existing DoE functions where their semantics fit. Add a design method only when the current full-factorial, Taguchi L9 and seeded assignment helpers cannot express the preregistered design.

## 4. Outcome vector

Preserve raw measures: correctness and acceptance; integration quality; test/validation outcomes; source/evidence completeness; reproducibility; time-to-integrated-result; inference and compute expenditure; human effort and intervention; context/token usage when actually measured; retries, failures, conflicts and duplicate work; attribution confidence; ATES/WTCV/TCV/TPV/RPI as existing repository metrics.

Quality and acceptance remain separate from throughput. Missing metrics remain null.

## 5. Dynamic allocation

Initial stage: balanced or randomized allocation sufficient to estimate baseline variance.

Adaptive stage: select follow-up runs using one declared policy:
- Bayesian optimization for continuous parameters;
- constrained bandit for discrete treatment arms;
- evolutionary mutation/crossover for manager policy candidates;
- information-gain sampling for uncertainty reduction.

Every adaptive decision records policy version, input evidence window, candidate set, selected arm, exploration probability and rationale. Retain a randomized exploration/control fraction to detect drift and selection bias.

## 6. Tournament structure

- **Round 0 — baseline:** run the canonical control on the cohort.
- **Round 1 — screening:** compare candidate factor combinations.
- **Round 2 — interaction:** test promising interactions with factorial or focused follow-up runs.
- **Round 3 — robustness:** repeat on held-out tasks, environments and dates.
- **Round 4 — promotion:** evaluate feasibility, Pareto position, uncertainty and dual-gate/task outcome.
- **Round 5 — lineage:** promote policy version, preserve parent and evidence links, schedule drift monitoring.

Elimination from active compute does not delete candidate history.

## 7. Promotion contract

A candidate becomes promotable only when declared hard constraints pass; task outcome and integration acceptance pass; evidence and artifact provenance are complete; evaluator and environment versions are pinned; repeat/held-out evidence meets the preregistered rule; no unresolved critical safety/security findings remain; and the promotion decision records the exact experiment version and evidence digests.

ATES, speedup, token efficiency or nominal zero-cost capacity alone cannot promote a candidate.

## 8. Event and artifact requirements

Every execution receipt should link:

~~~text
experiment_id + experiment_version + tournament_id + cohort_id + treatment_id
+ task_id + run_id + run_attempt + head_sha
~~~

The tournament_id/cohort_id must resolve to the canonical manager.tournament.v1 envelope. Record provider/model/adapter/manager/agent identity separately. Store artifact names, media types, byte counts and SHA-256 digests. Raw prompts, completions, credentials and arbitrary tool payloads stay outside the canonical public evidence plane.

## 9. Stopping rules

Stop or pause on resource budget exhaustion; repeated infrastructure failure; safety/security gate failure; cohort contamination; evaluator drift; insufficient evidence to distinguish treatments; preregistered futility or success boundary.

A stop is a recorded outcome, not a synthetic pass.

## 10. Version evolution

- Schema changes use semantic versioning.
- Additive optional fields may be minor revisions.
- Changed semantics, identity rules or required fields require a major revision.
- Reducers declare accepted schema versions.
- Migrations preserve original payload digest and migration provenance.
- Historical scores can be recomputed from raw events with a named reducer version; original published decisions remain immutable.
