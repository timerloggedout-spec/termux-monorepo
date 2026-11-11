# QDesk Observatory / Delphi / DoE — Status, Findings and Execution Plan

**Status date:** 2026-11-11 UTC  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Decision:** Continue bounded repair; do not bypass failed quality gates.  
**Status vocabulary:** DESIGNED → COMMITTED → EXECUTED → VALIDATED → PROMOTED are separate evidence states.

## 1. Executive status

The QDesk proposal and quota renderer repair have commits and open pull requests, but the previously observed CI cohorts were not green. This document records the exact evidence baseline and the repairs made in this pass. The new commits require fresh current-head checks before either PR can be merged.

| Workstream | PR / issue | Last observed head | Last observed result | Current action |
|---|---|---|---|---|
| QDesk Observatory / Delphi / DoE RFP | [PR #5145](https://github.com/timerloggedout-spec/termux-monorepo/pull/5145) | `4c1c1c3975b3cdde7406623b2525464e6bf2ce0f` | Open; mergeable metadata, but repo gate failed; Vercel tribute-dash and tribute-oversight status failures; eight unresolved CodeRabbit threads | Added acceptance gates QD-033–040, corrected parked lifecycle and Delphi/quota contracts, repaired a workflow YAML structural fault; re-run required |
| Quota Usage renderer | [PR #5149](https://github.com/timerloggedout-spec/termux-monorepo/pull/5149) | `74de57e3e892c3079c2465f0e46f7e1c34c7ac66` | Open; renderer regression work present; quota-analysis failed 2 assertions; repo gate and dangling-reference check failed | Corrected two stale test expectations and linked the page-specific test to the quota workflow; re-run required |
| Quota Usage defect | [Issue #5148](https://github.com/timerloggedout-spec/termux-monorepo/issues/5148) | N/A | Renderer dereferenced optional `states` map | Patch is in PR #5149; not merged |
| Dispatch liveness recovery | [Issue #5132](https://github.com/timerloggedout-spec/termux-monorepo/issues/5132) / [#5142](https://github.com/timerloggedout-spec/termux-monorepo/issues/5142) | N/A | Prior attempts include empty successful outputs and real builder failures; do not treat success status as proof of effect | Separate recovery lane; retain no-unchanged-retry instruction |

## 2. Current-head changes made in this pass

### 2.1 QDesk proposal branch

Branch: `qdesk-observatory-delphi-doe-rfp`

Changes committed:
- Expanded RFP idempotency from request/RFP to campaign and work-packet identity.
- Clarified active sweep plus guaranteed post-burst sweep semantics.
- Required full pagination of open `delphi:rfp` issues, not just the first 100.
- Required review approval to bind to a canonical hash of the complete proposal package, including architecture and acceptance criteria; any content change invalidates the prior disposition.
- Required incumbent preservation even after a successful candidate improvement.
- Made unknown/stale/incomplete/exhausted quota a provider-admission denial, including for nominally free providers.
- Corrected lifecycle: `DELPHI_PARKED` returns only to gate re-evaluation and cannot create designs, campaigns, work packets or provider calls.
- Added bounded feed-divergence semantics: visible STALE/INCOMPLETE during a declared propagation window, alert outside it, exact parity after recovery.
- Added acceptance tests QD-033 through QD-040.
- Repaired `.github/workflows/ios-termux-contribute.yml`: a colon-bearing shell command was authored as a plain YAML scalar (`run: echo "Existing PR: ..."`), which is invalid YAML because the colon-space occurs in a plain scalar. It is now a block scalar. This was the cause of the repo-gate ratchet finding `invalid_control_plane_yaml: 0 → 1` on the previously observed PR merge tree.

### 2.2 Quota Usage branch

Branch: `fix/quota-usage-missing-states-20261110`

Changes committed:
- Renderer normalizes absent, null or non-object snapshot `states` to an empty map and emits explicit `no reading`; it never zero-fills or invents status.
- Snapshot contract test accepts the optional map while validating any present service states.
- Node regression fixture covers missing and null maps.
- `tests/test_quota_usage_page.py` is included in `.github/workflows/quota-analysis.yml`.
- Corrected the corpus test to compare the October-only pack dates with the October reconstructed corpus. The pack intentionally retains historical August/September and November 1 observations; the corpus fixture contains 30 October daily files, hence 29 consecutive deltas. Comparing 29 deltas with all 37 pack dates was a stale test assumption.
- Corrected the sitemap assertion to the current canonical URL `https://timerloggedout-spec.github.io/tribute/quota-usage.html`; the test had asserted a stale `/help-wanted/` path.

## 3. CI evidence and failure diagnosis

### 3.1 QDesk PR #5145 — prior observed head

At `4c1c1c3975b3cdde7406623b2525464e6bf2ce0f`:
- Success: Lane matrix event-driven inventory, termux smoke, PR evidence evaluation, Gemini dispatch, Jules handoff, repository development evaluation, PR scope guard, Action Effectiveness Ledger, PR production ledger, Peer review orchestrator, Sweep Accountability.
- Failure: repo gate / hygiene + portability gate. The ratchet reported `invalid_control_plane_yaml` increasing 0 → 1 and identified `.github/workflows/ios-termux-contribute.yml`. The invalid plain scalar is corrected in this branch.
- Failure: Vercel status contexts `Vercel – tribute-dash` and `Vercel – tribute-oversight`. Root cause is not established in the retrieved evidence; do not label this a code failure or a rate-limit failure without provider logs.
- Neutral: CodeRabbit check. The eight inline findings are substantive and are addressed in the RFP and acceptance contract; a neutral check is not a successful independent review.
- Cancelled: DeepSeek CI, Context Relationship + Lead/Lag Audit, Audit Cycle, CellCog review and other optional lanes. Cancellation is preserved as cancellation, not green.
- Multiple dispatch check-runs were still queued at observation time; queued is not execution completion.

### 3.2 Quota PR #5149 — prior observed head

At `74de57e3e892c3079c2465f0e46f7e1c34c7ac66`:
- Success: verify, contracts, termux smoke, advisory CodeQL, Actions lint, provider batch production contracts, workflow surface evidence/policy, repository development evaluation and several ledger/review orchestration jobs.
- Failure: quota-analysis. 142 tests passed and 15 subtests passed; two existing assertions failed:
  1. October corpus delta count was 29, while the test compared it to 37 total pack days spanning several periods.
  2. Sitemap test expected `/help-wanted/quota-usage.html`, while the canonical current URL is under `/tribute/`.
- Failure: repo gate / hygiene + portability due the same workflow YAML defect described above.
- Failure: ArchWiz dangling-reference census reported 79 observations (65 new, 14 known), including dynamic JavaScript URL templates and missing path-filter/script references. This is a repository-wide inventory warning; each finding must be verified before changing or suppressing it. Do not blanket-ignore dynamic references or rewrite unrelated dashboard links as part of the quota fix.
- Neutral: CodeRabbit was rate-limited; the provider's comment explicitly says the review was not completed. Devin Review and other completed checks do not substitute for that missing provider review.

## 4. Review findings disposition

Eight inline CodeRabbit findings on #5145 were verified against the current RFP contract and translated into explicit requirements:

| Finding | Disposition | Acceptance |
|---|---|---|
| Campaign/work-packet idempotency | Accepted | QD-033 |
| Active sweep plus post-burst sweep | Accepted | QD-034 |
| Retain incumbent after improvement | Accepted | QD-035 |
| Bound feed delta and require recovery parity | Accepted | QD-036 |
| Deny provider call on stale/unknown quota | Accepted | QD-037 |
| Paginate Delphi issue census beyond 100 | Accepted; implementation prerequisite | QD-038 |
| Bind review to complete proposal content hash | Accepted; implementation prerequisite | QD-039 |
| Parked RFP must re-enter gate before design | Accepted | QD-040 |

The two heavy-lift findings (pagination and complete-content review binding) are now explicit mandatory implementation requirements. They are not represented as already implemented. The QDesk PR remains a proposal packet until the gate adapter, pagination, hash-binding and fixture work are actually built and independently validated.

## 5. Execution plan

### P0 — unblock current PR quality evidence
1. Confirm current branch heads and master ancestry.
2. Re-run the repo gate after the YAML correction.
3. Re-run the full quota-analysis workflow after the test corrections.
4. Verify the renderer regression test itself runs in CI and exercises both missing and null maps.
5. Re-run dangling-reference census and classify each new finding; do not suppress unverified findings.
6. Inspect Vercel provider failure details and retry only after identifying a transient provider failure or a changed input.

### P1 — close QDesk review and integration gaps
1. Implement Delphi issue pagination with bounded pagination and stable de-duplication; test more than 100 open RFP issues.
2. Implement canonical full-package hash binding for review disposition; reject stale awards after any content change.
3. Extend idempotency fixtures through campaign and work-packet creation.
4. Test the active-sweep/post-burst race and cancellation path.
5. Add incumbent-retention and bounded feed-recovery fixtures.
6. Add provider admission spy tests proving no call occurs under unknown/stale/exhausted quota.
7. Reconcile the signed Delphi ledger and ensure parked requests only re-enter through gate re-evaluation.

### P2 — finish Observatory and evolution integration
1. Map each canonical feed, mirror, producer, consumer and refresh cadence.
2. Add per-block freshness and source provenance; do not infer from page-shell timestamps.
3. Join Gantt dependency phases, QUE priorities, quota reservations and opportunity windows without collapsing their dimensions.
4. Connect HindSight/ICM context with provenance and permission-aware retrieval.
5. Add DoE generator golden tests, deterministic seed replay, SRM checks and independent verification.
6. Run shadow-only pilot; retain negative results and incumbent lineage.

## 6. Promotion and merge policy

A PR is merge-eligible only when all of the following are true on its exact current head:
- Required repository gates pass, including repo gate, hygiene/portability and relevant test workflows.
- Required tests pass with exit code 0 and the exact changed files are included in the test path.
- No unresolved critical/major review findings remain without a documented, evidence-backed disposition.
- Required independent review is complete; provider cooldown or neutral status is not a review.
- The base/head relationship is current and the merge method is compatible with repository policy.
- Post-merge verification is planned and the resulting master SHA will be re-fetched and checked.

No check is marked successful because it was queued, cancelled, neutral, skipped or unavailable. No production or paid provider action follows merely from a Delphi award or PR merge.

## 7. State ledger

| Item | State |
|---|---|
| QDesk RFP + design + feed RECON | COMMITTED |
| QDesk review-driven RFP/acceptance refinements | COMMITTED; current-head checks pending |
| Quota renderer fix + regression test | COMMITTED; current-head checks pending |
| Quota test battery integration | COMMITTED; current-head checks pending |
| Delphi pagination implementation | NOT_STARTED |
| Full proposal hash-binding implementation | NOT_STARTED |
| QDesk integrated worker / pool generator | PROPOSED; not implemented by this RFP |
| Quota PR merge | BLOCKED pending fresh checks |
| QDesk PR merge | BLOCKED pending fresh checks and independent review |
| Production promotion | NOT AUTHORIZED by this document |

## 8. Operator decision record

The user explicitly directed: “DO && commit && get everything FIX && Merge Now.” This authorizes implementation, commits and merges when objective repository gates are met. It does not authorize bypassing failing checks, fabricating provider review, hiding failed/cancelled workflows, paid spend, secret changes, or production deployment. Any merge blocked by branch protection remains blocked and is reported with the exact failing gate and remediation.
