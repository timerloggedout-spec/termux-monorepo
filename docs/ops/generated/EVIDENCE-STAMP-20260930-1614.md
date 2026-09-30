# Evidence stamp — 2026-09-30T16:14Z PDT session

Session-only stamp. Do not squash this branch to master.

## Live master

- SHA: `35eb6fdec7a0af5ca661b84df506848fb679cfc9`
- Message: `ops(help-wanted): live status refresh 2026-09-30T15:20Z`
- Actor: github-actions[bot]
- Paths: help-wanted status JSON/MD only

## Last dual-gate on master (functional squash, not the status bot tip)

- SHA: `c62f32f49478c8ffa9c9806c1db5ff27ea8a659a` (#911)
- repo-gate: [36677300893](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/36677300893) SUCCESS
- termux-smoke: [36677300962](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/36677300962) SUCCESS

Help-wanted live-status commits after `c62f32f` are dashboard JSON/MD only. Dual-gate list for workflow `repo-gate.yml` on `master` still tops at `c62f32f` in this query window.

## Candidate #935 (Ratatui + Tokio TUI)

- URL: https://github.com/timerloggedout-spec/termux-monorepo/pull/935
- Head: `4548437044443ef8ad7f91e934bd9d8cea85bd03`
- Base at recon: `35eb6fdec7a0af5ca661b84df506848fb679cfc9` (current master)
- Files: 11 / +983 / -1 / 17 commits
- mergeable_state: `unstable` (combined commit status failure)
- Dual-gate on head `45484370`:
  - repo-gate [36739425345](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/36739425345) SUCCESS
  - termux-smoke [36739425402](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/36739425402) SUCCESS

## Combined-status noise on #935 (non-gate #772)

- Devin Review: success + "trial expired and no credits remaining"
- CodeRabbit: success + "Review rate limited"
- Vercel help-wanted-dash / help-wanted-oversight / mcp-hub / termux-monorepo: failure, deployment rate limited 24h

These do **not** override dual-gate SUCCESS. They do make GitHub `mergeable_state=unstable` if combined status is required.

## Holds / anti-pulse

- #903 HOLD
- Do not pulse #175 keep-alives (#682, #787, #817, #928 and siblings)
- #184 names-only (no token values in issues/PRs)
- Evidence-stamp PRs are session-only; do not merge from stamps
- Instant-fail path-unfiltered workflows on feature branches are noise

## Decision

- KEEP #935 as the current production candidate.
- Do not promote this stamp.
- Do not squash #935 while `mergeable_state=unstable` if branch protection treats Vercel combined status as required.
- Next act: confirm required checks vs advisory Vercel; if Vercel is non-required, squash #935 onto `35eb6fde` with dual-gate IDs in the commit message.

Agent-Identity: Grok (Administrator)
