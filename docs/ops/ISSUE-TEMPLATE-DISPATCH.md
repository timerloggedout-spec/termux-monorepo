# Issue Templates Trigger the Swarm Fleet

Owner contract (2026-11-03): a filing enters the QUE dispatch subset when its template declares a `SWARM-DISPATCH` block. The block is interpreted by admission machinery before the intended swarm route. Specialized issue-intake forms remain separate direct event routes.

The full template, label, event, and downstream-route registry lives in [`GITHUB-ISSUE-INTAKE-MAP.md`](GITHUB-ISSUE-INTAKE-MAP.md).

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

## Relationship to the full issue-intake map

This document defines the QUE admission subset. The complete 15-form inventory, label-added triggers, lifecycle floor, and observer workflows live in [`GITHUB-ISSUE-INTAKE-MAP.md`](GITHUB-ISSUE-INTAKE-MAP.md).

## Current dispatch-block coverage

| Template | Block lane | Tier | Route | Observed downstream contract |
|---|---|---:|---|---|
| `project-task.yml` | `swarm-dispatch` | 3 | `project-task-dispatch.yml` | Admission evaluates the block; the direct issue-event route remains active and creates the bypass described below |
| `game-development-task.yml` | `game-development` | 3 | `game-development-dispatch.yml` | The route consumes the `issue-admission` artifact and requires a matching `decision: admitted` |

The remaining 13 templates use specialized direct intake or manual lifecycle handling. Their event contracts and labels are catalogued in the intake map.

## Admission and downstream route alignment

### Project Task

`project-task.yml` declares `issue-dispatch/v1`, lane `swarm-dispatch`, tier 3, and route `project-task-dispatch.yml`. `swarm-admission.yml` evaluates the block on issue `opened/reopened`.

**Verified divergence:** `project-task-dispatch.yml` also subscribes directly to issue `opened/reopened` events. Its job guard matches the `project-task` label, `[task]` title prefix, or `Task / spec` body heading, then parses and queues on success. This direct path uses the issue event as its input rather than the `issue-admission` artifact. The declared admission gate therefore has a bypass path. Treat end-to-end QUE enforcement as pending until the route consumes the admission receipt, following the Game Development pattern.

### Game Development

`game-development-task.yml` declares `issue-dispatch/v1`, lane `game-development`, tier 3, and route `game-development-dispatch.yml`. The downstream workflow runs after `swarm-admission` completes, downloads the `issue-admission` artifact, and proceeds only when the artifact identifies this template and records `decision: admitted`. It then parses the canonical `Entry`, `Task / spec`, `Scope`, and `Done-evidence` headings before queueing.

### Specialized direct-intake families

- **Delphi RFP:** `delphi-gate.yml` uses the `delphi:rfp` label and issue/comment events; conversational intake is `delphi-intake.yml`.
- **Target Brief:** `target-intake.yml` validates scope and authorization on issue `opened/edited/reopened`.
- **Research, APK cross-reference, and RE taxonomy:** each has a deterministic parser and an event subscription documented in the intake map.
- **Data Ingestion:** the form remains on the challenge-entries hand-triage route while its dedicated intake workflow is pending.

These routes remain valid issue-intake mechanisms; they become QUE dispatches only after their templates declare and pass the dispatch-block contract.

## Proof (2026-11-03)

`project-task.yml` carries the dispatch block and the admission evaluator is live on master. The direct issue-event route remains active alongside admission; the end-to-end enforcement gap is recorded above and in the intake map.
