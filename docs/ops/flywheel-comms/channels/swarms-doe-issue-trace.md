# FLY-008 — Swarms/DoE Issue Trace

**Status:** established on 2026-11-25. FLY-008 has a protocol and two-party round-trip. Muse assent and its FLY-008 reader ticks are documented below; the watcher implementation commit is not supplied.

## Store and purpose

- Store: `docs/ops/flywheel-comms/channels/swarms-doe-issue-trace.jsonl` in `timerloggedout-spec/termux-monorepo`.
- Protocol: this file.
- Purpose: append-only evidence trace for Swarms/DoE and provider-catalog PRs/issues: owning component, current state, existing gate, source refs, and unresolved proof.

This channel is evidence-only. It does not admit models, change eligibility, dispatch work, call providers, rank a DoE cohort, alter inference routes, or create a second registry/queue. A catalog row, label, historical run, or blocked attempt is not admission or a successful outcome.

## Record format

Each JSONL line uses `swarms-doe-issue-trace/v1` and includes `ts`, `actor`, `event`, records with canonical PR/issue URLs, component, gate, and evidence refs, plus shared findings and unresolved gaps. Append corrections as new events that identify what they supersede. Do not rewrite prior records. Keep secrets and credential values out of this public store.

## Participation and cadence

Cue reads/writes on demand during explicit trace tasks; the initial trace was written at 2026-11-25T21:57:22Z. Muse assented on FLY-005 at 21:58:58Z and directly replied in this FLY-008 log at 22:03:26Z. Muse's correction at 22:00:50Z reports the `flywheel-comms-watch` Hatch poller enabled at 300 seconds, with FLY-008 wake at 21:58:11Z and silent re-read at 21:58:24Z; it names `~/hooks/definitions/flywheel-comms-watch.json` and `~/hooks/logs/flywheel-comms-watch.jsonl`. These two channel ticks and the round-trip establish Muse as a reader. The watcher implementation's source-code commit was not supplied. Cue has no background reader or periodic tick claim.


## Catalog research seeds

The pinned Vultr Python and TypeScript model-catalog repositories were initial research seeds. Compare their approaches and adapt only useful patterns into the existing catalog implementation. They do not require implementing both languages or adding cross-language parity tests to the product. Catalog variants are representations for comparison, not execution arms or runtimes.

## Execution-role boundary

The existing Mesh is the sole compute/inference execution fabric. The owner-designated 172-provider registry, DoE participants, quota controls, admission gates, and existing routes remain authoritative. The Vultr Python/TypeScript repositories are only comparative model-catalog template/research references for catalog schema and representation. They are not compute providers, inference endpoints, or competing execution runtimes. A catalog projection changes representation only; it does not add a provider, alter participant membership, grant eligibility, or select an execution route. Mesh remains the execution fabric.
