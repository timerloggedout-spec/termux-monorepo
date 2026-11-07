# Issue Comment Router Fan-out Reduction — Implementation Plan

**Design:** [2026-11-05-issue-comment-router-fanout-design.md](../specs/2026-11-05-issue-comment-router-fanout-design.md)
**Proposal item:** AR-32
**Branch:** `perf/issue-comment-router-fanout-2026-11-05`
**Execution mode:** remote GitHub feature branch; no local Termux checkout is exposed in this session.

## Task 1 — Register AR-32

1. Append AR-32 to `docs/proposals/active/actions-refinements/ITEMS.md`.
2. Add this design and implementation plan.
3. Preserve the accepted proposal manifest and existing item states.

**Verification:** AR-32 appears exactly once; its path and proposal ID match the accepted manifest.

## Task 2 — RED: add route-contract regression coverage

1. Extend `scripts/ci/orchestration_contract_validator.py` with a standard-library-only validator for the router and three reusable targets.
2. Extend `tests/test_orchestration_contract_validator.py` with:
   - current repository contract test;
   - direct-subscriber regression;
   - missing reusable-call regression;
   - stale comment revision guard regression;
   - router concurrency regression.
3. The existing repo-gate already runs this validator and test file; do not modify `repo-gate.yml`.

**Expected RED:** the current router is a placeholder, the targets still directly subscribe to `issue_comment`, and the required `workflow_call` inputs do not exist.

## Task 3 — Make target workflows reusable without changing their non-comment entrypoints

Update:
- `.github/workflows/agent-review-auto-jules.yml`;
- `.github/workflows/gemini-dispatch.yml`;
- `.github/workflows/agent-jules-on-issues.yml`.

For each target:
1. Add typed `workflow_call` inputs.
2. Remove only its direct `issue_comment` trigger.
3. Preserve every other trigger.
4. Fetch the source comment by ID inside the target and validate issue/PR identity plus exact `updated_at`.
5. Preserve the target's existing trust, command, cooldown, concurrency, permission, and provider boundaries.
6. Replace direct-event payload access in the reusable path with validated step outputs.
7. Do not broaden provider allowlists or command prefixes.

## Task 4 — Implement the central router

Update `.github/workflows/issue-comment-router.yml`:
1. Subscribe to `issue_comment.created` and `issue_comment.edited`.
2. Use a per-comment-revision concurrency key with `cancel-in-progress: false`.
3. Use an immutable-pinned `actions/github-script` version.
4. Reduce router permissions to none; no checkout and no `actions: write`.
5. Classify exact trusted human commands and trusted provider bots.
6. Call the existing three target workflows with local reusable-workflow jobs and `secrets: inherit`.
7. Keep the ledger route classification-only; do not add a writer.

## Task 5 — GREEN and regression review

1. Run the native orchestration contract validator and its unittest suite in CI.
2. Confirm all non-comment event triggers remain unchanged.
3. Confirm every reusable call passes only IDs/revision metadata, not comment body text.
4. Confirm no new provider, token, secret, permission, schedule, or checkout was introduced.
5. Confirm the target workflow re-fetches and revalidates the comment revision.

## Task 6 — PR and WAIT

1. Open a draft PR to `master` with `Implements: AR-32`.
2. Inspect every check/job/log and wait for terminal results.
3. Re-fetch the immutable PR head SHA and verify repository gate + Termux smoke on that same SHA.
4. Request independent review if exposed.
5. Do not merge or claim validated until both gates are green and the route outcome is verified.

## Execution constraints

- The Termux MCP/device-info tool and local repository checkout are not exposed in this session. No device resource inspection, local worktree, or local dual-gate run is claimed.
- The GitHub remote feature branch is isolated from `master`; no local user checkout is touched.
- GitHub Actions CI is the authoritative executable validation available here.
- No provider API is invoked by this implementation session. Existing provider workflows retain their current explicit command and spend boundaries.
