# Delphic × DoE × MoneyBall — model-instance task allocation contract

**Version:** 0.1.0  
**Status:** integration design; execution gated by existing DoE/QUE prerequisites  
**Date:** 2026-11-12  
**Related:** DoE Family #1865 · role-clone pool #5183 · participant identity #5136 · inference executor #5176 · admission reliability #4979 · multi-arm routing #5151 / PR #5178 · DoE/queue program #5198 · Delphic #968 / PR #5216

## Objective

Make Delphic a reusable analysis capability in the existing DoE/MoneyBall model-task pool. Work is allocated **per eligible configured model instance**, selected for task fit and available capacity, not by a generic role label or model family name.

This contract does not create another model catalog, pool, scheduler, quota ledger, wallet authority, experiment registry or dashboard. Existing owners remain authoritative.

## Unit of allocation

A candidate arm is a configured instance, not merely a model:

```text
provider × model@version × endpoint/route × protocol
× account scope × system-prompt hash × tool-manifest hash
× role × moniker × context × instance_key
```

- DoE's canonical `treatment.instance` and `instance_key` remain authoritative.
- Build-dispatch arm identity (harness × endpoint) is a distinct population; do not conflate it with inference arms (provider × exact model × endpoint × protocol × account × configured instance).
- Candidate discovery may be broad; dispatch eligibility is exact-instance and current-window specific.
- Two configurations sharing model@version remain separate experimental units.

## Task-to-instance assignment

For each task filing, the allocator must:

1. Read the task's declared objective, artifact type, tool needs, context/sensitivity class, action ceiling, deadline/timebox and verification plan.
2. Filter the registered DoE pool to instances with an issued participant identity, eligible exact route, task-compatible capability evidence, current health/capacity, current free quota and matching action-class ceiling.
3. Exclude unknown/stale/unfunded quota, stale health, unsupported tools, unissued identity, unverified route and any card-gated/paid route. Do not use owner sessions as participant identity.
4. Rank eligible candidates by task fit, expected completion quality, latency/cost budget, recent reliability and diversity constraints. Keep ranking features and tie-break deterministic and auditable.
5. Use no-hard-select rotation among eligible candidates; no provider is selected because it is familiar or preferred. A quota-terminal (429) instance is terminal for its current quota window; rotate to another eligible instance without retry-burning.
6. Allocate one task to one configured instance per experimental unit unless the pre-registered design explicitly defines paired/replicated assignment. Parallel independent arms must be pre-registered, not improvised after observing results.
7. Require a verifiable output artifact. Silent-empty is an arm failure; quota/infra/unavailable is INCONCLUSIVE, not a model-quality failure.
8. Route the output to an independent verifier. The producing instance cannot self-certify its own outcome. Only independently verified outcomes may affect MoneyBall weights or DoE promotion/culling.

## DoE experiment design

- Use the existing DoE Family, Experiment schema and admitted campaign; proposals alone do not create observations.
- Pre-register hypothesis, factors/levels, assignment/randomization, blocking, sample-size rationale, stopping rules, outcome metrics, verifier and cull/promote thresholds.
- Treatment identity includes the complete configured-instance stamp and immutable prompt/tool hashes.
- One dispatched/executed run = one EXPERIMENT record = one observation.
- Minimum probation floor and other DOE-FAMILY rules apply; rule-7 floor n=3 is observational minimum, not proof of statistical significance.
- Distinguish execution status → task outcome → correctness → integration → regression → resource cost.
- No pooling observations across distinct instance_key values.
- Culls and cherry-picked propagation are explicit design events with cohort/version changes.

## MoneyBall wallet and culling

Reuse the MoneyBall participant-wallet pattern described by DoE Family:
- Per-participant wallet identity is attached to the registered participant, not inferred from provider/model.
- Initial allocation is paper/test class unless the owning MoneyBall lane explicitly establishes otherwise.
- No credit card, paid fallback, shared-bucket quota draws or unrecorded balance assumptions.
- Every cull event carries, in the same record: culled participant, wallet balance at cull, and pool destination. If no wallet balance is evidenced, write `NOT_ESTABLISHED`; do not invent a value.
- A cull outcome must not retroactively alter the experiment cohort or erase prior observations.
- Reward/weight updates require the independent verifier leg and DoE rule 9; provider quota/infra failures do not incur quality penalties.

## Required dispatch and observation stamp

At minimum, each task/run receipt binds:
- task_id and source filing reference
- experiment_id, cohort, design version and set_index/cumulative_n
- participant_id and participant registry reference
- provider, exact model@version, endpoint/route, protocol, account scope
- role, moniker, context, prompt ref+SHA256, tools ref+SHA256, instance_key
- dispatch_id/run_id, timestamp, selection reason and eligibility snapshot
- quota class, quota evidence timestamp/reset window, usage if available
- task artifact reference + content digest
- execution status, task outcome, correctness/verifier result
- latency/resource cost and explicit missingness
- parent dispatch/schedule-rule references for self-scheduled follow-ons
- receipt/hash-chain reference

Never place secret values in a stamp; references and hashes only.

## Integration tranches and dependencies

| Tranche | Work | Gate / owner |
|---|---|---|
| A | Passive read-only DoE/MoneyBall feed adapter; validate instance and task stamps | Delphic + DoE; no writes |
| B | Task-fit candidate ranking against already admitted, healthy, funded instances | Existing QUE governor / pool; no new scheduler |
| C | Exactly-once task claim and dispatch through existing executor | #5176, #4979 and #5151/#5178 sequence |
| D | Independent verification and append-only outcome receipt | DoE independent verifier / MoneyBall |
| E | Wallet consequences, reward weights, cull/promote and cohort propagation | MoneyBall owner + DoE Rule 9 / cull waterfall |
| F | Calibration and Observatory projections | Delphic read-only; canonical feeds remain source of truth |

Role-clone provisioning remains blocked by #5183's full-fleet census and #5136 participant-identity gates. Do not issue participants, provision wallets or quota buckets, or execute clone work ahead of those gates.

## Acceptance

1. A schema-valid task candidate packet references one or more exact configured instances with eligibility reasons.
2. A deterministic fixture proves task-fit filtering, quota-terminal rotation, no-hard-select tie-break and no cross-instance pooling.
3. A pre-registered DoE fixture produces correctly stamped observations without live provider calls.
4. Silent-empty, quota/infra, unavailable, honest task failure and independent-verifier failure are classified distinctly.
5. A cull fixture proves wallet balance/destination are in the same cull record and missing balance remains NOT_ESTABLISHED.
6. No live dispatch or wallet movement until the upstream admission, identity, executor, MoneyBall and independent-verifier gates are met.

## Authority boundary

Delphic calculates and projects. DoE owns design admission and experimental interpretation. MoneyBall owns participant-wallet economics and cull consequences. QUE owns policy, eligibility, claim/dispatch and action authority. Independent verifier owns correctness evidence. No component may assume another's authority.
