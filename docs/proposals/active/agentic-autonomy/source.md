# Evidence-Driven Autonomous Agentic Operations

## Decision

Routine P1 work should not pause for a manual approval when the current revision has a deterministic evidence trail. The operating system should advance a pull request from review evidence to **autonomous-merge eligible** only when every measured criterion is satisfied. Eligibility is a marker and a review-routing signal; it is not a direct merge command.

## Autonomous Eligibility

A non-draft pull request can receive an autonomous-eligibility marker only when all conditions hold for its current head SHA:

| Criterion | Required evidence |
|---|---|
| Scope | The author applies the `autonomous-merge` label. |
| Base | The PR targets `master-staging`; no staging-to-`master` wholesale merge is allowed. |
| Mergeability | GitHub reports the PR as mergeable and not `dirty`. |
| Reviews | At least one current-SHA automated or non-author review is present, with no `CHANGES_REQUESTED` review on that SHA. |
| Threads | No unresolved review threads are present. |
| Checks | All repository-owned required or observed check runs are successful or explicitly skipped; cancelled runs do not qualify as success. |
| Sensitive scope | The diff must not change `.github/workflows/**`, `.github/actions/**`, `docs/proposals/**`, security/credential paths, or branch-protection/configuration files. Those changes remain review-only. |
| Evidence | The workflow posts a SHA-bound, idempotent marker with the decision inputs and any excluded external status context. |

## Automatic Outcomes

The operating flow is deliberately progressive but not opaque. Existing peer-review, second-pass review, and Jules-routing workflows continue to collect and act on evidence. The new autonomous eligibility pass translates completed evidence into a visible marker, updates the relevant tracker if available, and lets an authorized merge workflow or agent act only on the current SHA. A new commit invalidates prior eligibility automatically.

## Safeguards That Remain

The following operations are not reduced to autonomous routine progression: credential rotation or secret access; force-push or history rewrite; protected-branch administration; first-time permission grants; workflow/configuration/self-modifying automation; private mapper custody; production destructive operations; and promotions from `master-staging` to `master`. These retain explicit authority and separate evidence.

## Rollback

Autonomous eligibility has no direct repository mutation. A label removal, new commit, failed check, unresolved thread, or new `CHANGES_REQUESTED` review prevents or invalidates eligibility. Any actual merge remains a normal GitHub merge record into `master-staging`, and a bad landed commit is reverted by a focused follow-up PR.

## Linear Constraint

The current Linear workspace cannot create a dedicated `TER-*` record because its issue quota is exhausted. GitHub issue #274 and the proposal ledger remain the durable tracker until capacity returns. This is a tracking limitation, not a reason to bypass evidence or safety requirements.
