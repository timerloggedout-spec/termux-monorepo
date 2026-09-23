---
name: evolutionary-replay
version: 1
summary: Use realized discovery history as a deterministic replay simulator for bounded manager-policy experimentation.
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
