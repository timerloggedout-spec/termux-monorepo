# #5219 RE-FIX — trigger audit + mint-effectiveness root cause

QDesk decision #5219 c.6827001855. Done-evidence verdicts on the
1h window 13:09:35–14:09:35Z: ② FAIL (4,799 runs vs <200/h) ·
④ FAIL (51× installation-limit on 28 runs) · ③ PASS (∅ Vercel cap
failures). First-pass 83/PASS superseded (20-page cap — invalid).

## Why (a)/(b) did not hold

- (a) moved buckets, not creation. Creation is event-driven
  (workflow_run 2,493 · issue_comment 1,435 ≈ 82% of the window).
  Token migration cannot cut creation count.
- (b) cancel-in-progress on repo-tracking-collect only: 1,746 runs
  cancelled in-window, 727 still created. Wrong layer for ②.

## Mint-effectiveness — root cause (firsthand)

All 51 rate-limit hits in the annotation sweep are
`API rate limit exceeded for installation` — the **Swarm App
installation bucket** (5,000 req/h per installation), not the
shared `GITHUB_TOKEN`. The 13:48Z collect-peer-responses 429
(run 43227930089, check 131215886690 — QDesk's spot-check) is an
installation-limit hit. The mint works; migration **concentrated**
all collector traffic into one 5,000/h bucket, and at ~4,800
runs/hour the bucket exhausts. The creation cuts in this PR are
the mint fix: fewer runs → fewer calls against the one bucket.
#5230 (headroom alerting) covers the paging side.

## Trigger audit — firsthand event splits (last 100 runs each)

| workflow | window | event split (last 100) |
|---|---|---|
| Quota Dispatch Tree | 785 | workflow_run 77% · issue_comment 17% · pull_request_target 5% · push 1% |
| repo-tracking-collect | 727 | workflow_run 94% · pull_request_target 5% · push 1% |
| lane events recorder | 375 | workflow_run 100% |
| Peer review orchestrator | 88 | issue_comment 74% · pull_request 12% · pull_request_target 14% |

Cascade: one upstream completion → lane-events-recorder →
quota-dispatch-tree + repo-tracking-collect (×2). The recorder
itself fired on 6 upstreams, including tribute-status-refresh —
which is itself triggered by tribute execute/followup/scout
completions — so one tribute event created a recorder run
directly AND another via the status-refresh completion.

## Cuts in this PR

1. **peer-review-orchestrator**: drop the duplicate `pull_request`
   trigger (identical types to `pull_request_target`; the collect
   job gates only on issue_comment vs everything else). ~12% of
   its runs. Its concurrency is UNTOUCHED: cancel-in-progress
   stays false (recorded failure mode, runs 37247048701/
   37247242679 on #1125 — cancelled provider collects recorded
   as failures).
2. **quota-dispatch-tree**: pull_request_target types trimmed to
   [opened, synchronize, reopened, closed] (edited /
   converted_to_draft / ready_for_review create runs the decide
   job cannot use differently); `push` dropped (covered by the
   workflow_run cascade + */30 schedule). issue_comment KEPT:
   the decide job acts only on `/quota force all`, which has no
   other intake (17% of recent runs; accepted, not hidden).
   Concurrency: per-event group → single group + cancel (the
   tree is an idempotent re-evaluation).
3. **repo-tracking-collect**: same PR-type trim. Concurrency
   already cancel-in-progress (leg b).
4. **lane-events-recorder**: `tribute-status-refresh` removed
   from the fan-in (duplicate leg; covered by the direct tribute
   legs). NO concurrency change: append-only Neon writer with no
   re-scan guarantee — cancelling mid-write could drop a batch.
5. **context-relationship-audit** (175/h): `edited`/`deleted`
   types removed (issue_comment, pull_request_review_comment,
   issues, pull_request_review) — they re-ran the whole audit
   on metadata-only changes.

## Re-verify

`scripts/ops/verify_rate_limit_window.py --window-start <ISO>
--hours 1` reproduces the corrected method (6×10-min slices +
annotation sweep with coverage recorded). Criteria: ② <200/h ·
④ ∅ installation-limit annotations. A capped slice or a partial
sweep can never read as a pass.

## Honest estimate

The trims remove the known duplicate/multiplier legs, but the
tail is long (top-12 workflows ≈ 2,986 of 4,799; the rest spread
over dozens). Whether the fresh post-merge window reads <200/h
depends on the fleet's activity in that window — the trims are
necessary, and if the fresh window still fails, the next leg is
scheduled-aggregator consolidation (time-batched collection in
place of event-driven fan-out), not more trigger trims.
