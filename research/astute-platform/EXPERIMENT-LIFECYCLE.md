# Research Astute — Experiment Lifecycle

## Intake

Create one experiment manifest per thought experiment. Record its research question, scope, domain tags, initial hypotheses, known sources, graph types, and expected outputs. Intake creates a reviewable research record; it does not assign truth or feasibility.

## Lifecycle states

`proposed` → `scoped` → `seeded` → `research_active` → `under_review` → `published` → `archived`

Additional terminal or exception states: `blocked`, `paused`, `superseded`.

Every transition records actor, timestamp, prior state, new state, reason, evidence references, and revision.

## Continuous project cycle

Use the Loopy six-stage cycle:

1. **Observe** — fetch current experiment snapshot, source updates, graph validation, and outstanding questions.
2. **Choose** — select one bounded action using declared priority and confidence criteria.
3. **Act** — add or revise one bounded claim, source, concept, edge, path, or analysis.
4. **Verify** — run schema, graph, evidence, and relevant domain checks against the same snapshot.
5. **Record** — save action, evidence, result, changed IDs, and remaining work.
6. **Repeat or stop** — continue while measurable progress exists; otherwise emit a named terminal state.

Terminal states: `success`, `clean_noop`, `blocked`, `approval_required`, `exhausted`, `stagnated`.

## Work decomposition

- Experiment-level scope stays independent.
- Shared platform changes use their own issues and acceptance criteria.
- Independent path hypotheses can be researched in parallel when their evidence and files do not overlap.
- Merge and publication require the repository's existing validation and review policy.
- A loop run does not authorize scheduling, production changes, external messages, or irreversible operations.

## Research run receipt

Each run records:
- `run_id`, `experiment_id`, `snapshot_before`, `snapshot_after`;
- selected action and decision rationale;
- changed concept, claim, edge, path, and source IDs;
- tool/adapter versions and validation outcomes;
- evidence added, challenged, or retired;
- terminal state and remaining unproven work.
