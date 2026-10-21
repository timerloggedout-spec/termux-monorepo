# Manager Tournament Contract

## Objective

Compare orchestration policies, not isolated model leaderboard scores.

A tournament runs the same task cohort against multiple manager policies under the
same tool inventory, environment contract, budget, and acceptance criteria.

## Manager record

Each manager declares manager_id, policy/version, routing graph, admission rules,
retry policy, escalation policy, parallelism policy, review policy, environment
fingerprint, and tool inventory fingerprint.

## Outcome dimensions

Preserve raw observations for task completion, time-to-integration, useful tokens,
duplicate tokens, feedback cycles, retries, conflicts, human interventions,
provider failures, model failures, final acceptance, attribution confidence,
and task complexity.

Throughput is never a merge gate by itself.

## Tournament protocol

1. Freeze task cohort.
2. Freeze environment/tool inventory.
3. Freeze evaluation rubric version.
4. Execute each manager.
5. Preserve canonical event JSONL and runtime provenance.
6. Run deterministic verifiers first.
7. Run LLM/agent judges only where deterministic verification is insufficient.
8. Compare integrated outcome and evidence quality.
9. Retain failures; do not cosmetically rerun them.
10. Record manager evolution and changed policy.

## Judge hierarchy

Use deterministic verification first, then environment-grounded evaluation,
then LLM-as-judge, then human adjudication for unresolved cases.

A judge score is evidence about the evaluator and cohort, not a universal model
ranking.

## Anti-gaming

Do not reward unnecessary agent activity, activity inflation through task splitting,
redundant reviews, retries without diagnosis, speed that lowers correctness, or
missing complexity treated as zero.
