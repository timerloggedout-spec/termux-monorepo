# Linear Adapter Protocol

**Status:** optional integration; degraded availability recorded 2026-11-19.

Linear is an execution-state mirror when its API is available. Repository scope, priority, and acceptance evidence remain governed by `CLAUDE.md`, `docs/proposals/registry.yaml`, active proposal `ITEMS.md` files, GitHub, and the repository gates.

## Authority and priority

1. Platform safety and explicit operator direction.
2. Current user objective and repository entry point: `CLAUDE.md`.
3. Active proposal and item scope.
4. GitHub branch, commit, pull request, review, and check evidence.
5. Linear issue metadata and status, when reachable.

Adaptive Dynamic Awareness selects the next action from current priority, risk, dependencies, blockers, freshness, and the ability to verify progress. Linear availability is one input to routing, not a repository-wide admission condition.

## Healthy integration path

When Linear is reachable and a matching issue exists:

- Reuse the existing `TER-*` issue.
- Keep its state aligned with actual work.
- Link the proposal item, branch, commit, and pull request.
- Mark completion only after the corresponding repository evidence exists.

Create an issue only when the integration accepts writes and no existing issue covers the work. Preserve the repository item as the durable scope record.

## Degraded or unavailable path

When Linear search, issue creation, or updates fail:

1. Continue from the accepted repository proposal and its `ITEMS.md` scope.
2. Record the failure mode, date, and evidence in `docs/ops/INTEGRATION-DRIFT-2026-11-19.md`.
3. Use GitHub branches, commits, pull requests, reviews, and checks for execution evidence.
4. Keep proposal status and item status synchronized with verified repository state.
5. Mark Linear synchronization as pending; reconcile metadata when the integration becomes healthy.

A missing `TER-*` issue, workspace issue cap, API outage, or stale Linear record does not invalidate an already accepted repository scope. Agents must not fabricate issue identifiers or report synchronization that has not been verified.

## Branch model

```
feature/* ──PR──► master-staging ──focused promotion──► master
```

- `master-staging` is the permanent integration spine.
- A pull request targets `master-staging`.
- Promotion to `master` remains selective and reviewable.
- Repository gates and required reviews govern merge readiness.

## Evidence contract

Every material state claim names its evidence: proposal item, branch, commit, pull request, workflow run, or test result. Linear URLs and identifiers supplement that evidence. External tracker state never substitutes for repository verification.
