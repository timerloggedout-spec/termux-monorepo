# Linear Triage backlog — reconciliation findings (TER-15)

Status: investigation complete for a representative sample; systemic fix recommended below.
Scope: item 3 and item 5 of the TER-15 "Linear Integration" round. This is a reconciliation
record, not a new backlog of work — per the round's own direction, the goal was to fold lessons
back into what already exists, not spawn a wave of new issues/PRs.

## 1. What was actually in "336+ issues stuck in Triage"

A sample of the 50 most-recently-updated Triage-state issues in the `Termux-monorepo_linear`
team (`TER-`) was pulled directly from Linear (`linear_search_issues`, `state_id` = Triage).
Every single issue in that sample was one of two shapes:

- `PR #<N> agent feedback rollup` — a parent issue
- `[coderabbitai[bot]] PR #<N>: <file or "review feedback">` — a child issue under that parent

Both shapes are created automatically by `.github/workflows/agent-feedback-linear-sync.yml`
(confirmed in its source and in `sec(workflows): gracefully catch USAGE_LIMIT_EXCEEDED errors
in sync-linear`, commit `1f94692f`). The workflow creates one rollup issue per PR plus one child
issue per CodeRabbit/Devin review comment on that PR. **None of the sampled issues were
independent feature requests or bugs** — they are a byproduct of review-comment bookkeeping,
and nothing in the pipeline ever transitions them out of Triage once the PR is resolved.

### Sample evidence: merge status of the PRs behind these issues

| PR | State | Merged |
|----|-------|--------|
| #593 | closed | yes |
| #588 | closed | yes |
| #581 | closed | yes |
| #578 | open | no |
| #575 | closed | yes |
| #550 | closed | **no** (abandoned) |
| #545 | closed | yes |
| #537 | closed | yes |
| #525 | closed | yes |
| #523 | open | no |
| #509 | closed | yes |
| #508 | closed | yes |
| #500 | open | no |
| #499 | closed | yes |
| #493 | closed | yes |
| #491 | closed | yes |
| #485 | closed | yes |

13 of 17 sampled PRs (76%) are already merged. For a merged PR, the review feedback it generated
is resolved by definition (addressed pre-merge, or accepted as-is at merge time) — the rollup +
child issues sitting in Triage for a merged PR are stale tracking noise, not open work. Extrapolated
across the full 336+ issue set (dominated by the same two title shapes going back through PR
history), the large majority of "stuck in Triage" is very likely this same pattern rather than a
genuine backlog of unaddressed items.

### What was folded back (not a new PR wave)

As a concrete instance of the fix (not an attempt to process all 336+ by hand in one pass):
`TER-333` (PR #588 rollup), `TER-334`, `TER-335` (its two CodeRabbit subtasks) were each given an
explanatory comment citing the merged PR as evidence, then moved from Triage to Done. This is the
reconciliation pattern to repeat: **evidence (PR merged) → comment → Done**, not "close on
suspicion" (per `termux-monorepo-agentic-governance`'s evidence-led triage rule).

PRs #578, #523, #500 are still open — their rollup/subtask issues are correctly left in Triage;
they are not stale.

### Recommended systemic fix (not implemented this round — needs its own scoped PR)

`agent-feedback-linear-sync.yml` (and/or a small scheduled job) should watch for the parent PR's
`closed`/`merged` webhook event and auto-transition the rollup + its subtasks to **Done** (merged)
or **Canceled** (closed unmerged) at that point, instead of leaving them in Triage forever. This
would have prevented the majority of this backlog from accumulating in the first place, and is a
natural companion to the `context-relationship-linear-freshness.yml` automatic-trigger fix landed
alongside this doc. Filing as a follow-up rather than doing it inline here, to keep this round's
diff reviewable.

## 2. Linear API quota / availability (item 5)

**Finding: this is a real, ongoing constraint — the workspace's free-plan issue-count cap — not
a transient blip, and not a request-rate throttle.**

Evidence:

1. Two independent prior incidents already documented this in-repo:
   - `docs/ops/SYNC_AUDIT_REPORT.md`: *"A new Linear issue ... could not be created because the
     connected workspace rejected it at its free issue limit."*
   - `docs/reviews/linguist-177/PUBLICATION-RECORD.md`: *"Creation of a dedicated Linear issue
     was attempted, but the workspace returned an explicit free-issue-limit error."*
   - `agent-feedback-linear-sync.yml` itself was patched (`1f94692f`) specifically to catch
     `USAGE_LIMIT_EXCEEDED` from Linear and degrade gracefully instead of failing the workflow.
2. Reproduced live during this investigation: a throwaway probe issue creation
   (`linear_create_issue`) against the `Termux-monorepo_linear` team failed outright just now.
3. By contrast, **reads and updates on existing issues worked without any error** during this
   same session — issue search/get, status transitions (TER-14, TER-15, TER-333/334/335), and
   comments all succeeded immediately and returned current data (`updated_at` timestamps matched
   the actions just taken).

Conclusion: the constraint is specifically on **creating new issues** (Linear's workspace-level
free-plan issue cap), not on the GraphQL API's request rate and not on reads. This means:

- `archwiz/linear_sync.py` and `archwiz/linear_client.py`'s read paths (`get_issue`,
  `find_issue_by_identifier`, status checks) are **not** operating on stale data — the sync
  script's understanding of existing issue state is current, not throttle-lagged.
- The actual risk is any workflow that tries to **create** new Linear issues (new feature
  rollups, new subtasks) will keep failing until either the workspace is upgraded off the free
  plan or issue volume is brought down (which is exactly what the Triage cleanup above starts
  to address — every rollup/subtask issue closed frees capacity for real new tracked work).

No further code change is needed for the sync script itself; the existing `USAGE_LIMIT_EXCEEDED`
catch-and-warn behavior in `agent-feedback-linear-sync.yml` is the correct degrade-gracefully
posture given this is a plan limit, not a bug. The durable fix is workspace capacity (an Operator
/ billing decision, out of scope for an agent) plus reducing issue churn per the recommendation
in §1.