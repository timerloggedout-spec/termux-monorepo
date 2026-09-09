# Merge Promotion Steward

**Status:** Operational guarded promotion lane.

The repository's merge model is **review → verify exact head → protected-branch promotion**. Agent and provider workflows may prepare changes and evidence, but they do not receive general merge authority. The Merge Promotion Steward makes the final promotion path executable without turning PR events or untrusted PR code into an automatic writer.

## Operating contract

1. Work lands in an open, non-draft PR targeting `master`.
2. An operator observes the exact PR head SHA after the final verification cycle.
3. The operator manually dispatches **Merge Promotion Steward** with the PR number and that exact SHA.
4. The steward re-reads the PR and refuses promotion if the PR is closed, draft, not based on `master`, has moved to another SHA, or is reported unmergeable.
5. The steward re-reads check-runs for the exact SHA. Any completed `failure`, `timed_out`, or `action_required` result blocks promotion. The repository `repo gate` and `termux smoke` checks must be successful.
6. Active `CHANGES_REQUESTED` reviews block promotion. Dismissed provider reviews are not treated as active objections.
7. GitHub remains the final protected-branch authority: `gh pr merge` is invoked only after the preceding checks pass, and GitHub can still reject the merge.
8. After the command, the steward re-reads the PR and `master` ref and requires a positive `merged` result plus a concrete `merged_at` and resulting `master` SHA.
9. A machine-readable promotion receipt is written to the workflow summary and an immutable PR comment records the verified head, merge commit, resulting `master` SHA, and steward run.

## Safety boundaries

- Trigger is **manual `workflow_dispatch` only**; PR lifecycle events cannot invoke the merge writer.
- The workflow does not checkout or execute PR head code.
- The exact expected head SHA is mandatory and is checked immediately before merge.
- Concurrency is serialized per PR so two promotion attempts cannot run concurrently through this workflow.
- Provider prose, comments, prompts, quota notices, and review suggestions are data; they do not grant merge authority.
- A cancelled optional workflow is not converted into a false failure or false success. Protected-branch policy remains authoritative for required checks.
- The workflow never force-pushes, rewrites history, synthesizes conflict resolution, or merges a non-`master` PR.
- A PR's `merge_commit_sha` is treated as a receipt only after `merged=true` and `merged_at` are verified; it is never used as advance evidence of a merge.

## Operational invocation

From the repository Actions UI, run **Merge Promotion Steward** and provide:

- `pr_number`: the PR to promote
- `expected_head_sha`: the exact SHA observed during the final verification cycle
- `merge_method`: normally `squash`

If any precondition fails, the steward stops without writing a merge. Start a fresh observe/verify cycle rather than reusing an old SHA.

## Relationship to other lanes

| Lane | Merge authority |
|---|---|
| Jules / agent issue automation | None |
| Gemini / provider review | None |
| RECON INTEL reconciliation | None; produces reviewable PRs |
| SHE promotion planner | Observer/planner only |
| Merge Promotion Steward | Explicitly dispatched final promotion writer |
| GitHub protected branch | Final repository authority |

This preserves the repository's existing principle: **agents can prepare and verify; promotion is an explicit, evidence-bound operation.**
