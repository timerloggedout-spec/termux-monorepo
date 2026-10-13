# Source / Design

## Operator intent

The interactive visualization is not merely a prettier Gource. It is a custom rendering and command surface for repository owners and maintainers.

The repository already provides the necessary substrate:
1. OPS-EVENT-GOURCE schema defines a thin, seekable, append-only event IR compatible with Gource custom logs and existing ACTION-EFFECT-EVENT / EVIDENCE-ENVELOPE surfaces.
2. ops_event_seeklog.py provides SeekLog-compatible percent/index seeking and sequential/random replay semantics.
3. GOURCE-CORE-AGENTIC frames Core/Gource as an event-model and replay reference while keeping visualization optional.
4. The context relationship graph connects files, AST symbols, commits, PRs, issues, labels, timeline events, comments, reviews, and exact permalinks.

## Architecture

```text
MAINTAINER / OWNER
        │
        ▼
HITL CONTROL SURFACE
   ┌────┼─────────────┐
   ▼    ▼             ▼
 GRAPH REPLAY     COMMAND DECK
   │      │             │
   └──────┼─────────────┘
          ▼
 CUSTOM RENDERING ENGINE
          │
      OPS-EVENT IR
          │
   ┌──────┼────────┬────────┐
   ▼      ▼        ▼        ▼
 GitHub Workflows Cadence Evidence
   │      │        │        │
   └──────┴────────┴────────┘
                 ▼
          EVIDENCE ENVELOPE
                 │
        ┌────────┴────────┐
        ▼                 ▼
   Gource consumer   MDX/MMD/image
   parallel view     curation layer
```

## Core separation

Gource provides a proven temporal visualization grammar, custom-log compatibility, and a reference implementation for replay. Our engine adds typed operational events, provenance, action/effect/evidence correlation, context-graph overlays, HITL command semantics, cadence and collaborator events, and synchronized MDX/MMD/image projections.

The critical rule is: **renderers consume events; renderers do not become event authorities.**

## Event domains

Extend the OPS-EVENT vocabulary with stable domains/kinds for: repo commits/branches; issue open/comment/label/close; PR open/review/comment/status; workflow dispatch/run/check; cadence sprint/cycle; collaborator observed/plan; evidence receipt; and action proposed/approved/dispatched/completed/failed/reconciled.

Each event should carry stable identity, timestamp, actor/agent attribution when known, repository/ref scope, correlation/causation IDs, source URL, and evidence references.

## Command plane

```text
operator intent
  → command proposal
  → context preview
  → policy check
  → HITL approval
  → dispatch
  → runtime observation
  → effect capture
  → evidence envelope
  → event append
  → dashboard refresh
```

A dashboard click must never translate directly into an unrestricted API write. Mutating commands require exact target identity and explicit approval where policy requires it.

Example command intents include drafting a GitHub comment, previewing a reply to a Tribute PR, requesting collaborator synchronization, preparing a cadence transition, dispatching an approved workflow, requesting a PR review, reconciling a deployment, or opening a follow-up task from a collaborator comment.

## Comment intelligence

A comment control resolves its parent issue/PR, author, timestamp, direct permalink, referenced issues/PRs, changed files, labels, reviews, workflow runs, collaborator activity, and relationship-graph edges. The operator sees: Comment → Context → Proposed Action → Approval → Effect → Evidence.

The context-relationship graph's verified/candidate separation remains mandatory. Inferred similarity cannot silently become an operational fact.

## Cadence and collaborator plane

Cadence becomes an event stream rather than a separate calendar silo. Sprint/cycle events can reference scope, Tribute candidates, open PRs, blocked reviews, collaborator synchronization needs, experiments, completion criteria, and retrospective evidence.

Collaborator state must distinguish observed activity, explicit intent, inferred relationship, proposed synchronization, and confirmed synchronization. No autonomous outreach should be inferred merely from graph proximity.

## MDX / MMD / image curation

The existing artifact pipeline becomes a projection layer:

```text
OPS-EVENT + Context Graph
          │
          ├── Mermaid topology
          ├── MDX operator narrative
          ├── static image snapshot
          ├── interactive dashboard scene
          └── Gource-compatible replay
```

Every projection carries the same snapshot identity, source SHA, and event range so a maintainer can move from an image or MDX explanation back to the exact event set.

## n8n-style orchestration

n8n is useful as a workflow vocabulary: trigger → enrich → branch → approve → dispatch → observe → reconcile. It should not own repository truth. A future adapter can compile an approved control-plane command into a workflow graph while GitHub + OPS-EVENT + Evidence Envelope remain canonical.

## HITL safety boundaries

- Read-only by default for visualization, replay, and graph traversal.
- Explicit command states: DRAFT → CONTEXTUALIZED → POLICY_CHECKED → AWAITING_APPROVAL → APPROVED → DISPATCHED → OBSERVED → EFFECT_RECORDED → RECONCILED.
- No hidden writes from selection, dragging, expansion, or replay controls.
- Exact-target requirement for mutation.
- DISPATCHED is never equivalent to COMPLETED.
- Provider rate limits, cancellations, unavailable credentials, and deployment capacity remain distinct from application correctness.

## Reference views

1. Constellation — context graph + repository relationships.
2. Timeline — SeekLog temporal replay with scrub/seek.
3. Command deck — proposed/approved actions and state transitions.
4. Cadence board — sprint/cycle scope and collaborator synchronization.

Selecting an entity in one view should focus the same entity across the others.

## Acceptance criteria

- The dashboard can replay a bounded OPS-EVENT interval.
- A Gource-compatible log can be emitted from the same event range.
- Gource can be displayed in parallel without becoming authoritative.
- A selected GitHub comment resolves to its parent and related context.
- A command can be previewed without executing.
- Mutating commands require explicit HITL approval.
- Every dispatched command has a correlation ID and evidence envelope.
- A completed action produces an OPS-EVENT effect/evidence sequence.
- MDX/MMD/image projections identify source SHA and event range.
- Partial corpus state is visible and blocks unsafe claims.
- Verified and candidate graph edges remain visually and operationally distinct.
- Replay can pause, resume, seek, and compare two snapshots.
