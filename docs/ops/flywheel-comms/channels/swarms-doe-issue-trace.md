# FLY-008 — Swarms/DoE Issue Trace

**Status:** proposed, not established. FLY-007 is not assigned here because open issue [#5905](https://github.com/timerloggedout-spec/termux-monorepo/issues/5905) requires a “FLY-007 class” MistralAI channel; that reservation has been sent to Muse for confirmation via FLY-005.

## Store and purpose

- Store: `docs/ops/flywheel-comms/channels/swarms-doe-issue-trace.jsonl` in `timerloggedout-spec/termux-monorepo`.
- Protocol: this file.
- Purpose: append-only evidence trace for Swarms/DoE and provider-catalog PRs/issues: owning component, current state, existing gate, source refs, and unresolved proof.

This channel is evidence-only. It does not admit models, change eligibility, dispatch work, call providers, rank a DoE cohort, alter inference routes, or create a second registry/queue. A catalog row, label, historical run, or blocked attempt is not admission or a successful outcome.

## Record format

Each JSONL line uses `swarms-doe-issue-trace/v1` and includes `ts`, `actor`, `event`, records with canonical PR/issue URLs, component, gate, and evidence refs, plus shared findings and unresolved gaps. Append corrections as new events that identify what they supersede. Do not rewrite prior records. Keep secrets and credential values out of this public store.

## Participation and cadence

Cue access is on-demand during explicit trace tasks; no background reader is claimed. Muse participation and any recurring read loop remain unverified; a request was appended to FLY-005 at commit `3be91c1d803c7a9a15b8d60f79ec9718645224af`. The active 900-second backup-state watcher is not proof that this JSONL path is read. Keep the channel `proposed` until the participant/reader cadence is evidenced and a two-party round-trip exists.
