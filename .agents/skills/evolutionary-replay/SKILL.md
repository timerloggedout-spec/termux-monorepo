---
name: evolutionary-replay
version: 1
description: Use realized discovery history as a deterministic replay simulator for bounded manager-policy experimentation.
---

# Evolutionary Replay Skill

Use this skill when optimizing **exploration or orchestration policy**, not when attempting to autonomously rewrite the repository or train model weights.

## Required loop

1. Recon the current manager policy, cohort, SHA, workflow/run lineage, and evaluator.
2. Load a completed discovery history with immutable node IDs and realized outcomes.
3. Replay the incumbent first; this is the control.
4. Generate bounded data-only policy mutations.
5. Evaluate every candidate against the same replay history.
6. Keep the incumbent in the candidate set for every generation.
7. Record policy ID, history revision, replay score, covered nodes, replay cost, and generation lineage.
8. Select a candidate only when it meets the configured replay improvement threshold.
9. Deploy at most the selected policy to a fresh online cohort.
10. Use the normal WAIT -> WATCH -> VALIDATE -> RE-FETCH -> COMPARE -> RECORD loop.
11. Promote only after the existing Paper2Agent dual gate and correctness/integration evidence pass.
12. Append the new discovery tree; never overwrite prior history.

## Do not

- treat replay as execution;
- infer unseen outcomes from replay;
- score model intelligence from replay score;
- bypass provenance or dual gates;
- silently replace an incumbent with a candidate that only looks better after changing the evaluator;
- delete failed or negative observations.

## DoE-controlled plane

Use `scripts/agent_evolution/doe_control.py` when a replay study needs controlled
factor variation. DoE owns the pre-registered design and assignment; the replay
engine supplies deterministic offline observations.

1. Freeze campaign ID, hypothesis, evaluator/history revision, factors and levels,
   seed and practical threshold.
2. Generate the full-factorial policy design and retain exactly one incumbent control.
3. Validate design ID, arm uniqueness and control identity.
4. Replay every arm against the same immutable history.
5. Preserve every result and its design/campaign/arm/policy/history lineage.
6. Select at most one candidate for a fresh online confirmation cohort.
7. Create a separate confirmation assignment containing only incumbent + selected
   candidate; randomize within declared task blocks and emit canonical EXPERIMENT
   records for actual executions.
8. Analyze primary outcome, correctness, integration, cost and interactions separately.
9. Route promotion through proposal lifecycle and the existing dual gates.

The offline DoE design artifact is a preregistration record. The separate confirmation
assignment artifact covers only the incumbent and one selected candidate. Canonical
EXPERIMENT records remain the per-run observation ledger. Replay rows remain
`replay_only` and carry `recorded_outcomes_only` verification. Promotion-readiness
output is advisory; route promotion through proposal lifecycle and dual gates.
