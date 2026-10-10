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

[... prior sessions omitted for brevity in this update; full history preserved in git ...]

Session 2026-10-10 14:17 PDT / 2026-10-10 21:17 UTC:
- Master tip at session start `14ecf4a1ef36e38cf5e48610225bdb66cc3776eb` (help-wanted refresh 2026-10-10T20:20Z).
- No conclusion=failure in the latest master window. v3 workflow id 377919668 run 38085578562 event=workflow_run conclusion=success on tip, artifact 11682202279.
- Continuous CI Sweep 38085566455 success. Help-wanted deploys and refreshes success. Watchers skipped. Context audit success.
- Historical v3 failure 38049030150 on ancestor `3400fe3b` (list/pipe class) already addressed by inventory retries/sort/21-day budget on master. Not a current-tree recurrence.
- #1201 open on older base `89622e2c`, mergeable_state=unstable (checks pending), 103 files. Advisory CodeRabbit capacity. Do not promote until rebased + dual-gate green on candidate SHA.
- Ghost 37655538554 still queued on disabled id 354842048. Do not open another workflow id.
- #903 HOLD. Do not pulse #175. #184 names-only. Linear TER-15 Done / TER-71 In Progress — not promote authority. Vercel rate-limit non-gate.
- Promotion only on current-SHA dual-gate (hygiene + portability + agentic termux smoke) + task outcome verified. Mega-merge allowed when dual-gate + mergeable.

Agent-Identity: Grok (Administrator)
