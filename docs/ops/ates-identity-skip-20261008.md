# ATES identity skip — 2026-10-08

## Binding

- Repo: `timerloggedout-spec/termux-monorepo`
- Base SHA observed: `4f1d3628997a452d6250f1c3f819a16c4e5113fa`
- Incident: https://github.com/timerloggedout-spec/termux-monorepo/issues/1026
- Failed run: https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/37125900597
- Failed step: `Collect trusted workflow metadata` (job `emit`, 2026-10-03)
- Current counterevidence: ATES runs [37864442221](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/37864442221) and [37864441367](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/37864441367) concluded `success` on master.

## Defect

`agent-throughput-evidence.yml` hard-failed when `workflow_run.name` was outside the explicit Gemini/DeepSeek identity map. A rate-limit early return also skipped writing metadata, so the next step failed on a missing file. Both are observer defects, not product regressions.

## Fix

Unmapped identity and installation rate limits now write a skip receipt and set `proceed=false`. Downstream emit/validate/upload steps run only when `proceed=true`.

## Non-claims

This does not close #1026 until the workflow file is on `master` and a later unmapped `workflow_run` is observed as skipped rather than failed. PR production ledger #1025 is separately stale: latest sampled runs through 37864437275 concluded `success`.
