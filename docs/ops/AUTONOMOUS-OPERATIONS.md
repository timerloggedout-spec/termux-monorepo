# Evidence-Driven Autonomous Operations

## Purpose

This repository is an **automated agentic development environment**. Routine implementation, review routing, and staging integration should progress from measurable evidence rather than wait for a human approval message. The default production path is automated discovery, current-SHA validation, visible review evidence, and selective integration into `master-staging`.

> Human attention is reserved for irreversible authority, secrets, and policy changes. It is not a routine queue between a green agentic PR and staging integration.

## Operating Model

| Stage | Autonomous responsibility | Human/authority boundary |
|---|---|---|
| Work selection | Agents claim tracked items, branch from `master-staging`, and record evidence. | None for ordinary P1 implementation. |
| Review routing | Peer-review, second-pass, and Jules workflows collect findings and route actionable work to the current branch. | None; a non-author or automated current-SHA review is sufficient evidence for routine P1 progression. |
| PR eligibility | The `autonomous-merge` label opt-ins a PR to deterministic scope, review, thread, check, and mergeability evaluation. | Label removal is an immediate rollback switch. |
| Staging merge | The evidence-gated workflow may squash-merge an eligible routine PR into `master-staging`. | It never merges protected `master`, workflow/governance/security-sensitive changes, or PRs with unresolved evidence. |
| Tracker update | GitHub markers and proposal evidence are recorded automatically; Linear is updated when capacity is available. | Linear quota does not waive validation or audit evidence. |
| Production promotion | A focused promotion PR selectively advances a verified staging slice to `master`. | Protected-branch and production-policy requirements remain in effect. |

## Autonomous Merge Eligibility

The machine-enforced criteria in `.github/workflows/autonomous-merge-eligibility.yml` are intentionally stricter than a manual "looks good" signal. A PR must be non-draft, same-repository, current-SHA reviewed, thread-clean, mergeable, and check-clean; it must target `master-staging`, carry the opt-in label, and avoid workflow, governance, configuration, credential, and security-sensitive paths. The decision is persisted in a SHA-bound comment.

A new commit, label removal, failed check, unresolved thread, or `CHANGES_REQUESTED` review invalidates the prior decision. The automation neither runs PR code nor merges a PR solely because a label is present.

## Explicit Authority Boundaries

The following remain deliberately outside routine autonomous progression: credentials and secrets; force-push/history rewrite; protected-branch administration; first-time GitHub App or provider permission grants; workflow and configuration changes; private mapper custody; external A2A transport; destructive production actions; and `master-staging` to `master` promotion. These boundaries protect recoverability and do not impede routine agentic integration.

## Relationship to the Linguist Program

PR #275 benefits from automated peer review and evidence collection but is not opted into autonomous merging: it changes proposal/governance and workflow-adjacent material, so it remains a review-only PR. The dirty Jules stacks #154 and #177 remain excluded by mergeability and scope rules. The CEDRlang codec, local A2A foundation, and future mapper-custody work retain their separate explicit boundaries.

## Evidence and Rollback

Every autonomous decision produces a visible GitHub marker keyed to the head SHA. Operators and agents can inspect the marker, remove the opt-in label, open a review thread, or push a corrective commit. A landed staging change is rolled back through a focused revert PR, preserving the full audit trail.
