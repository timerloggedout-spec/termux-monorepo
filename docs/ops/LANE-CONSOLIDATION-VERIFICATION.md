# Lane consolidation: verification contract

Implements: RL-20. Companion to PR #1239, not a replacement for the generated lane board or LANE-MATRIX policy.

## Scope and outcome

The original PR changes two context collectors and one cockpit test. It does not change model budgets, workflow cadence, provider admission, database migrations, or routing. The verified product outcome is validation of untrusted paths before an optional ast-grep fallback, with parity across both collector copies; cockpit root-name tolerance is a separate existing test change.

`tests/test_context_collector_lane_parity.py` uses only unittest, temporary directories, and mocked optional-tool probes. It checks traversal, absolute paths, backslashes, direct symlinks, parent-symlink escape, and read-only fallback when ast-grep is absent. It imports both source files directly rather than relying on ambiguous module search paths.

Run: `python -B -m unittest discover -s tests -p test_context_collector_lane_parity.py -v`. The four test methods passed on the original candidate plus the new regression file; the same suite produced five failing subtests against master 8f1a56eb5242e2b1055d61d9c2d8a4ffea08db8d. This distinguishes a real regression guard from a test that merely echoes the patch.

## Historical timing claims are not current configuration

The September 20 LANE_CONSOLIDATION_SSOT and MERGED-BRANCH-AUDIT reports are historical records. Do not treat checked boxes, approval prose, or a newer document date as runtime verification. Inspect source on the candidate SHA.

| Setting | Historical SSOT | Observed source at master 8f1a56eb and original PR head 0182ca4f |
|---|---|---|
| Continuous ops schedule | Every two hours, 17 */2 * * * | Hourly, 17 * * * * |
| Sweep debounce | 90 minutes | debounceMs = 45 minutes |
| Stale threshold | 3 hours | staleMs = 2 hours |
| Peer wait budget | 480 seconds | MAX_WAIT_SEC = 1 |
| Sweep capacity | Default 8, cap 20 | Default 8, cap 20; matching |

Sources: `.github/workflows/agent-continuous-ops.yml`, `.github/workflows/peer-review-orchestrator.yml`. The new contract records discrepancies; it does not reset workflow settings to historical values. Model/provider quota availability remains unverified without live catalog and provider evidence.

## Branch folding decision rules

1. Resolve branch heads from Git refs, not a capped connector page. Exclude symbolic origin/HEAD.
2. Record the exact master SHA, head SHA, and `git rev-list --left-right --count master...head` result.
3. Ahead=0 means the branch tip is reachable from master, not permission to delete it. Divergence alone does not establish a conflict or missing functionality.
4. Compare scoped diffs and patch equivalence before extracting. Do not fold timestamp-only report refreshes, generated catalog feeds, unrelated privilege changes, or long-lived dashboard histories into a context-collector fix.
5. Preserve separate dashboard/evaluation/connector lanes and their review bases. Do not wholesale merge master-staging or dashboard-lanes-v2.
6. Keep inventory snapshots outside this durable contract; the generated lane board remains the operational board. No pulse PR or issue #175 recon comment is needed.

## Connector evidence boundaries

On October 19, 2026, the connected Supabase list_projects action returned an empty projects array. This is a visibility/association blocker, not proof that production has no database. No database branch, migration, health, RLS, or production-readiness claim follows from that response. Do not create a project or paid branch to fill the evidence gap.

Linear title searches for lanes, consolidation, and PR 1239 returned no matches before the RL-20 follow-up was submitted. Historic production automation issue TER-18 concerns August 3, not this candidate. Connector connection alone is not integration validation. GitHub remains authoritative for commits, PR state, and named CI jobs.

## Promotion contract

Require named hygiene + portability gate and agentic termux smoke success on the final head SHA, local parity, a verified task outcome, and a non-conflicting merge state. Combined check summaries do not substitute for named jobs. Original-head evidence expires after every new commit.

Historical original-head evidence at 0182ca4f1f21212f309b7f0ea66cf6e1c88e0fbe:
- repo gate: https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39074426373
- termux smoke: https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39074426357

Both local gate scripts passed in a sparse Debian checkout of the original candidate. This is not Android device validation. The existing pytest-based context/cockpit suites were not executed locally because pytest was unavailable; the added stdlib suite was executed. New documentation/test commits must obtain fresh hosted gate evidence before production promotion.
