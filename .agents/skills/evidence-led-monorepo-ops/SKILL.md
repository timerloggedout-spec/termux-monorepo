---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin operations for timerloggedout-spec/termux-monorepo. Reconstruct current state, bind actions to immutable SHAs, preserve provenance, and never confuse activity with verified outcome.
---

# Evidence-Led Monorepo Operations

Load this skill for every repository-admin session.

## Operating contract

RECON -> CLASSIFY -> PLAN -> ACT -> WAIT -> VALIDATE -> RE-FETCH -> RECORD -> REPEAT

The goal is a verified repository outcome, not a green-looking activity stream.

## 1. Reconstruct current state

Before a consequential action, resolve:

- live master SHA;
- target branch/ref and immutable head SHA;
- merge-base and ahead/behind relationship;
- changed paths;
- open PR/issue context;
- current workflow runs, jobs, steps, artifacts, reviews, and comments relevant to the current SHA;
- applicable skill, governance, lane, and proposal SSOTs.

Prefer exact file, symbol, PR, issue, label, scope, or permalink roots. Keep verified relationships separate from heuristic candidates.

## 2. Evidence hierarchy

Prefer evidence in this order:

1. current-SHA repository diff and contracts;
2. current-SHA validation/test results;
3. current-SHA workflow/job/step/artifact evidence;
4. substantive current-SHA review findings;
5. provenance and task/issue lineage;
6. historical evidence from superseded SHAs;
7. size, age, comment count, or activity volume as **context only** (not promote blockers).

A workflow success proves that workflow result. It does not prove the requested task outcome.

## 3. Evidence identity

Every material observation should bind, where available, to repository/ref; immutable commit SHA; base SHA/merge-base; workflow/run/attempt/job/step IDs; artifact or receipt IDs; review/comment IDs; observed/event timestamps; agent/provider/model identity with confidence; experiment/cohort ID when applicable; status/outcome; provenance/confidence; and superseded predecessor.

Never infer missing IDs, timestamps, counts, authorship, or causal relationships.

## 4. State classification

Keep these states distinct:

PASS | FAIL | UNKNOWN | WARNING | SKIPPED | STALLED

Apply them separately to dispatch, execution, provider availability, quota/capacity, correctness, tests, integration, review, deployment, and task outcome.

A provider outage, rate limit, skipped reviewer, stale branch, and correctness failure are different observations.

## 5. Adaptive WAIT integration

During asynchronous work, use .agents/skills/adaptive-wait/SKILL.md.

- Re-fetch immediately after material commits, reruns, steering, or newly reported failures.
- Back off only when authoritative state is live and repeated observations show no material delta.
- Retry only when the next attempt differs for an evidence-backed reason.
- Continue disjoint work while useful evidence is accumulating.
- Stop on authoritative terminal state, stagnation, or a missing authority/input.
- Bind conclusions to the SHA that produced the evidence.

HOLD and OBSERVE are not idle parking states. WAIT collects evidence until promote conditions hold, then promote.

## 6. Change discipline

For repository mutations:

1. identify a change that advances the requested outcome (slice **or** mega — both valid);
2. re-read the current file/ref before writing;
3. make the change;
4. run the smallest relevant deterministic validation;
5. commit with a specific message;
6. re-fetch the resulting SHA and checks;
7. preserve failed attempts and superseded evidence.

Never force-push, reset, delete evidence, or silently overwrite another active state.

## 7. Promotion

Promotion requires current-SHA evidence for base alignment/reconciliation; relevant tests and invariants; review/finding disposition; integration/task outcome; and repository-defined dual gates.

COMMITTED, EXECUTED, VALIDATED, and PROMOTED are independent states.

Do not promote because a branch is old, a PR is green on an older SHA, a reviewer is silent, or a provider returned HTTP 200.

Repository dual-gate: hygiene/portability + agentic termux smoke. Vercel is non-gate (#772). Copilot / CodeRabbit / Devin are advisory only.

**Mega-merge policy (Operator 2026-09-24):** Mega-merge is **allowed** when dual-gate SUCCESS + mergeable on the candidate SHA. Collaborators hold large context windows. CodeRabbit’s ~100-file limit is **advisory review capacity**, not a hard promote ban. File count alone must not refuse a dual-gate-green PR. `mergeable_state=dirty` or merge conflict remains a hard block until rebased.

## 8. Historical continuity

Historical collection is bounded and resumable. Record page/window bounds, continuation state, collection timestamp, source/ref, parser/API failures, exclusions, and coverage. Never call a partial page complete history.

A failed or superseded attempt remains evidence. Correct forward with a successor change.

## 9. Write boundaries

Read-only reconnaissance may inspect repository/GitHub state. Mutating operations require the applicable explicit authorization and governance tier.

Never persist secrets, authorization headers, tokens, browser/session stores, private discussion bodies, or generated credentials in the repository. Issue #184 is names-only.

## 10. Closeout receipt

Use a compact receipt shape:

    operation: <bounded operation>
    repo: <owner/name>
    base_sha: <sha>
    head_sha: <sha>
    observed_at: <UTC>
    evidence:
      checks: [<ids>]
      runs: [<ids>]
      reviews: [<ids>]
      artifacts: [<ids>]
    state: PASS|FAIL|UNKNOWN|WARNING|SKIPPED|STALLED
    outcome: PASS|FAIL|UNKNOWN
    provenance: <source/actor confidence>
    decision: KEEP|RETRY|STEER|HOLD|PROMOTE|STOP
    reason: <evidence-backed reason>
    remaining: <unproven work>

Receipts are projections; the longitudinal GitHub/evidence corpus remains the source of historical truth.

## Related operational skills

- adaptive-wait — asynchronous control and cadence;
- adaptive-feedback-cycle — continuous feedback and historical evaluation;
- review-loop — review ingestion and repeated validation;
- context-relationship-graph — metadata-only relationship evidence;
- production-reconciliation — ref/base reconciliation;
- action-effectiveness-ledger — action-to-outcome measurement;
- evidence-envelope / evidence-provenance — normalized provenance;
- workflow-orchestration — modular Actions coordination;
- evolutionary-replay — bounded replay of realized discovery history.

This skill owns repository-admin evidence discipline; it does not replace those specialist lanes.

## Session 2026-09-28 17:15 PDT

- Live master tip: `8daeeb72d71ecdefa2f9cde6698426131117e474` (catalog/mmdc bot refresh after #904).
- Dual-gate PASS on that SHA: repo-gate 36497249095 + termux-smoke 36497249115.
- #904 squash `4efef68d` dual-gate PASS on master: 36497147812 / 36497147650.
- Candidate evidence for #904 pre-merge: repo-gate 36497057302 + termux-smoke 36497057157 on `4df79c30`.
- Tunnel scheduled fail 36496185804 / 109176191755 classified empty-URL skip, closed by #904.
- Instant-fail path-unfiltered workflows on feature branches are noise.
- #903 HOLD (empty-diff / ledger). #899 rebase in flight. Do not merge stale #892/#894.
- Do not pulse #175. #184 names-only. Vercel combined-status is #772 non-gate.

Agent-Identity: Grok (Administrator)

Session 2026-10-01 13:14 PDT / 2026-10-01 20:14 UTC:
- Master tip at session start `478949af307f8ed83fe09afe26bbb21f2d3894cd` (catalog refresh after #973).
- #973 merged at `ffb39b22fa29155de1f95fce55899403a7adbb7a`. #964 closed on that evidence. Zero-job filename failures did not recur on the merge SHA.
- Remaining push failure on ffb39b22 was Historical Evaluation Correlation run 36914069529 (catalog --check race). Repair branch fix/historical-correlation-catalog-race. Do not promote until that SHA has no correlate failure from catalog drift.
- Vercel rate-limit is noise. #903 HOLD. Do not pulse #175. #184 names-only. Linear TER-15 / TER-71 still In Progress — not promote authority.


Session 2026-10-02 15:21 PDT / 2026-10-02 22:21 UTC:
- Master tip at session start `20cfd74ea7f99a664098d695f808756409fd6e3b`.
- Active failure class: push of ancestor `0b135032108bc0cb5ceda8a62cc1f2638fcf55f5` onto master produced zero-job filename failures (ci-sweep 37071088656, swe-reference 37071087430, agent-jules 37071086431, actions-run-watcher 37071085454, fix-on-failure 37071084658, context-relationship-backfill 37071083955). Actor timerloggedout-spec. Tip remained `20cfd74e`. Not a current-tree YAML regression.
- Ruleset `master-no-rewind` id 24394235 active: deletion and non_fast_forward, no bypass actors.
- #996 merged `57cbafa6b589d93309f690ea6194a1c0f65396c6`. Evidence on receipt `063547bbd9d01197c2b9e4eca20864a60b314aa2` (parent `fc4c1ce84b1377472833de421f1a72780e49da69`): repo gate 37071857211 success, termux smoke 37071857224 success, development evaluation 37071857133 success. Parent repo gate 37071836003 success, termux smoke 37071835891 success, development evaluation 37071835865 success, historical promotion gate 37071835885 success, actionlint 37071835928 success, workflow surface policy 37071835907 success. Receipt action_required was bot approval, not a code failure. Post-merge push gates in progress at note time (repo gate 37072092071, termux smoke 37072092119).
- #984 not master. #903 HOLD. Do not pulse #175. #184 names-only. Linear TER-15 still In Progress — not promote authority.


Session 2026-10-02 20:14 PDT / 2026-10-03 03:14 UTC:
- Master tip at session start `c90727c83b63915a7656c3be3c901250fe7797ec` (sweep receipt after #1004 `830e11a9`).
- Post-merge n8n SHE bridge on `830e11a9`/`a61c089a`/`c90727c8` success (not zero-job). Repo gate 37089400164 success, termux smoke 37089400157 success, sweep 37091668135 success. Combined status failure is Vercel rate-limit only.
- Ancestor `0b135032` zero-job class is not current-tree. Hygiene-24h zero-job on feat/dashboard-lanes-v2 closed by #1003 on that base only.
- Active class: Sweep Accountability receipt non-fast-forward (run 37082734311). Repair branch `fix/sweep-receipt-non-ff-20261002`. Do not promote until that SHA has no filename-named workflow failure and repo gate is green.
- #984 not master. #903 HOLD. Do not pulse #175. #184 names-only. Linear TER-15 / TER-71 not promote authority.

Session 2026-10-03 09:16 PDT / 2026-10-03 16:16 UTC:
- Master tip at session start moved through sweep receipt `7f7562c81919d623bb4ec02835cfdbb90af81cb8` to help-wanted refresh. Active master filename class: historical backfill run 37126510237 on `39f3eaf50cd1549d2975f959084e5203d98f8848` exit 2, GitHub issues HTTP 403 after retries (page 7). Watcher run 37126698328 followed that conclusion. Not a graph-contradiction recurrence.
- Repair branch fix/backfill-rate-limit-defer defers 403/429 after retries (RateLimitDeferred, exit 0, no graph commit). Do not promote until that SHA has no filename-named workflow failure and repo gate is green.
- Throughput runs 37125932879 artifact-not-found plus 403 are not this repair. Sweep 37136188913 receipt refname race is not master. #984 not master. #903 HOLD. Do not pulse #175. #184 names-only. Linear TER-15 / TER-71 not promote authority.

Session 2026-10-03 12:15 PDT / 2026-10-03 19:15 UTC:
- Master tip at session start moved during recon from `ea84e1e0d22e680bd051c919a295ba53e52dd036` to `349411034c89ea77207f7cbb79f37007426b2d9e`.
- Active failure class: continuous-improve run 37145725107 on `4a54d96f76f0bba120f1d6713d2e3c7e9baab7af` exit 255, ssh temporary failure in name resolution. Environmental host, not YAML parse. Repair branch `fix/continuous-improve-dns-preflight` adds getent preflight and dispatch-lost skip. Do not promote until that SHA has no filename-named workflow failure and repo gate is green.
- #1052 merged `b74b91cd822ce27ef4401a553df331e02b47bcc6`. Push termux smoke 37143927236 success. Push repo gate 37143927238 cancelled (superseded), not a compile failure.
- #1053 merged `4d53960ab6ab2afd55e9852904dfb1eb108b6a27`. Push event gates not listed on that SHA. Not reopened.
- #903 HOLD. Do not pulse #175. #184 names-only. Linear TER-15 / TER-71 not promote authority.
