# Issue Templates Trigger the Swarm Fleet

Owner contract (2026-11-03): **a filing IS a dispatch** — declared
at the template, never interpreted downstream — and it reaches the
swarm only **through QUE admission**. Today's treadmill was
unadmitted fan-out; template triggers must never spawn raw.

This document is the contract of record. Machinery:
`.github/workflows/swarm-admission.yml` (the route) +
`scripts/ops/swarm_admission.py` (the evaluator, with tests) +
`ops/quota/dispatch-tiers.json` (the tiers/chains it enforces).

## The dispatch block (schema `issue-dispatch/v1`)

GitHub's issue-form schema admits no custom top-level keys, so the
block rides as a structured comment header at the top of the
template file — in the template, machine-readable, invisible in the
rendered form:

```
# SWARM-DISPATCH-BEGIN
# schema: issue-dispatch/v1
# lane: <owning seat/route, e.g. swarm-dispatch>
# que_tier: <1-4 per dispatch-tiers.json>
# payload_class: <what the filing carries>
# route: <workflow that executes, e.g. project-task-dispatch.yml>
# after: <comma-separated workflow-name patterns, may be empty>
# chain: <dispatch-tiers chain entry, may be empty>
# chain_stage: <this filing's stage index in the chain, if any>
# SWARM-DISPATCH-END
```

Fields: `lane` (who owns the route) · `que_tier` (the filing's
dependency tier) · `payload class` (what kind of work it carries) ·
`route` (the existing machinery that executes it — admission never
replaces routes, it gates them) · `after`/`chain` (the v2 edges,
enforced at admission).

## The admission route

On `issues.opened`/`reopened`, `swarm-admission` matches the filing
to its template by the template's declared labels or title prefix —
the #3577 keying, so API-filed replicas of a form behave identically
to form filings. It then evaluates in the **dispatch-tiers v2 guard
order**:

1. **tier** — from the block.
2. **after** — any incomplete (queued/in_progress, non-ancient) run
   of an after-class pattern defers the filing. Wedged ancients
   (≥7 days, runner-free) are excluded: they would defer the fleet
   forever.
3. **chain** — when the block declares a chain + stage, incomplete
   prior-stage runs in scope defer the filing.
4. **flow projection** — live queued depth vs the tier's saturation
   threshold (v1: tier 4 defers at ≥400, tier 3 at ≥800; tiers 1–2
   never flow-defer).

**Fail-soft is the design.** Deferral stamps the reason on the issue
and labels it `deferred-by-tier`; the filing stays queued as an
issue — nothing is spawned, nothing is lost — and the QUE admission
drain (Tranche 4) re-evaluates deferred filings as the queue
clears. Evaluation errors defer too, with the error as the reason:
admission never admits blind.

## Receipts

The filing's **first fleet comment is its dispatch stamp**:
`[MUSEai]@{role:{swarm-admission}}` + decision (ADMITTED/DEFERRED)
+ template · lane · tier · payload · route · the flow numbers used
· after/chain results · the admission run URL. Admission applies
`swarm-admitted` or `deferred-by-tier`. The stamp is the
measurement-plane transition (enqueued → admitted/deferred) in
comment form until the QUE Tranche-1 plane store lands, at which
point the same fields emit as plane events.

## Exhibits — the partial instances this generalizes

Filed as exhibits, not parallel-built:

- **project-task** (#3577, PR #4076): the form + intake workflow
  validate and receipt filings; selection/execution happens in the
  dispatch machinery. **The proof conversion** (below) adds the
  block + admission in front of this existing route — the RFP/task
  batches that routed by hand now route by contract.
- **delphi-rfp**: filings wake the Delphi gate by event
  (`delphi-intake.yml`). Converts by adding the block; its gate
  becomes the route.
- **help-wanted intake** (3L0 tribute lane) and the **claim system**
  (`dispatch-claimed` labels + lease/watchdog machinery): the
  claim IS an admission-shaped act performed by hand today; the
  block + route formalize the same shape at filing time.

## Conversion checklist (remaining templates)

Each lane converts its own form by adding the block — the router is
generic and needs no change:

`apk-cross-reference` · `apk-cross-reference-findings` · `bug` ·
`data-ingestion` · `delphi-rfp` · `egm-review` · `proposal` ·
`research-provider` · `research-service` ·
`reverse-engineering-taxonomy` ·
`reverse-engineering-taxonomy-record` · `target-brief` · `game-development-task`.

A template without a block is simply not a dispatch: filings under
it get no stamp and no route (unchanged behavior).

## Game Development route (ATF-16)\n\n`.github/ISSUE_TEMPLATE/game-development-task.yml` declares `issue-dispatch/v1` with lane `game-development`, tier 3 and route `game-development-dispatch.yml`. The dedicated route is triggered by the completed `swarm-admission` workflow and consumes its one-run `issue-admission` artifact. It parses and queues only when the artifact identifies this template and records `decision: admitted`; deferred, unmatched or failed admission runs never queue. A deferred or missing admission decision never becomes an executable task. The form supplies the canonical `Entry`, `Task / spec`, `Scope`, and `Done-evidence` headings consumed by `scripts/dispatch/project_task.py`; it does not select a provider.\n\nThe existing Target Brief / Web Adapter Foundry route and the Reverse Engineering APK/taxonomy intake families remain separate.\n\n## Proof (2026-11-03)

`project-task.yml` converted end-to-end: block added, evaluator
tests 6/6 (local, disclosed interim), admission workflow live on
master; the proof filing and its admission run are stamped on the
filing itself and reported to the owner through main.

## Scientific and behavioral experiment routes

The scientific specialist forms are first-class triggerable filings, not manual labels:

| Template | Dispatch lane | Payload | Route |
|---|---|---|---|
| `.github/ISSUE_TEMPLATE/scientific-research-task.yml` | `scientific-quantitative` | `scientific-task` | `project-task-dispatch.yml` |
| `.github/ISSUE_TEMPLATE/behavioral-experiment-task.yml` | `do-statements-performance-psychology` | `behavioral-experiment` | `project-task-dispatch.yml` |

Both forms use the shared `Entry`, `Task / spec`, `Scope`, and `Done-evidence` intake headings. The existing project-task route retains its `issues.opened` and `issues.reopened` triggers. Because `swarm-admission` evaluates the same issue event in parallel, the route waits for a fresh, post-event `[MUSEai]@{role:{swarm-admission}}` receipt matching one of its registered templates before it parses or queues the filing. Stale receipts, other-template receipts, and deferred decisions do not dispatch. A `que-intake-event:<issue.updated_at>` marker makes the routing receipt idempotent for retries; a later reopen event has a new event key and is re-evaluated. Label and title-prefix matching both remain supported for API-filed replicas.

The specialist capability registry is `ops/roles/scientific-specialists.json`. It defines capability contracts and candidate role metadata; it does not create provider identities or new canonical DoE seats. Intake emits candidate role hints only. Assignment, execution, and promotion remain downstream responsibilities.

DO Statements and Performance Psychology are distinct experiment lanes. The combined lane is emitted only when both are present in the intake. A keyword match is `candidate_not_preregistered`, never proof of a designed or executed experiment.

