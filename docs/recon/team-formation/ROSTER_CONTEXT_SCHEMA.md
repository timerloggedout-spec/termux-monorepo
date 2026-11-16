# Anchored Roster Context and Identity Schema

## Recommendation

Use **anchored entity references with a context manifest** as the canonical schema. Do not use a single free-form path such as `Context/Role/Skill:Roster:Agent:{custom_team-a/b-run#'n'}` as the only persisted identifier. That notation is useful as a human-facing shorthand, but a roster needs separate records for a team, role, skill, agent, machine, target, task, run, label, and temporary batch. Combining those records into one string makes renames, membership changes, validation, queries, and score-event replay unnecessarily brittle.

The recommended model preserves the shorthand through aliases and command/UI formatting, while persisting typed references such as `team:game-players`, `role:strategy-4x-player`, `skill:gameplay-scenario-analysis`, `agent:custom-team-a:07`, and `run:game-players:0007`. The canonical record then binds them into one reviewable context manifest.

> **Canonical rule:** Human-readable labels and aliases may evolve. Stable entity references and their versioned relationship records remain the audit anchors.

## Schema Choices Considered

| Approach | Strength | Limitation | Decision |
|---|---|---|---|
| Colon-delimited compound string | Compact and readable in issue titles, commands, and dashboards. | Ambiguous ownership, brittle parsing, poor support for multiple skills/machines/labels, difficult rename history. | Keep as an alias/display format only. |
| Nested path-only hierarchy | Matches a tree of lane → team → role → agent. | Cannot naturally model an agent with multiple skills, teams with multiple lanes, shared machines, or batch/runs. | Use only for navigation/display. |
| **Anchored entities + relationship records + context manifest** | Typed, additive, queryable, versionable, supports aliases and many-to-many relationships. | More records and initial schema discipline. | **Recommended canonical model.** |

## Entity Registry

Every entity has a stable identifier, entity kind, display name, aliases, status, version, and provenance. The identifier is not repurposed after archival; a replacement receives a new identifier and links to its predecessor.

| Entity kind | Purpose | Example reference |
|---|---|---|
| `roster` | Root roster or program. | `roster:termux-monorepo` |
| `lane` | Broad responsibility boundary. | `lane:game-player-machines` |
| `team` | Cohesive operating group. | `team:game-players` |
| `role` | Specific work role and scorecard. | `role:strategy-4x-player` |
| `skill` | Evidence-backed capability; may be used by multiple roles. | `skill:gameplay-scenario-analysis` |
| `agent` | Individual roster candidate or machine-backed worker identity. | `agent:custom-team-a:07` |
| `machine` | Managed device, emulator, VM, or lab capability. | `machine:android-emulator-a14-01` |
| `target` | Repository component, controlled lab, artifact, game build, or wallet environment. | `target:game:unciv:pending-build` |
| `tool_profile` | Versioned tool/environment contract. | `tool-profile:ghidra-static-analysis:v1` |
| `scorecard` | Versioned role-specific measurement definition. | `scorecard:strategy-4x-player:v1` |
| `task` | Work request that has a target and expected evidence. | `task:issue-243:game-catalog-intake` |
| `run` | One bounded execution or observation instance. | `run:game-players:0007` |
| `batch` | Temporary grouping for custom team formation, review, or a quota-conscious PR batch. | `batch:custom-team-a` |
| `label` | Source label retained from GitHub or another system. | `github-label:roster-teams-games-players` |

## Relationship Records

Rather than inferring relationships from a long string, store them as typed records. A relationship has `from_ref`, `relationship`, `to_ref`, `valid_from`, `valid_to`, `evidence_ref`, and `status`.

| Relationship | Example | Meaning |
|---|---|---|
| `belongs_to` | `role:strategy-4x-player → team:game-players` | Establishes a roster hierarchy without preventing multi-team support elsewhere. |
| `operates_in` | `team:game-players → lane:game-player-machines` | Locates a team in its primary lane. |
| `demonstrates` | `agent:custom-team-a:07 → skill:gameplay-scenario-analysis` | Connects evidence-backed capability to an agent. |
| `assigned_to` | `agent:custom-team-a:07 → task:issue-243:game-catalog-intake` | Records a bounded assignment. |
| `runs_on` | `run:game-players:0007 → machine:android-emulator-a14-01` | Preserves device and environment provenance. |
| `targets` | `task:issue-243:game-catalog-intake → target:game:unciv:pending-build` | Makes the experiment/review object explicit. |
| `measured_by` | `role:strategy-4x-player → scorecard:strategy-4x-player:v1` | Separates score logic from role naming. |
| `grouped_in` | `agent:custom-team-a:07 → batch:custom-team-a` | Supports temporary custom teams without creating permanent taxonomy debt. |
| `sourced_from` | `target:game:unciv:pending-build → github-label:roster-teams-games-players` | Preserves origin-label context. |

## Context Manifest

A task or run uses a single context manifest to assemble the relevant references. This is the persisted replacement for a compound string while remaining easy to display as a short path.

```yaml
schema: roster-context/v1
context_id: context:game-players:strategy-4x:run-0007
status: proposed
roster_ref: roster:termux-monorepo
lane_ref: lane:game-player-machines
team_ref: team:game-players
role_ref: role:strategy-4x-player
agent_ref: agent:custom-team-a:07
skill_refs:
  - skill:gameplay-scenario-analysis
  - skill:session-telemetry-capture
machine_ref: machine:android-emulator-a14-01
target_ref: target:game:unciv:pending-build
tool_profile_ref: tool-profile:game-session-capture:v1
scorecard_ref: scorecard:strategy-4x-player:v1
task_ref: task:issue-243:game-catalog-intake
run_ref: run:game-players:0007
batch_ref: batch:custom-team-a
source_label_refs:
  - github-label:roster-teams-games-players
  - github-label:ml-pipelines
expected_evidence:
  - session-trace
  - objective-verdict
  - reset-record
review_pair:
  - team:game-qa-accessibility
```

The example’s short display alias can be written as `games/strategy-4x/custom-team-a/07/run-0007`. It is convenient for chat, dashboards, labels, and PR descriptions, but resolving it must always return the canonical manifest and entity references above.

## Mapping the Proposed Notation

| Suggested component | Canonical mapping | Reason |
|---|---|---|
| `Context` | `context:<domain>:<role>:<run>` manifest. | A context is a composition of records, not merely a name. |
| `Role` | `role:<slug>` entity plus a `scorecard:<slug>:vN` reference. | Roles and score formulas evolve at different rates. |
| `Skill` | One or more `skill:<slug>` references with evidence and confidence. | An agent can demonstrate multiple skills; a skill can serve several roles. |
| `Roster` | `roster:<slug>` root entity. | Supports multiple rosters or experiments without collision. |
| `Agent` | `agent:<team-or-lineage>:<sequence>` entity. | Gives each candidate a stable identity and lineage. |
| `{custom_team-a/b-run#'n'}` | `batch:custom-team-a` plus `run:<lane>:<sequence>`; optional display alias `custom-team-a/run-n`. | Separates temporary grouping from durable team taxonomy and run evidence. |

## Validation Rules

The first machine-readable validator can be small and deterministic. It should reject a manifest when a required reference is absent, a reference resolves to the wrong entity kind, an archived entity is assigned without an explicit override, a task target is not registered, a player run lacks a machine profile, a score event names a scorecard from the wrong role, or a run sequence collides within its lane/batch.

The validator should also preserve additive behavior: a new lane, team, role, skill, machine profile, game catalog entry, label, or scorecard is a new entity record rather than a schema edit. Aliases may be added or changed, but prior aliases remain available for historical resolution.

## Review-Friendly Batch Model

For the user’s quota-conscious review approach, `batch` is intentionally distinct from `team`. A batch such as `batch:custom-team-a` may group a limited, cohesive set of proposal items, schema records, and test evidence in one PR. The PR body should list the batch ID, the entity kinds affected, the items implemented, the expected reviewer templates, and the explicitly deferred work. This allows review bots to evaluate one coherent document/schema change without creating a PR per entity or hiding unrelated implementation changes in the same review.

The practical batch rule is: **one PR per coherent schema or evidence slice; cherry-pick only self-contained commits that do not change another batch’s entity contracts.** The initial PR is therefore documentation-only and intentionally contains the evidence package and schema proposal together, not a roster-engine refactor.

## References

[1] [Game Player Fleet and Genre Teams](./GAME_PLAYER_FLEET.md)

[2] [Initial Target Register Template](./TARGET_REGISTER.md)

[3] [Label Recon and Additive Team Taxonomy](./LABEL_TAXONOMY.md)

[4] [ATF active item backlog](../../proposals/active/agent-team-formation/ITEMS.md)

[5] [Recent Qodo review template on PR #248](https://github.com/timerloggedout-spec/termux-monorepo/pull/248#issuecomment-5335877275)
