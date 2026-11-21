# Post-merge remediation checkpoint — 2026-11-02

**Repository:** `timerloggedout-spec/termux-monorepo`  
**Canonical branch:** `master`  
**Merged remediation:** [PR #3815](https://github.com/timerloggedout-spec/termux-monorepo/pull/3815)  
**Merge commit:** `da4eae4a06617430bbd7b53695c79b748ffafa8b`

## Reconciliation

This checkpoint supersedes no historical evidence. It records a follow-up inspection after PR #3815 merged.

| Surface | Observed state | Consequence |
| --- | --- | --- |
| Backfill workflow | Resolves `git rev-parse HEAD` once; exports it as `GITHUB_SHA` and `EXPECTED_SOURCE_SHA`; requires the builder receipt's `source_sha` to match; validator receives the same expected SHA | Deterministic source identity is now represented in the workflow. Runtime validation is still required. |
| Canonical manifest | Blob `bcd13129b3ebd283df920ae18cf1426fb0d8ba85`; 35,221 nodes; 57,358 edges; next page 2; `PARTIAL_CONTINUATION_REQUIRED`; checkpoint eligibility false | No evidence of corpus advancement. |
| Backfill Actions execution | Commit-associated workflow lookup returned no PR-triggered runs for the merge commit | This lookup cannot establish a successful post-merge run. Do not claim the new guard has passed CI. |
| Quota dispatcher | Still computes repo-wide queued + in-progress count and applies `busy >= 6` as the broad admission pause | Lane-aware admission remains an open control-plane issue. |
| ATES emitter | Main job remains gated on `workflow_run.conclusion == 'success'` | Failure/cancellation/other outcomes lack equivalent main-path receipts. |

## Remaining work

### P0 — prove backfill execution

- Obtain an Actions dispatch for the merged workflow using a supported, authorized dispatch surface.
- Use the manifest's canonical continuation page; do not force a page number that disagrees with the manifest.
- Require a non-deferred builder receipt, exact repository/ref/source-SHA identity, fresh output, validator success, and an observable manifest change before describing the run as productive.
- Keep checkpoint eligibility false unless its independent criteria pass.

### P0 — lane-aware dispatcher admission

- Separate global queue safety from per-lane pressure. Count only relevant workflow/lane runs for ordinary admission.
- Retain a hard global cap; never add a recovery exception that can create unbounded fan-out.
- Define a bounded critical-lane recovery rule with per-lane concurrency and explicit age/eligibility conditions.
- Emit machine-readable `paused_reason`, measured counts, affected lanes, override state, and dispatch outcomes.
- Add deterministic tests for empty backlog, unrelated backlog, target-lane backlog, hard global cap, stale critical lane, and explicit force.

### P1 — ATES outcome coverage

- Inventory the allowlisted source workflows and their completed outcomes.
- Represent success, failure, cancellation, skipped/deferred/rate-limited, and unmapped cases with honest status receipts or explicit documented exclusions.
- Preserve source run ID, attempt, head SHA, workflow identity, and deduplication key.
- Keep provider/model, task boundary, and complexity unknown when evidence is absent; never synthesize values.
- Keep ATES observational-only, not a speed-based merge gate.

### P1 — corpus quality triage

The latest canonical manifest still reports 120 unresolved internal references, 4,942 candidate edges, 12 parser failures, and 1,392 excluded source files. Triage must retain per-item provenance and explicit dispositions; aggregate counts alone are not resolution.

## Execution boundary

The GitHub connector available in this session exposed repository/file/PR operations and workflow run inspection, but no workflow-dispatch operation. Therefore no Actions dispatch was attempted here. This is a tool-capability limitation, not a claim that GitHub Actions itself cannot dispatch the workflow.

## Acceptance definition

A task is closed only when the relevant code change is merged, tests pass in CI, runtime evidence is attached, and the observed state satisfies its own acceptance criteria. A merged patch, a green no-op, or a larger graph is not sufficient evidence by itself.
