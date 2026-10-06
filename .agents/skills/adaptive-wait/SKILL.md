---
name: adaptive-wait
description: Adaptive WAIT for agentic GitHub operations. Re-fetch authoritative state, detect progress or stalls, keep useful disjoint work moving, and promote only from current-SHA evidence.
---

# Adaptive WAIT

Use this skill whenever work is asynchronous: GitHub Actions, reviews, deployments, provider jobs, external agents, or any operation whose next action depends on new state.

## Control objective

Waiting is an evidence-collection phase, not an idle timer. HOLD is not an idle parking state.

The controller must answer, on every cycle:

1. What immutable state am I watching?
2. What evidence changed since the last observation?
3. Can that evidence change the next action?
4. If not, should I back off, do disjoint work, or stop?
5. What authoritative re-fetch will prove the next state?

Continuous Fully Automated Agentic Development: agents auto-promote when dual-gate + task outcome are verified on the candidate SHA. Sovereignty cockpit = ArchWiz + chat (goals/constraints, not a synchronous merge checkpoint).

## State machine

| State | Entry evidence | Action |
|---|---|---|
| ACTIVE | run/job/review/artifact state is changing or useful work is still executing | re-fetch at an adaptive cadence; do not duplicate work |
| QUIET | no meaningful delta, but the operation remains live | increase the wait interval; work on a disjoint bounded task |
| STALLED | repeated identical state, no progress, deadlock, expired deadline, or repeated non-informative retry | stop blind retries; classify and change the experiment/approach |
| TERMINAL | authoritative success/failure/cancellation or task outcome is verified | validate current SHA and close the cycle |
| BLOCKED | required authority, credential, input, or external capacity is missing | record the blocker; request only the missing authority/input |

Never treat elapsed time, HTTP 200, a successful dispatch, or a green individual job as task completion.

## Adaptive cadence

Choose the next observation from evidence, not a universal polling constant:

- Immediate re-fetch: after a material commit, workflow dispatch, rerun, steering action, review response, or newly reported failure.
- Short wait: while a run/job is actively producing new steps, logs, artifacts, or review events.
- Backoff: when repeated observations contain no material delta and the authoritative state remains live.
- Stop retrying: when the same failure repeats without a changed input, environment, or hypothesis.
- One-shot: when no new feedback can change the next action.
- Deadline stop: when the platform/task deadline is authoritative; do not invent a second application-level timeout.

Record why the cadence changed.

## Mandatory re-fetch contract

After every material commit or steering action, re-fetch: SHA -> workflow/run -> jobs -> steps/logs/artifacts -> reviews/comments -> resulting SHA/status.

Bind every conclusion to the SHA that produced its evidence. A newer SHA invalidates approval evidence from an older head unless the evidence is explicitly historical.

## Disjoint-work rule

While useful work is running, continue only with work that cannot mutate or invalidate the watched operation. Good disjoint work includes deterministic documentation or inventory improvements, bounded repository reconnaissance, non-invasive tests, relationship-graph queries, and review/evidence ingestion.

Do not create competing writes, duplicate workflow dispatches, or overlapping branches merely to stay busy.

## Retry / steering rule

Retry only when the new attempt has an evidence-backed reason to differ: changed input or SHA; transient infrastructure/provider failure; recovered capacity/quota; corrected workflow/reference; or a new review finding or authoritative instruction.

Preserve every attempt. Never rewrite history to hide a failed wait cycle.

## Evidence receipt

Each cycle should be representable by a compact receipt:

    observed_at: <UTC>
    watched:
      repo: <owner/name>
      ref: <branch/tag/SHA>
      sha: <immutable SHA>
    state: ACTIVE|QUIET|STALLED|TERMINAL|BLOCKED
    evidence:
      runs: [<run ids>]
      jobs: [<job ids>]
      reviews: [<stable ids>]
      artifacts: [<stable ids>]
    delta: <what changed since prior observation>
    decision: WAIT|BACKOFF|STEER|RETRY|STOP|PROMOTE
    reason: <evidence-backed reason>
    next_check: <authoritative condition>
    outcome: PASS|FAIL|UNKNOWN

Never store secrets, authorization headers, raw discussion bodies, or private session state in the receipt.

## Promotion boundary

Promotion requires: current immutable SHA; current-base relationship verified; relevant validation evidence terminal; requested task outcome verified; no unresolved actionable finding; and evidence attributable to the candidate SHA.

Dual-gate status is necessary where the repository defines it, but it is not a substitute for task-outcome verification.

Repository dual-gate: `hygiene + portability gate` + `agentic termux smoke`. Vercel rate-limit is non-gate (#772). Copilot / CodeRabbit / Devin are advisory only. `mergeable_state=dirty` or a GitHub merge conflict is a hard block even when dual-gate is green — rebase/re-extract onto live tip.

**Mega-merge (Operator 2026-09-24):** Allowed when dual-gate + mergeable. CodeRabbit ~100-file limit is advisory review capacity, not a promote ban. Size alone does not block.

## Terminal states

- success — requested outcome verified;
- clean-no-op — no change required;
- blocked — new authority/input is required;
- approval-required — policy requires escalation;
- exhausted — authoritative task/platform limit reached;
- stagnated — repeated cycles produced no measurable progress.

Never report exhausted, stalled, or blocked as success.

## Closeout

Record what was proven, what remains unproven, the watched SHA, the final authoritative evidence, and the next disjoint action or terminal state.

This skill is the wait/controller layer. adaptive-feedback-cycle owns broader continuous learning; production-reconciliation owns ref alignment; evidence-envelope owns normalized observation fields.

## Session 2026-09-28 17:15 PDT

- Live master `8daeeb72d71ecdefa2f9cde6698426131117e474`.
- Dual-gate PASS: repo-gate 36497249095 / termux-smoke 36497249115.
- #904 merged. Watching #899 rebase onto live tip.
- Instant-fail path-unfiltered workflows are noise.
- #903 HOLD. Do not merge #892/#894. Do not pulse #175. #184 names-only.

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

Session 2026-10-03 16:16 PDT / 2026-10-03 23:16 UTC:
- Master tip at session start `635c481af60e7fa79c1fcb90d6bd4e28deb9c27a`. No master filename-named workflow failure after 21:25Z.
- #1070 merged `da08d49e9722366e8a2dfcfd4fc8c7ab3f2f36b7`. Pre-merge RECON 37155014804 still setFailed on the pre-fix SHA. Current master skip path is present. Not a current-tree failure.
- Active residual: PR Change Effectiveness Ledger run 37159037262 exit 128, `Not a valid commit name` after head moved. Repair branch `fix/ledger-missing-head-skip`. Do not promote until that SHA has no filename-named workflow failure and repo gate is green.
- #984 not master. #903 HOLD. Do not pulse #175. #184 names-only. Linear TER-15 / TER-71 not promote authority.
Session 2026-10-03 17:20 PDT / 2026-10-04 00:20 UTC:
- Master tip at session start `01992fcd922a7e0c064116992abab1b6d78f9e26` (sweep receipt).
- #1085 merged `fa49b9fc5a401a3bd2c764b057d01518e58888ce`. Push gates: repo gate 37161524126 success, termux smoke 37161524158 success, empty-commit watcher 37161524135 success. Sweep push 37161524167 cancelled (superseded), not a filename failure.
- Active class: Action Effectiveness Ledger run 37161519194 exit 126, `/usr/bin/jq: Argument list too long` on unbounded recent_events argv. Skill Quality Lane 37161520852 exit 2 was new blank line at EOF on the three skill files. Not a compile failure.
- Repair branch `fix/ledger-jq-arg-max`. Do not promote until that SHA has no filename-named workflow failure and repo gate is green.
- #984 not master. #903 HOLD. Do not pulse #175. #184 names-only (open, title only). Linear TER-15 / TER-71 not promote authority.

Session 2026-10-05 12:15 PDT / 2026-10-05 19:15 UTC:
- Master tip at session start `844742bebcc1a0aadd512f7bb0d3ecc878b7b5ac` (sweep receipt). Combined status failure is Vercel rate-limit only.
- #1138 merged `0c14c7c87f5567b37e664a6ecf37337121294f84`. Push gates on that SHA succeeded: repo gate 37341142744, termux smoke 37341142701, empty-commit watcher 37341142595, sweep 37341142766, context audit 37341142590. Catalog receipt `46d3853e` repo gate 37341287278 success. Span/404 class closed on those SHAs. Not a filename failure.
- Residual class: Operations Cadence Audit workflow id 362815777 still registered, file absent on tip. Last run 35548390883 (2026-09-21) exit 1, NoneType schedule drift. Ops report 37288781360 is model_not_supported. Not a compile failure.
- Reconciliation dispatch 37362442314 on master. Do not promote this cadence restore until that SHA has no filename-named workflow failure and repo gate is green.
- #984 not master. #903 HOLD. Do not pulse #175. #184 names-only. Linear TER-15 / TER-71 not promote authority. Vercel rate-limit noise. Devin trial-expired skip is not a pass.

Session 2026-10-05 15:16 PDT / 2026-10-05 22:16 UTC:
- Master tip at session start `78c37cd86ba4350a6e55233e69c54b9ef61c9b96` (sweep receipt).
- #1140 still open. Head `f5fb5ef409acc7eeccfd7de76ade29d47ef960c7`. Repo gate 37368700777 attempt 2 success. Operations Cadence Audit 37368700755 attempt 2 success. Sibling pull_request conclusions labeled failure were cancelled jobs with no failed step (termux smoke 37368700752, historical gate 37368700795, sweep 37368700825). Not filename parse. Smoke rerun attempt 2 queued.
- Dispatch 37362442314 authoritative metadata: event workflow_dispatch, head_branch master, head_sha 7dc766caa5b7be6d63b94c3dec349684525bde51, conclusion failure. Not master-staging and not f534f2e3. Do not rewrite that provenance.
- Do not promote #1140 until the follow-up SHA has no filename-named workflow failure and repo gate is green.
- #984 not master. #903 HOLD. Do not pulse #175. #184 names-only. Linear TER-15 / TER-71 not promote authority. Vercel rate-limit noise. Devin trial-expired skip is not a pass.

Session 2026-10-05 18:16 PDT / 2026-10-06 01:16 UTC:
- Master tip at session start moved; observed tip `51f69cfdec4d953c3401f3245321fce9b4734ed2` (sweep receipt), then help-wanted refresh `37fb994`.
- #1143 merged `01493829297a2f6035a45ecab688a5c0d7658eef`. Ancestor of tip (compare ahead, behind 0). Push gates on that SHA were not listed (superseded by #1144 51s later).
- #1144 merged `fb1434ac652497cf6e5173dcebc41faad2241a42`. Push gates: repo gate 37393739923 success, termux smoke 37393740748 success, sweep 37393741112 success, empty-commit watcher 37393739957 success, cadence audit 37393739914 success, Team MVT 37393739716 success. Debate-hygiene class closed by inclusion; schedule rerun not yet observed. Not a filename failure.
- Active class: Dependabot dynamic run 37393760327 on `fb1434ac` exit 1, security_update_not_possible for mcp-hub npm group (undici 5.28.4 vs 6.28.1 and siblings). Not YAML parse. Repair branch `fix/dependabot-mcp-hub-unresolvable-security` ignores those names so the update job stops failing Actions. Do not promote until that SHA has no filename-named workflow failure and repo gate is green.
- Ops report run 37288781360 remains model_not_supported. Integration cannot read Actions variables (403). Do not swap the B3 model fallback again.
- help-wanted-followup run 37398435167 success. Vercel rate-limit noise. Devin trial-expired skip is not a pass.
- #984 not master. #903 HOLD. Do not pulse #175. #184 names-only. Linear TER-15 / TER-71 not promote authority.


Session 2026-10-05 19:15 PDT / 2026-10-06 02:15 UTC:
- Master tip at session start `9e32251ce669fd0227df24442d2a449c12279352` (sweep receipt).
- Active class: Dependabot dynamic run 37393760327 on `fb1434ac` exit 1, security_update_not_possible (undici 5.28.4 vs 6.28.1, tar 7.5.7 vs 7.5.21, smol-toml 1.5.2 vs 1.9.0, and the same class for brace-expansion, fast-uri, ip-address, js-yaml, minimatch, @tootallnate/once).
- #1145 merged `64c246923e4e889805a47fcd5d448c5ccd2bcae8` on code head `805ea5c26ac90224ea20413f8229a86b2a184c79`. Pre-merge: repo gate 37398625558 success, termux smoke 37398625696 success, cadence audit 37398625708 success, historical promotion gate 37398625811 success. DeepSeek 37398625656 and ledger 37398625639 cancelled with zero steps (concurrency), not filename failures. Vercel rate-limit noise. Devin trial-expired skip is not a pass.
- Post-merge push on `64c24692`: repo gate 37403216737 success, termux smoke 37403216782 success, empty-commit watcher 37403216811 success, sweep 37403216705 success. Tip then moved to receipt `70adac622d15e50a56245d48e63b5efa32297409`. No filename-named failure on that tip.
- Incident #1141 closed. Audit cycle run 37368938736 was a cancelled job with zero steps on `d41a8e12`. Later audit-cycle 37399490480 success. Not a compile failure.
- #984 not master. #903 HOLD. Do not pulse #175. #184 names-only. Linear TER-15 / TER-71 not promote authority.

