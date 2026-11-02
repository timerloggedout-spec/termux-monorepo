# NESTED-FAMILY — provider ⊃ model ⊃ {roles, tasks run} (nested-family/v1)

Owner standard (2026-11-01, via main; tracking lane leads): every
**provider → model → {role(...); task[list]}** becomes viewable ∧
tracked per nested family, **with dispatch connection** — each task
entry links its dispatch record. Spec of record for the
`nested-family/v1` substrate; render = Web Dev lane (dashboard family,
live-chart standard); scoring-plane records = DoE expert lane's
EXPERIMENT/intake carriers, consumed here as sources, never re-scored.

## The record

| Piece | Path |
|---|---|
| Canonical record | `ops/tracking/nested-family.json` (`nested-family/v1`) |
| Dashboard twin | `apps/help-wanted-dashboard/data/nested-family-feed.json` (byte-identical payload; pages consume the feed and nothing else) |
| Generator | `scripts/tracking/nested_family.py` (offline; committed records only) |
| Single-writer | `.github/workflows/repo-tracking-collect.yml` (same writer as the tracking surface) |
| Tests | `tests/test_nested_family.py` |

## Schema (nested-family/v1)

```
{
  schema: "nested-family/v1",
  generated_at, generated_by,
  spec: {doc, grouping, task_link},          // this file + join rules, carried in-record
  sources: [{id, path, records_read, records_used}],
  summary: {providers, models, roles, tasks, dispatches,
            by_outcome{status: n}, by_source{id: n}},
  providers: [{
    provider,                                 // verbatim from the stamp
    models: [{
      model,                                  // model@version VERBATIM as recorded;
                                              // NOT_ESTABLISHED stays literal, never resolved
      roles: [..],                            // distinct roles this model has played
      monikers: [..],
      contexts: [..],
      task_count,
      tasks: [{                               // the task list it has run
        task_class, role, moniker, context,
        dispatch_id,                          // join key to the dispatch record
        run_id, workflow, session_id,         // dispatch connection (run-id join)
        ts,
        outcome: {status, gate_call, confirmed},
        instance_key,                         // when the source carries one, else null
        source,                               // source id (below)
        source_ref,                           // repo path of the dispatch record
      }]                                      // sorted by ts
    }],
    model_count, task_count,
  }],
  gaps: [..],
}
```

## Sources (existing records only — ∅ new instrumentation)

Priority order; a dispatch is counted **once**, under the highest
priority source that carries it (dedupe key = `dispatch_id`, falling
back to `session_id` for desk rows):

1. `stamps` — `experiments/doe/routed-dispatch/stamps/*.json`, the
   canonical dispatch stamps (stamp fan-out, Swarm lane). Flat
   3l0-intake-shaped records: {dispatch_id, ts, provider, model,
   endpoint, moniker, role, context, task_class, run{run_id,
   session_id, workflow}, outcome{status, gate_call, confirmed,
   artifact}, quota{pool, slice, cost_class}, instance?}.
2. `intake` — `ops/3l0/intake.jsonl` (3l0-intake/v1), the fan-out copy;
   catches dispatches whose canonical stamp file is absent.
3. `desk-usage` — `ops/challenge/desk-feed.json`
   `traversals[].provider_usage[]`, the DoE scoring carrier (util-1
   auditor + routed carrier): {provider, model, role?, moniker?,
   session_id, state, via, context?}. No run_id/dispatch_id on this
   carrier: the task entry links by `session_id`, `dispatch_id` =
   null, outcome = {status: state, gate_call: null, confirmed: null}.

Non-sources, named: PLAN rows (planned ≠ run — the family lists tasks
a model **has run**); EXPERIMENT records without a provider-bearing
instance (cannot nest honestly); session-history provenance records
(no dispatch outcome semantics).

## Rules

- **Verbatim identity:** provider/model/role/moniker are copied from
  the stamp exactly; grouping is provider ⊃ model ⊃ tasks, and a
  model's roles are the distinct roles across its tasks. Never
  collapse by model alone across providers (the same model string
  under two providers = two families). A stamp whose model field is
  absent/null nests under the literal `NOT_ESTABLISHED` (fleet
  honesty convention: missing = NOT_ESTABLISHED). Desk-carrier
  outcome states can be full prose verdicts: task entries keep them
  verbatim; only the summary's `by_outcome` buckets prose states
  (>40 chars) under `(prose state — verbatim in tasks)`.
- **Dispatch connection:** every task carries `dispatch_id` +
  `run_id` + `source_ref` (the stamp's repo path) — the run-id join
  back to the dispatch record of record. Where a carrier lacks one of
  these, the field is null and the gap is structural (named in the
  record), never back-filled.
- **Honesty:** `NOT_ESTABLISHED` values in sources stay literal
  (a stamp whose model is NOT_ESTABLISHED nests under that literal —
  it is a real dispatch with an unrecorded model, not an error).
  Outcomes are the stamp's own; this substrate never scores,
  confirms, or re-judges them (scoring planes own verdicts).
- **Single-writer:** only `repo-tracking-collect.yml` writes the
  record + twin. Coverage grows as stamps flow; lanes never hand-edit
  the outputs.
