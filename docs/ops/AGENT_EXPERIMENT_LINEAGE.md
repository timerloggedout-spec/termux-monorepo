# Agent Experiment Lineage

> Living control-plane specification for preserving multi-run, multi-agent experiment provenance.

## Purpose

A development cycle may contain many simultaneous lanes, workflow runs, retries, refinements, provider/model treatments, and validation passes. These must remain distinguishable without rewriting history or collapsing useful evidence.

## Identity hierarchy

```text
PROJECT / SCOPE
  └─ CYCLE
      ├─ EXPERIMENT / COHORT
      │   ├─ RUN
      │   │   ├─ ATTEMPT
      │   │   │   ├─ REQUEST
      │   │   │   └─ OBSERVATION
      │   │   └─ ATTEMPT ...
      │   └─ RUN ...
      └─ EXPERIMENT ...
```

### Required identifiers

- `cycle_id`: one iterative improvement cycle; may contain multiple runs.
- `experiment_id`: stable treatment definition within a cycle.
- `cohort_id`: population/treatment grouping used for comparison.
- `run_id`: one concrete workflow execution or equivalent provider execution batch.
- `attempt_id`: one attempt/retry/steering branch inside a run.
- `request_id`: provider/API request identity when exposed.
- `parent_attempt_id`: provenance edge for retries, refinements, or steering.

Identifiers must be stable enough to join GitHub events, workflow runs, logs, artifacts, provider telemetry, commits, reviews, and resulting outcome records.

## Multiple runs are evidence, not duplicates

A repeated run is not automatically a new experiment. Record its relationship:

```text
CYCLE-42
├── RUN-01  baseline
├── RUN-02  repeat / variance check
├── RUN-03  refinement
├── RUN-04  regression validation
└── RUN-05  promotion validation
```

The manager may add or cull runs dynamically. There is no application-level maximum number of lanes or runs. Platform/provider limits remain observable infrastructure constraints and must not be disguised as policy.

## Attempt lineage

Never rewrite Git history or erase unsuccessful attempts merely to make the current solution appear linear.

```text
X
├── attempt A → SHA A
├── attempt B → SHA B
└── attempt C → SHA C ← promoted
```

Promotion selects the validated successor. Prior attempts remain evidence.

## Treatment dimensions

The baseline matrix is:

```text
provider × model × prompt × manager × cohort × sequencing
```

It may be extended with task, repository/project, scope, validation class, reviewer, toolchain, context strategy, command stack, timing strategy, and other explicitly justified factors.

## Outcome record

Keep task outcome separate from performance metrics:

```text
outcome: PASS | FAIL | UNKNOWN + notes
correctness
integration
checks/tests
warning/error rate + severity
complexity / Big-O when relevant
compute/resource use
feedback/rework cycles
context/prompt efficiency
provider quota/resource use
latency
```

A successful HTTP response, workflow conclusion, low latency, or large response is not sufficient evidence of task success.

## Regression protection

Every promoted change records the validation runs that support it. A later regression creates a new observation and successor change; it does not delete the prior promotion evidence. A cycle remains open until the desired outcome is confirmed or a documented terminal condition requires new input.

## Graph integration

The context-relationship graph should connect:

`issue ↔ PR ↔ commit ↔ workflow ↔ job ↔ step ↔ log/artifact ↔ provider ↔ model ↔ request ↔ agent ↔ manager ↔ cycle ↔ experiment ↔ run ↔ attempt ↔ outcome`

Edges must carry evidence/provenance and temporal bounds where available. Unknown relationships remain explicitly unverified rather than inferred as facts.

## Skill feedback loop

Changes to this specification or related `.skill` files should themselves have provenance:

```text
observation
  → candidate process change
  → validation run(s)
  → promoted skill/spec revision
  → supersedes previous revision
```

This makes process documentation part of the same continuously improving agentic development system rather than an external manual audit.
