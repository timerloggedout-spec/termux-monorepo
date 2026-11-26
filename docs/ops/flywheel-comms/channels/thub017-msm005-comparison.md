# FLY-015 — THUB-017 / MSM-005 Comparison

**Status:** proposed, opened 2026-11-26T14:13:23Z. This is a dedicated lane for the #1541/#1540 research-and-accounting comparison; it is not a FLY-005 or FLY-006 task filing.

## Store and purpose

- Store: `docs/ops/flywheel-comms/channels/thub017-msm005-comparison.jsonl` in `timerloggedout-spec/termux-monorepo`.
- Protocol: this file.
- Purpose: evidence-led comparison of THUB-017 research orchestration and MSM-005 paper-point accounting across PR #1541, its open #1470 feature base, and PR #1540, which merged into that feature branch.
- This channel coordinates review only. It does not authorize code changes, merging, deployment, model/provider calls, paid fallback, quota changes, or review-thread resolution.

## Live anchors at opening

- PR #1541 GitHub head: `923643bb006444c2526a998a4fa9a24275b6a09f`; current base branch head: `5e57dcd3d1e8d2a417ad213cdf96622d126df7cf`.
- PR #1470 is open against master.
- PR #1540 merged on 2026-11-13 as `2791d2aacddd01d253e772715a1b07aeebdee351` into the #1470 feature branch, not master.
- The #1541 PR body also cites `e9fb8f1d813f9ca8e89f5df7de29a329afdba034`; reconcile this with the actual current head before using any validation receipt.
- Current GitHub review-thread query: 19 total, 10 unresolved.
- The #1541 pilot stopped at quota admission before inference: 0 model requests. Keep that separate from deterministic implementation tests.

## Record format and rules

One JSON object per line: `{"ts":"<UTC>","actor":"<registered peer>","to":"<registered peer>","event":"<state change>","body":"<Siglary{best} line>"}`. Each event has one recipient. Append only; corrections supersede earlier entries. State changes only. No secrets or credentials. FLY-003 remains the home for completion confirmations of record.

## Responsibilities and completion steps

1. **muse-vm — comparison lead:** verify current PR/base/merge SHAs; distinguish #1541's immediate diff from the full #1470+#1540+#1541 stack; map shared MSM-005 files, functions, contracts, and tests against the unique THUB-017 research delta.
2. **muse-vm — review triage:** classify each of the 10 currently unresolved #1541 review threads as still valid, addressed, outdated, or blocked, with thread URL, file/line, and evidence. Do not resolve threads.
3. **muse-vm — recommendation:** identify the canonical accounting implementation and the smallest safe integration/rebase order; specify only deterministic, quota-safe validation and name any remaining owner decision.
4. **manus-cue — coordinator:** maintain live-state anchors, check the returned evidence and safety boundary, then synthesize the comparison and decisions for the owner.
5. **Both — closeout:** append the answer and ACK in this JSONL. Keep the lane `proposed` until the protocol plus a two-party round trip and reader cadence are evidenced.

## Cadence

Muse's registry-driven `flywheel-comms-watch` is reported at 300 seconds; its read of this new path still needs an ACK/evidence. Cue reads and writes on demand through the GitHub connector and makes no background-reader claim. The lane remains proposed until the owner/peer read loop is evidenced.
