# Trigger & Workflow Registry

**Registry ID:** `termux-monorepo.trigger-workflow`  
**Schema:** `trigger-workflow-registry/v1`  
**Status:** INITIAL_BASELINE + ISSUE-TEMPLATE-CENSUS · workflow reconciliation in progress  
**As of:** 2026-11-27

## Purpose

One navigable relationship index for repository entry methods, GitHub events, selectors (labels, mentions, comment commands), admission gates, workflows, effects, and evidence feeds.

This registry is an **index and normalized relationship layer**. Existing specialized contracts remain authoritative for their domains. The generated workflow catalog remains the exhaustive workflow inventory; this registry deliberately avoids copying its 331 workflow rows.

## Authority map

| Concern | Source of record | Registry role |
|---|---|---|
| Workflow inventory | `docs/ops/generated/automation-workflow-catalog.json` | Link and normalize relationships |
| Workflow catalog generation | `scripts/ci/automation_docs.py` | Preserve existing generator |
| Issue-template dispatch | `docs/ops/ISSUE-TEMPLATE-DISPATCH.md` | Reference `issue-dispatch/v1` |
| QUE admission | `.github/workflows/swarm-admission.yml`, `scripts/ops/swarm_admission.py`, `ops/quota/dispatch-tiers.json` | Model admission gate |
| Research intake | `docs/ops/RESEARCH-TRIGGERS.md` | Link research-specific triggers |
| Labels and role dispatch | `docs/recon/team-formation/LABEL_TAXONOMY.md`, `ROLE_LABEL_DISPATCH.md` | Preserve additive label/role semantics |
| Dashboard surfaces | `docs/ops/SURFACES-MAP.md` | Connect methods to projections |
| Filing-to-publish | `docs/ops/REVIEW-PUBLISHING.md` | Model route and publish chain |

## 1. Method taxonomy

| Method | What the operator does | Actual event/selector | Key constraint |
|---|---|---|---|
| Issue template | Selects a form and submits structured intake | `issues.opened` / `issues.reopened` | Swarm dispatch requires a valid `SWARM-DISPATCH` block and QUE admission |
| Label | Applies or removes a typed label | `issues.labeled` / `issues.unlabeled`, where subscribed | A label is a selector/classification/state signal; it is executable only where a workflow consumes it |
| @ mention | Mentions an agent or role in a supported context | `issue_comment` / `issues`, per workflow | Mention syntax is workflow-specific; role stamps are attribution unless a parser explicitly consumes them |
| Comment command / marker | Posts a command or structured marker | `issue_comment` | Parser, authorization, idempotency key, and receipt belong to the owning workflow |
| Manual dispatch | Operator starts a workflow with inputs | `workflow_dispatch` | Inputs and permissions are defined by that workflow |
| Schedule | Time-based initiation | `schedule` | Cron and timezone interpretation are defined in workflow source |
| Git change | Pushes a branch/ref update | `push` | Branch/path filters matter |
| PR activity | Opens, updates, reopens, or marks a PR ready | `pull_request` | Activity types and path filters are workflow-specific |
| Review activity | Submits a review or inline comment | `pull_request_review`, `pull_request_review_comment` | Review/feedback handler owns the selector |
| Workflow completion | Completes an upstream workflow | `workflow_run` | Downstream workflow filters upstream name and conclusion |
| Reusable workflow | Calls a reusable workflow | `workflow_call` | Caller/callee contract owns inputs and secrets |
| Repository event | Sends a typed repository event | `repository_dispatch` | `event_type` and payload schema must be explicit |

**Important distinction:** an issue template is the human-facing entry method; `issues.opened` is the GitHub event that wakes a workflow. A label or mention is a selector only when an owning workflow explicitly parses it.

## 2. Issue-template census

Source enumeration of `.github/ISSUE_TEMPLATE/` found **14 YAML forms**: **2 declare `issue-dispatch/v1`** (`project-task`, `game-development-task`) and **12 are intake-only** in the current source snapshot. The census preserves each form's title, labels, source blob SHA, and parsed dispatch fields.

- Machine-readable source census: `docs/ops/generated/issue-template-census.json`
- Human-readable census: `docs/ops/ISSUE-TEMPLATE-CENSUS.md`

The 12 intake-only forms remain available to workflow-specific consumers; this classification means only that their template source has no `SWARM-DISPATCH` block. The contract's conversion checklist identifies these as remaining conversions.

## 3. Confirmed route examples

### Issue filing → QUE admission → route

```text
Issue template with SWARM-DISPATCH block
  → issues.opened / reopened
  → swarm-admission.yml
  → tier → after → chain → flow projection
  → ADMITTED or DEFERRED
  → declared route (only after admission)
  → route-specific intake / QDesk / build
  → publication workflow where applicable
```

The `issue-dispatch/v1` block declares lane, QUE tier, payload class, route, after-patterns, chain, and optional chain stage. The admission stamp and `swarm-admitted` / `deferred-by-tier` labels provide a receipt. Deferral preserves the filing for later queue re-evaluation.

### @jules issue handler

The generated workflow catalog identifies `agent-jules-on-issues.yml` (“Jules on Issues (label / @jules)”) with `issues` and `issue_comment` events. Exact selector parsing and activity filters remain in the workflow source.

### Research triggers

Research intake has its own contract in `docs/ops/RESEARCH-TRIGGERS.md`. It covers repository observatory cadence/manual runs, research seed records, PR-based recon, provider catalog completion, and issue-template intake. The owning document remains the detailed route map.

### Filing → build → publish

```text
issue-template filing
  → QUE admission
  → project-task-dispatch.yml
  → QDesk claim
  → build-dispatch.yml
  → PR/build receipt
  → per-surface GitHub Pages workflow
```

See `docs/ops/REVIEW-PUBLISHING.md` for current publish workflow and preview rules.

## 4. Workflow trigger exemplars

Eight routing workflows have now been source-read and recorded in `docs/ops/generated/workflow-trigger-census.json`, with a human-readable companion at `docs/ops/WORKFLOW-TRIGGER-CENSUS.md`. The sample covers QUE admission, project-task intake, admission-following game-development queueing, Jules labels and mentions, Gemini `/build`, provider commands, and Delphi marker/manual intake. Each record includes the workflow blob SHA and configured event/selector/gate/effect. This is an exemplar set; the generated catalog and live `.github/workflows/` directory now both contain 332 YAML workflows. The complete catalog-level event index is `docs/ops/generated/workflow-event-index.json`, with a human-readable companion at `docs/ops/WORKFLOW-EVENT-INDEX.md`.

## 5. Workflow event catalog

The generated catalog at `docs/ops/generated/automation-workflow-catalog.json` is the exhaustive per-workflow inventory. The inspected snapshot reports 331 workflows and records:

- workflow name and path;
- domain;
- trigger event names;
- schedules;
- jobs;
- authority class (`read-only-or-advisory`, `bounded-state-write`, `writer`);
- concurrency policy;
- pinned Actions.

The catalog's event-name summary does not fully encode activity types, branch/path filters, selector expressions, inputs, payload schemas, or permissions. Those require parsing the workflow source.

## 6. Label consumer census

Thirteen source-referenced labels now have producer/consumer relationship records in `docs/ops/generated/label-consumer-census.json`, with a human-readable companion at `docs/ops/LABEL-CONSUMER-CENSUS.md`. The records distinguish intake selectors, queue states, admission outcomes, domain queues, and learning signals. The repository's live labels collection was unavailable through the current GitHub read connector, so this is a selected source-backed census, not a complete live label inventory. Historical label counts remain dated evidence.

## 7. Labels, mentions, and commands

| Signal | Current interpretation | Reconciliation rule |
|---|---|---|
| GitHub label | Classification, route selector, admission state, or queue state | Link each label to the exact workflow/template consumer |
| `[MUSEai]@{role:{…}}` | Role/actor attribution and provenance stamp | Treat as executable only when a named parser consumes it |
| `@jules` | Example agent-mention selector in Jules issue workflow | Extract exact parser/context from workflow source |
| Slash command / HTML marker | Workflow-specific operator command or request key | Record parser, authorization, idempotency, and receipt |

Labels are additive taxonomy signals. The registry preserves original names and meaning; it does not rename labels or invent dispatch behavior.

## 8. Comment trigger census

Seventeen source-read comment routes now cover slash commands, mentions, provider commands, and HTML marker selectors. Records preserve workflow blob SHAs, line references, event arms, and authorization/context guards. See `docs/ops/COMMENT-TRIGGER-CENSUS.md` and `docs/ops/generated/comment-trigger-census.json`. This is a selected source-verified set, not an exhaustive parse of every `issue_comment` consumer.

## 9. Registry record model

The JSON companion defines stable IDs and these relationships:

```text
entry_method
  → trigger_event
  → selector (optional)
  → admission_gate (optional)
  → route
  → workflow
  → effect / receipt
  → feed / evidence
```

Every relationship carries status and source provenance. Use `CONFIRMED`, `PARTIAL`, `CANDIDATE`, `UNKNOWN`, or `RETIRED` for inventory confidence. Runtime state remains a separate vocabulary: `QUEUED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `CANCELLED`, `SKIPPED`. Admission and promotion states remain separate.

## 10. Feed and HUD integration

The dashboard consumes this registry as a read-only projection and joins it with the existing workflow catalog and per-surface feeds.

Recommended normalized feed fields:

`event_id`, `event_type`, `entry_method_id`, `selector`, `workflow_path`, `workflow_run_id`, `issue_or_pr_number`, `decision`, `authority`, `source_sha`, `occurred_at`, `observed_at`, `evidence_url`, `status`.

Use existing feed freshness contracts, including `generated_at`, source SHA, and stale indicators. GitHub and owning workflow artifacts remain authoritative. The HUD stays read-only.

## 11. Known gaps — explicit work queue

1. Extend the issue-template census into a refreshable deterministic extractor; initial source census is complete.
2. Expand the selected workflow trigger census into an exhaustive parser over the workflow catalog, including activity types, branches, paths, inputs, permissions, selector expressions, and outputs.
3. Census current GitHub labels and identify every workflow/template consumer.
4. Extract all `@mention` spellings, slash commands, and HTML marker parsers.
5. Join routes/workflows to `desk.html`, `admin-graph.html`, `proposals.html`, `dispatch-tree.html`, `pr-lanes.html`, and `tracking.html` through `SURFACES-MAP.md` and exact feed contracts.
6. Generate a deterministic reconciliation report with source fingerprint, timestamp, coverage counts, and unresolved edges.

## 12. Automation and update strategy

- Reuse `scripts/ci/automation_docs.py` and its existing workflow catalog refresh lane.
- Add a dedicated registry extractor only after the field mapping and parser fixtures are agreed.
- Make extraction deterministic and read-only.
- Validate duplicate IDs, unresolved references, missing provenance, unsupported event names, and authority mismatches.
- Publish a feed only from validated registry output; preserve partial/unknown coverage explicitly.
- Keep the source registry and generated runtime feed distinct.

## 13. Non-negotiable boundaries

- GitHub remains the source of truth for issues, PRs, labels, comments, workflow runs, and commits.
- Existing specialized contracts retain authority over their domain.
- QUE admission gates issue-template swarm dispatch.
- A role stamp is attribution until a concrete parser makes it a selector.
- A label is a selector only when an owning workflow consumes it.
- The registry and HUD describe execution; they do not grant execution authority.
- COMMITTED, EXECUTED, VALIDATED, and PROMOTED remain distinct.

## Sources and companion

- Machine-readable registry: `docs/ops/TRIGGER-WORKFLOW-REGISTRY.json`
- Workflow inventory: `docs/ops/generated/automation-workflow-catalog.json`
- Issue-template census: `docs/ops/ISSUE-TEMPLATE-CENSUS.md` and `docs/ops/generated/issue-template-census.json`
- Workflow trigger census: `docs/ops/WORKFLOW-TRIGGER-CENSUS.md` and `docs/ops/generated/workflow-trigger-census.json`
- Workflow event index: `docs/ops/WORKFLOW-EVENT-INDEX.md` and `docs/ops/generated/workflow-event-index.json`
- Comment trigger census: `docs/ops/COMMENT-TRIGGER-CENSUS.md` and `docs/ops/generated/comment-trigger-census.json`
- Label consumer census: `docs/ops/LABEL-CONSUMER-CENSUS.md` and `docs/ops/generated/label-consumer-census.json`
- Issue dispatch contract: `docs/ops/ISSUE-TEMPLATE-DISPATCH.md`
- Surface ownership map: `docs/ops/SURFACES-MAP.md`
