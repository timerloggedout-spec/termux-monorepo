# Provider-Agnostic Role Label Dispatch Contract

> **Status:** Proposal under ATF-15. This document defines a contract and does not enable a workflow, create labels, assign agents, start machines, or mutate a roster.

## Purpose

GitHub labels can be a concise **intent signal** for the user’s own teams and roles. They must not be treated as the role identity, task payload, authorization record, or provider selection. This contract maps an approved label to a stable roster context and an auditable dispatch intent. Any implementation later chooses a compatible in-house runner, queue, machine controller, or optional third-party bridge without changing the role taxonomy.

The resulting separation is intentional:

| Concern | Canonical record | Example |
|---|---|---|
| Visible issue signal | GitHub label | `Roster:Teams:Games:Players` |
| Role identity | Roster registry | `role:strategy-4x-player` |
| Team/lane location | Roster relationships | `team:game-players` in `lane:game-player-machines` |
| Task identity | Context manifest | `task:issue-243:game-catalog-intake` |
| Target and tool scope | Target/tool-profile records | `target:game:unciv:pending-build` and `tool-profile:game-session-capture:v1` |
| Dispatch decision | Dispatch intent | `dispatch-intent:issue-243:game-player-intake:v1` |
| Execution provider | Separately bound adapter | `dispatcher:termux-roster-orchestrator:v1` |
| Execution evidence | Run and review records | `run:game-players:0007` plus review pair |

> **Canonical rule:** A label triggers an approved policy. The policy resolves stable roster references. A provider only receives an already-resolved, reviewable dispatch intent.

## Core Vocabulary

| Term | Definition |
|---|---|
| **Role-trigger label** | A declared GitHub label that can request evaluation of a named role policy. It never contains unbounded instructions. |
| **Role policy** | Versioned rule that declares which role/lane/team may be selected, what context fields are required, what evidence is expected, and whether the outcome is `propose`, `queue`, `dry_run`, or a separately authorized `dispatch`. |
| **Context manifest** | Versioned record defined in [`ROSTER_CONTEXT_SCHEMA.md`](./ROSTER_CONTEXT_SCHEMA.md) that binds the task to its target, role, tools, machine, scorecard, and review pair. |
| **Dispatch intent** | A small auditable envelope created only after all policy preconditions resolve. It references—not duplicates—the context manifest and target record. |
| **Dispatcher binding** | A replaceable adapter from a declared policy to an in-house queue/runner or explicitly configured external integration. It is not a role and cannot redefine a policy. |
| **Label reconciler** | A manual, dry-run-first operation that compares declared policy labels with actual repository labels and reports proposed creates or metadata changes. |

## Policy Registry Shape

The later implementation should use a tracked registry such as `config/roster/role_label_policies.yaml`. The registry is the only source allowed to map labels to role policies or dispatcher bindings. It is reviewed like source/configuration, versioned, and referenced by context manifests.

```yaml
schema: role-label-dispatch/v1
repository: timerloggedout-spec/termux-monorepo

policies:
  - policy_id: role-dispatch:game-player-intake:v1
    status: proposed
    trigger_labels:
      - github-label:roster-teams-games-players
    trigger_mode: aggregate_issue_labels
    context_template: context:game-players:intake:v1
    roster_ref: roster:termux-monorepo
    lane_ref: lane:game-player-machines
    team_ref: team:game-players
    selectable_role_refs:
      - role:strategy-4x-player
      - role:simulation-player
    required_context_refs:
      - task_ref
      - target_ref
      - tool_profile_ref
      - scorecard_ref
      - review_pair
    expected_evidence:
      - session-trace
      - objective-verdict
      - reset-record
    outcome: propose
    dispatcher_binding_ref: dispatcher:termux-roster-orchestrator:v1
    idempotency_scope: issue-and-policy

  - policy_id: role-dispatch:mobile-analysis-intake:v1
    status: proposed
    trigger_labels:
      - github-label:reverse-engineering
      - github-label:ghidra
      - github-label:forensics
    trigger_mode: aggregate_issue_labels
    context_template: context:mobile-analysis:intake:v1
    roster_ref: roster:termux-monorepo
    lane_ref: lane:mobile-analysis-forensics
    team_ref: team:mobile-analysis-forensics
    selectable_role_refs:
      - role:mobile-artifact-analyst
    required_context_refs:
      - task_ref
      - target_ref
      - tool_profile_ref
      - review_pair
    expected_evidence:
      - target-record
      - method-log
      - findings-record
    outcome: propose
    dispatcher_binding_ref: dispatcher:termux-roster-orchestrator:v1
    idempotency_scope: issue-and-policy

providers:
  - dispatcher_binding_ref: dispatcher:termux-roster-orchestrator:v1
    kind: internal_adapter
    status: proposed
    accepted_policy_prefixes:
      - role-dispatch:
    writes_allowed: none

  # Optional examples only. They are not role definitions and are disabled by default.
  - dispatcher_binding_ref: dispatcher:jules-example:v1
    kind: external_adapter_example
    status: unbound
  - dispatcher_binding_ref: dispatcher:tembo-example:v1
    kind: external_adapter_example
    status: unbound
```

The example uses normalized source-label references. The visible GitHub spelling can remain `Roster:Teams:Games:Players`, while its durable registry identity is `github-label:roster-teams-games-players`.

## Role Trigger Resolution

A label event is not an immediate instruction to run an agent. The resolver collects the issue’s current declared labels, selects policies whose complete trigger set is satisfied, and resolves a candidate context manifest.

| Step | Input | Output | Required condition |
|---:|---|---|---|
| 1 | `issues.labeled` event or manual review | Current issue number and normalized label set | Event is from the declared repository. |
| 2 | Label set + policy registry | Eligible policy IDs | Every policy label is explicitly registered. |
| 3 | Policy + issue/target register | Candidate context manifest | Required role, target, tool profile, task, and reviewer references resolve. |
| 4 | Candidate context manifest | Dispatch intent | Policy state and outcome permit an intent. |
| 5 | Dispatch intent + idempotency ledger | One queue/proposal record or no-op | No active intent has the same issue, policy, context revision, and target revision. |
| 6 | Dispatcher binding | Provider-specific handoff or retained proposal | Binding accepts the policy and has the necessary separately configured capability. |

The first deployment should support **`outcome: propose`** and **`outcome: dry_run`** only. A policy may reach `queue` or `dispatch` only after its role, target, tool profile, scorecard, and independent-review requirements have been accepted in the roster proposal.

## Dispatch Intent

A dispatch intent provides a stable reconciliation point for GitHub, the relationship graph, and an internal orchestration queue. It carries identifiers and evidence URLs, not raw issue/comment bodies or secrets.

```yaml
schema: role-dispatch-intent/v1
intent_ref: dispatch-intent:issue-243:game-player-intake:v1
policy_ref: role-dispatch:game-player-intake:v1
status: proposed
issue_url: https://github.com/timerloggedout-spec/termux-monorepo/issues/243
source_label_refs:
  - github-label:roster-teams-games-players
context_ref: context:game-players:intake:issue-243
context_revision: 1
target_ref: target:game:unciv:pending-build
role_candidates:
  - role:strategy-4x-player
  - role:simulation-player
review_pair:
  - team:game-qa-accessibility
outcome: propose
dispatcher_binding_ref: dispatcher:termux-roster-orchestrator:v1
idempotency_key: sha256:declared-at-implementation
created_at: 2026-08-19T00:00:00Z
```

A provider adapter may record its own run handle against the intent, but it must not create a new canonical agent, team, role, or target reference. A failed adapter handoff updates only the intent status and bounded error category; it does not infer a substitute role or silently retry against another provider.

## Label Lifecycle and Creation

Labels are managed through a separate manual reconciliation path rather than by runtime dispatch logic.

| Operation | Actor and mode | Allowed behavior |
|---|---|---|
| Validate registry | Pull-request test or read-only workflow | Checks identifier format, duplicate labels, role/context references, and policy-to-dispatcher compatibility. |
| Reconcile labels | `workflow_dispatch`, dry run by default | Compares registry labels with GitHub labels and reports proposed creates/description/color changes. |
| Apply label reconciliation | Explicit operator-approved workflow input | Creates only labels already declared in the tracked registry; records action output. |
| Label event resolution | Runtime event, idempotent | Reads only predeclared labels and creates at most one dispatch intent per policy/idempotency key. |
| Provider dispatch | Separate adapter | Consumes resolved intent only; cannot manufacture labels or override policy state. |

This preserves the user’s requested label-driven behavior while avoiding brittle hard-coded workflows. New own-role triggers are added as registry records, for example `role-dispatch:ci-reliability-triage:v1` or `role-dispatch:research-intake:v1`; no workflow fork is required simply because a new team or role exists.

## Batch, Quota, and Review Behavior

Multiple label changes on the same issue should converge into one policy evaluation rather than emit a run for every label event. The resolver calculates an idempotency key from the issue, sorted eligible policy IDs, context revision, target revision, and policy version. A second event with the same key is a no-op; a changed context or policy produces a superseding intent with explicit linkage to the earlier one.

The review unit is therefore **one policy contract or one coherent set of policy records**, not one PR per label. A policy PR should include the policy IDs, role references, label aliases, context templates, expected evidence, allowed outcome, dispatcher binding state, and intentionally unbound providers. It should never combine a policy taxonomy change with unrelated runtime automation or provider credential changes.

## Graph Compatibility

The Context Relationship Graph can represent the GitHub side immediately after PR #244 lands:

```text
issue:243 --LABELED_AS--> label:Roster:Teams:Games:Players
label:Roster:Teams:Games:Players --IN_SCOPE--> scope:game-player-machines
```

The roster-role adapter proposed after PR #244 will add a sidecar mapping from `github-label:*` to `role-dispatch:*`, context templates, and roster references. The existing graph remains metadata-only and evidence-backed: it records verified GitHub label edges and registry evidence, while policy evaluation remains a separate deterministic process.

## Acceptance Criteria for ATF-15

The first implementation is acceptable only when it can validate the registry and demonstrate all of the following without dispatching a real provider:

1. A registered own-role label resolves to a policy and a proposed context manifest.
2. An unregistered label produces no role policy and no dispatch intent.
3. A label whose policy lacks a required target/tool/review reference is reported as blocked with the missing reference.
4. Repeated label events with the same idempotency key create no duplicate intent.
5. A changed policy/context revision supersedes, rather than overwrites, the earlier intent.
6. A provider binding marked `unbound` cannot execute a dispatch, even if its example label exists.
7. The manual reconciler can report label differences in dry-run mode and cannot create labels absent from the reviewed registry.
8. The graph/roster bridge stores references and evidence URLs only; it retains no issue, comment, review, session, or credential body content.

## References

[1] [Anchored Roster Context and Identity Schema](./ROSTER_CONTEXT_SCHEMA.md)

[2] [Label Recon and Additive Team Taxonomy](./LABEL_TAXONOMY.md)

[3] [Game Player Fleet and Genre Teams](./GAME_PLAYER_FLEET.md)

[4] [ATF active item backlog](../../proposals/active/agent-team-formation/ITEMS.md)

[5] [Context Relationship Graph PR #244](https://github.com/timerloggedout-spec/termux-monorepo/pull/244)

[6] [Game Teams issue #243](https://github.com/timerloggedout-spec/termux-monorepo/issues/243#issue-5185983300)
