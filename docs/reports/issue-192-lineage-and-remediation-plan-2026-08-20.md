# Issue #192 Lineage, PR #276 Assessment, and Workflow Remediation Plan

**Assessment timestamp:** 2026-08-20
**Scope:** Original Issue #192 planning seed, delivered matrix, live PR #276, peer-review churn, Jules workflow failures, scheduled cycles, and stale-check modernization.

## Executive Position

Issue #192 began as a broad, pragmatic request: review a useful-actions catalog, implement as many Marketplace and GitHub-native workflow patterns as were beneficial, use the SWE forks as references, preserve free-tier efficiency, and especially detect empty diffs or empty commits from automated agents. The delivered program **faithfully implemented the safe and testable core** of that request while declining to equate “available action” with “approved production capability.” [1]

The next bottleneck is now operational rather than research-driven. Peer-review event fan-out and external-provider quotas create most workflow churn; an existing Jules workflow is failing without useful logs; and PR #276 introduces a writer workflow that resembles the still-gated B4 class. The correct next sequence is therefore: **stabilize the control plane, clear existing correctness debt, then decide whether to authorize any new writer or dispatch capability.**

> **Recommendation:** Do not merge PR #276 in its present form. Treat its documentation/submodule-template portion and its writer workflow as separate concerns. The workflow needs a B4-style acceptance decision and a corrected integrity contract before it can be considered.

## 1. Planning Lineage: Seed → Delivery Matrix

### Original seed

The Issue #192 seed listed 21 Marketplace or native candidates, the GitHub artifact guide, a useful-actions discovery fork, and the SWE-agent / mini-SWE-agent forks. It asked for prioritized, adaptive integration, more research, and efficient batching. Its opening note specifically requested a commit-diff watcher capable of catching empty diffs or empty commits from agents such as Jules. [1]

The issue’s early timeline also exposed the operating constraints that shaped the program: Jules created PR #193, OpenRouter reported its free-model daily quota exhausted, and a later update recorded Gemini reusable-workflow input failures as fixed by PR #269 while residual trigger hygiene remained in Issue #268. [1]

### Alignment table

| Original intent | Delivery | Extension beyond the seed | Current state |
|---|---|---|---|
| Adopt beneficial workflow patterns | B1, B2, B3, and B6 selected narrow, owned controls rather than bulk imports. | A governance ledger now requires an owner, immutable pin, minimum permission, testable trigger, rollback, and review path for every action. | Implemented on `master`. |
| Detect workflow/agent defects | Actionlint, CodeQL, workflow-surface routing, artifact verification, repo gate, Termux smoke, and the existing commit/PR diff watcher provide layered evidence. | The system now distinguishes deterministic defects, provider cooldowns, stale activity, empty diffs, and hostile inputs rather than treating every failure as equivalent. | Implemented, but baseline disposition remains. |
| Improve artifact handling | B2 established a producer/consumer contract. | SHA-256 manifest, allowlist, retention, no hidden files, and consumer verification were added—not merely upload/download steps. | Implemented and passing. |
| Explore agentic issue automation | B3 provides a read-only, cost-capped operations report. | Source/lock separation, compiler review, injection corpus, threat detection, safe-output schema, and one bounded issue output are all now explicit. | Implemented pilot; runtime evidence should be refreshed. |
| Enable helpful agent improvements | AR-04/B4 documented a controlled issue-to-PR design. | Fixed branch, allowlisted output, idempotency, provenance, hostile-input, and human-merge conditions must precede a writer implementation. | Intentionally blocked. |
| Link workflows to external capacity | B5 specified repository/service dispatch. | Typed envelope, allowlist, schema, size, replay, audit, and no-secret payload requirements are now known. | Deferred until a real service case exists. |
| Use SWE/mini-SWE references | Both forks were reviewed for CI patterns. | They informed the extensible repository-development performance suite rather than becoming unbounded production agent dependencies. | Research complete; THUB-007 remains a distinct program. |
| Continue research | X-01–X-07 broadened research beyond the original list. | Actionlint, dependency review, Scorecard, CodeQL, GitHub Agentic Workflows, starter workflows, and curated catalogs were evaluated through the same gates. | X-01–X-05 implemented/referenced as recorded; X-06–X-07 remain discovery sources. |

The delivery matrix therefore **aligns with the seed’s direction but improves its safety, observability, and reversibility**. The program did not abandon the desire for automation; it made the privilege gradient explicit.

## 2. PR #276: What the New Commits Mean

### Live state at assessment

[PR #276](https://github.com/timerloggedout-spec/termux-monorepo/pull/276), titled **“lego_fork composition template + PR sprawl isolation,”** was open against `master` with three commits, six changed files, a `CONFLICTING` merge state, and a CodeRabbit `CHANGES_REQUESTED` decision. The commits were:

| Commit | Author | Purpose |
|---|---|---|
| `3d506c9f80be` | `timerloggedout-spec` | Adds the lego fork template and PR-sprawl isolation materials. |
| `0f769b3e61fe` | `timerloggedout-spec` | Adds a one-shot workflow intended to create/update the lego fork gitlink. |
| `5396acba1137` | `github-actions[bot]` | Directly updates the gitlink on the PR branch. |

The final commit demonstrates that the newly added workflow already exercised `contents: write` and pushed to the hard-coded PR branch. This is not a default-branch push, but it is still a **workflow writer** and therefore intersects the B4 boundary.

### Why the current workflow is not ready to merge

The workflow has several problems independent of its current merge conflict and nine review findings.

| Finding | Why it matters | Required disposition |
|---|---|---|
| `contents: write` plus `git push origin HEAD:leader/lego-fork-smod-template` | A workflow writes to a branch directly, while B4 is deliberately not authorized. Hard-coding a branch reduces scope but does not supply the required provenance, test matrix, or owner acceptance. | Remove/disable the writer from this PR, or place it in a separately accepted B4 implementation with the complete tests below. |
| Manual `pin_sha` input has no strict full-SHA validation | The workflow accepts an arbitrary user-provided string. | Validate exactly 40 lowercase hexadecimal characters before network or git operations. |
| Fetch fallback to `origin main` | If the requested object fetch fails, the workflow can proceed with a different ref. | Remove fallback behavior. A pin mismatch must fail closed. |
| Pin assertion is logically weak | `SHA == PIN OR SHA == rev-parse HEAD` always permits the current checkout; the second condition does not prove the requested pin was reached. | Require `git rev-parse HEAD` to equal the validated requested SHA exactly. |
| Token and persistence surface | Checkout receives a secret-or-default token and later pushes. | Use no persisted credential for read-only preparation; only configure scoped authenticated push after validation, in an isolated writer job. |
| Missing B4 safety tests | There is no fixture evidence for no-op, wrong SHA, duplicate dispatch, stale branch, invalid path, workflow mutation attempt, token denial, or fork event. | Add the B4 test matrix before any adoption. |
| Documentation/process findings | Branch-source, `Implements:` trailer, executable gate commands, gitlink provenance, overlap claims, grammar, and Markdown numbering are incomplete. | Resolve all valid review findings in a documentation-only follow-up. |

### Recommended PR #276 split

1. **Hold PR #276** while it is conflicting and has unresolved review findings.
2. Split it into a **documentation/submodule-template PR** and a separate **B4 proposal/implementation PR**. The documentation PR can retain the `lego_fork` inventory and the PR-sprawl isolation procedure once rebased and corrected.
3. Remove or disable `ops-gitlink-lego-fork.yml` from the documentation PR. Do not allow a one-shot execution as a substitute for the B4 acceptance process.
4. If the operator explicitly accepts B4 later, implement only a fixed-purpose gitlink updater with: validated SHA, origin/reachability check, fixed branch ownership, explicit no-op result, immutable action pins, no fallback ref, constrained file allowlist (`.gitmodules`, exactly one gitlink path, exactly one inventory file), duplicate-dispatch guard, and human merge only.

## 3. Peer-Review Churn: Root Cause and Specific Remediation

### Measured churn

The latest 100 peer-orchestrator runs showed the following event profile:

| Trigger | Runs | Success | Failure | Cancelled | Diagnosis |
|---|---:|---:|---:|---:|---|
| `issue_comment` | 76 | 23 | 21 | 32 | Dominant fan-out channel. Provider comments, operator markers, and cooldown notices repeatedly re-enter the workflow. |
| `pull_request_target` | 9 | 0 | 9 | 0 | Initial cycles intentionally fail until every configured provider supplies SHA-bound evidence. |
| `pull_request_review_comment` | 12 | 0 | 1 | 11 | Individual inline comments create separate runs; concurrency causes extensive cancellation. |
| `pull_request_review` | 3 | 0 | 0 | 3 | Review events are similarly coalesced/cancelled. |

The source confirms the mechanism. It subscribes to four high-volume event classes, serializes by PR with `cancel-in-progress: false`, requires every provider in `PEER_REQUIRED_PROVIDERS` (default `coderabbit,qodo,devin`), uses a one-second wait, and exits nonzero whenever current-SHA completion evidence is absent. It deliberately comments its state, supports cooldown retries, and is designed as a required check. [2]

This is not a single bug. It is a **design mismatch between event granularity and external-provider latency/quota**. GitHub documents that a concurrency group allows one running run and, by default, only one pending run; additional pending runs are canceled and replaced. A `queue: max` setting can preserve up to 100 pending runs but would make provider churn worse here rather than better. [3]

### Concrete remediation steps

| Step | Change | Expected outcome | Safety condition |
|---:|---|---|---|
| **1** | Make the required-provider quorum an explicit reviewed policy, not an inaccessible default. Verify repository variables with an admin-capable token. Remove any provider that is not actively installed, reachable, and intended to block merging. | Stops permanent non-delivery from inactive Qodo/Devin policy entries. | Record the provider list and owner in repository docs; do not infer it from defaults. |
| **2** | Create a cycle only on `pull_request_target` for `opened`, `synchronize`, `ready_for_review`, and `reopened`. Treat provider comments/reviews as **state reconciliation signals**, not separate cycles. | One active cycle per PR SHA instead of a cycle per comment. | State must remain SHA-bound and reject stale evidence. |
| **3** | Change comment/review reconciliation concurrency to `peer-orch-reconcile-<PR>-<SHA>` with coalescing of the latest event. Do not use FIFO preservation for every bot comment. | Suppresses redundant work while preserving the final provider state. | Reconciliation is read-only except for one idempotent state update. |
| **4** | Replace `MAX_WAIT_SEC: 1` failure semantics with two explicit outcomes: `provider_pending` / `provider_cooldown` as a visible but non-required operational status, and `responses_collected` as success. | Separates provider capacity from source validation failures. | Branch-protection changes require a separate owner decision; do not silently make reviews optional. |
| **5** | Make cooldown retry exact and sparse: one retry per provider/PR/SHA after the documented retry timestamp; no generic hourly re-request. | Eliminates quota-amplifying retry loops. | Preserve an idempotent cooldown-source marker and enforce a retry budget. |
| **6** | Move provider status to a single job summary or one updatable state comment; do not emit additional review requests unless policy explicitly authorizes the provider/action tuple. | Reduces comment-trigger feedback loops. | No copied provider UI markup, cookies, tokens, browser state, or undocumented APIs. |
| **7** | Measure before promoting it as required: runs per PR SHA, provider latency, cooldown count, canceled runs, and missing-provider rate. | Turns subjective churn into a reviewable service-level decision. | Store only minimal metadata; no provider content archive is needed. |

**Target acceptance tests:** repeated bot comments on the same SHA generate at most one active reconciliation; stale SHA evidence cannot complete the new cycle; a cooldown creates no more than one eligible retry; no provider policy creates a permanent block when that provider is intentionally disabled; and a true substantive review records completion exactly once.

## 4. Jules and Agent-Review Failures

### `agent-jules-on-issues.yml`

The recent sampled runs show three failures and no successes. The latest run had no visible job list or downloadable log from the GitHub API, so the cause is not yet proven. It should be treated as **untriaged**, not as an assumed capacity failure.

The source nevertheless exposes corrective work that should be done in a minimal diagnostic PR:

1. Add workflow-scope `permissions: {}` and immutable SHA pins for `actions/github-script`, cache actions, and any Jules invocation action after supply-chain review.
2. Do not reference `secrets.JULES_API_KEY` directly in a conditional expression. Place the secret in a job environment variable and test the environment variable in the condition, following GitHub’s documented secret-handling pattern.
3. Gate label-triggered issue execution by the trusted actor who applied the label, not merely by the label text. An untrusted issue body is still data even if a trusted maintainer labels it.
4. Delimit and constrain issue/comment text passed to Jules. The external agent should receive an explicit instruction that issue body, comments, file paths, and review excerpts are untrusted reference data, never commands.
5. Add a deterministic workflow contract test for push no-op success, trusted label, untrusted labeler, authorized mention, missing API key fallback, invalid secret condition, and idempotent marker behavior.
6. Add a diagnostic summary that reports event class and the selected path without exposing issue content or secret state.

### `agent-review-auto-jules.yml`

This workflow has broader trigger/permission surface than necessary: it listens to comment creation and edits, has a concurrency key that includes each comment/review identifier, retains mutable `@v7`/`@v4` action references, and relays raw provider feedback into a Jules comment. It filters known provider controls and cooldown notices, which is good, but it still needs tighter coalescing and prompt-injection confinement.

The remediation is to trigger only on substantive creation/submission events, use a PR/SHA-based concurrency group instead of a per-comment group, reduce permissions to exactly the API methods used, pin every action, and format all provider text as untrusted data. The output should be one SHA-bound, idempotent relay per provider source revision; repeat review comments should update state rather than start fresh work.

## 5. Interval Cycles and Stale-Check Upgrades

### Current scheduled cadence

| Workflow | Current cron | Upgrade assessment |
|---|---|---|
| Continuous agent ops | `17 * * * *` | Hourly, off the top of the hour. It should not create review retries beyond its budget. |
| Read-only agentic operations report | `22 2 * * 1` | Weekly Monday. Good cadence for a low-cost advisory report. |
| CodeQL advisory | `23 3 * * 1` | Weekly Monday. Good, but results remain advisory. |
| Scorecard advisory | `41 3 * * 1` | Weekly Monday. Good, distinct from CodeQL. |
| Context relationship reconciliation | `17 6 * * 1` | Collides exactly with fork-sync audit. |
| Fork-sync audit | `17 6 * * 1` | Shift one workflow by at least 15–30 minutes. |
| Dependency phase evaluate | `23 5 * * *` | Daily cadence should have a freshness SLO and no write side effects. |

GitHub notes that scheduled workflows are best effort and may be delayed under high Actions load; schedules should therefore be treated as **eventual maintenance**, not as a time-critical merge gate. [4] The existing off-hour minute selection is good. The exact Monday `06:17` collision is not.

### Upgrade design

1. Create a **read-only workflow freshness monitor**. Run it every four hours or daily, not every minute. It should inspect the latest completion of each scheduled workflow, compare it to workflow-specific service-level objectives, and write only a job summary/artifact.
2. Use separate freshness states: `healthy`, `late`, `missed`, `disabled`, `unknown`, and `not_applicable`. Do not call a check stale merely because it was intentionally skipped.
3. Keep scheduled workflows non-required. Required checks should be tied to the PR’s current head SHA, not to a weekly baseline execution.
4. Give each schedule an owner, a cadence, an expected duration, a tolerated lateness window, a retry policy, and a rollback owner in a small `automation-slo.yaml` registry.
5. Deconflict the Monday 06:17 collision by moving fork-sync audit or context reconciliation to a different minute. This is a low-risk first upgrade.
6. Change continuous-agent-ops from a broad “advance stuck work” loop to an **action-budgeted reconciler**: maximum action count remains capped, but cooldown retry, stale nudge, and empty-diff action must each have independent per-PR/SHA idempotency keys and cooldowns.
7. Add lifecycle controls for stale checks. A stale provider review should become a visible operational state after an SLA window, then require a deliberate disposition—retry, replace provider, or remove it from the quorum—not a permanent failed check.

## 6. Phased Execution Plan

| Phase | Scope | Deliverable | Merge criterion |
|---|---|---|---|
| **0 — Contain** | PR #276 and unsafe writer path | Split/hold PR #276; remove or disable the writer workflow pending B4 acceptance. | No unreviewed direct branch writer remains in a mergeable PR. |
| **1 — Repair** | Peer orchestrator and Jules failures | One focused PR for provider quorum/coalescing, one focused PR for Jules diagnostics and immutable pins. | Deterministic fixture tests plus a measured decrease in duplicate runs. |
| **2 — Observe** | Freshness registry and review telemetry | Read-only schedule monitor, run-rate dashboard/summary, and SLO registry. | No new write permission; summary accurately distinguishes delayed, skipped, failed, and cooldown states. |
| **3 — Dispose debt** | Actionlint and stale PR portfolio | Baseline finding disposition; owner-backed classification of open PRs. | Each finding/PR has a fix, exception, rebase, supersession, or closure decision. |
| **4 — Expand deliberately** | B3 refresh, dependency-review first run, then B4/B5 decision | Controlled runtime evidence for B3 and dependency review; separate B4/B5 proposals only if a concrete use case exists. | Explicit operator acceptance, threat model, permissions review, tests, and rollback. |

## Bottom Line

The project’s evolution is coherent: the original “build useful automation” seed has become a safety-first, GitHub-native control program with tangible results. The discipline now needs to be applied to the existing high-churn agent workflows. PR #276 is the immediate proof point—its goal may be useful, but its writer mechanism must not jump ahead of the B4 safety decision.

The near-term objective is not more autonomous behavior. It is **less duplicated work, clearer provider states, bounded retries, accurate freshness signals, and smaller, rebased, reviewable PRs**.

## References

[1]: [Issue #192 initiating seed and timeline](https://github.com/timerloggedout-spec/termux-monorepo/issues/192)
[2]: [Peer review orchestrator workflow](../../.github/workflows/peer-review-orchestrator.yml)
[3]: [GitHub Actions concurrency documentation](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs)
[4]: [GitHub Actions schedule event documentation](https://docs.github.com/en/actions/reference/events-that-trigger-workflows#schedule)
[5]: [Issue #192 action decision ledger](../proposals/active/actions-refinements/ACTION-DECISION-LEDGER.md)
[6]: [PR #276](https://github.com/timerloggedout-spec/termux-monorepo/pull/276)
