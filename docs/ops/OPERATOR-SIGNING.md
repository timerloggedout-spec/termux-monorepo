# OPERATOR Signing Ledger

**Source policy:** [PR #126 comment 5243623808](https://github.com/timerloggedout-spec/termux-monorepo/pull/126#issuecomment-5243623808).

## Rule

OPERATOR agents (Grok and other provider sessions with OPERATOR access) **must** sign material modifications with **session id** and **message / comment id**.

Format:

```text
Signed-off-by: <AgentName> (OPERATOR) <session-id> / <message-or-comment-id>
```

What must be signed: matrix score changes, ops workflow changes, policy docs under `docs/ops/`, disposition / context_key contract changes.

Non-OPERATOR bots (Jules, CodeRabbit, Devin, Tembo, …) use normal bot attribution.

## Ledger (append-only)

| Date (UTC) | Agent | Session / Message id | Diff pointer | Summary |
|------------|-------|----------------------|--------------|---------|
| 2026-08-10 | Grok | session-2026-08-10 / msg-matrix-init | [commit](https://github.com/timerloggedout-spec/termux-monorepo/commit/843ddff37d2e515ba13bc56f8f4875126cc665d5) | Initial matrix + signing docs |
| 2026-08-10 | Grok | session-2026-08-10 / msg-ctxkey-autojules | [280762c](https://github.com/timerloggedout-spec/termux-monorepo/commit/280762cb505e7de3dab964f22c8de0b99e10cdcf) | auto-jules context_key + disposition-first |
| 2026-08-10 | Grok | session-2026-08-10 / msg-pr-145 | [PR #148](https://github.com/timerloggedout-spec/termux-monorepo/pull/148) | Opened #148 |
| 2026-08-10 | Grok | session-2026-08-10 / msg-pr-146 | [PR #149](https://github.com/timerloggedout-spec/termux-monorepo/pull/149) | Opened #149 |
| 2026-08-10 | Grok | session-2026-08-10 / msg-split-ledger-ctxops | [faa76e5](https://github.com/timerloggedout-spec/termux-monorepo/commit/faa76e547e845547ebe52bfb7eb6bf0e3684b164) | Clean matrix; ledger; continuous-ops context_key |
| 2026-08-10 | Grok | session-2026-08-10 / msg-sync-146-ledger | *(this commit on #149 branch)* | Sync docs to signal-alignment branch |

## How to append

1. Make the change (workflow / matrix score / policy).
2. Add a row here with date, agent, session/msg id, link to commit or PR diff.
3. Include the Signed-off-by line in the commit message and any related issue/PR comment.

## Related

- [`DECISION-MATRIX.md`](DECISION-MATRIX.md) — clean scored data only
- [`DELPHI-WEIGHTING.md`](DELPHI-WEIGHTING.md) — future agent-weight interpolation
- AGENTS.md hard rules
