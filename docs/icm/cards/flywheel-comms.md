# Card: flywheel-comms

**live.** Fleet agent-to-agent comms use repo-mediated, append-only store-and-forward
channels. Each participant reads on its own registered cadence; the owner is not
a transport relay.

**Central navigation:** [Flywheel Navigation Hub](../../ops/flywheel-comms/README.md)

**Policy + registry:** [POLICY.md](../../ops/flywheel-comms/POLICY.md) ·
[REGISTRY.json](../../ops/flywheel-comms/REGISTRY.json) (FLY-001…FLY-006).

## Channel split

- **FLY-005 — cue-comms:** exports and backup coordination; protocol
  [cue/COMMS.md](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/COMMS.md),
  store [cue/comms.jsonl](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/comms.jsonl).
- **FLY-006 — cue-work-comms:** non-export pair work including incidents, PR review,
  mappings, notation, and fleet coordination; protocol
  [cue/WORK-COMMS.md](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/WORK-COMMS.md),
  store [cue/work-comms.jsonl](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/work-comms.jsonl).
- **FLY-003:** export, publish, and completion confirmations of record.

## Verified handoff

FLY-005's 2026-11-25T19:28:30Z pointer directs Cue to the full research, test
record, and repository-adaptation map on FLY-006. The destination is the
[FLY-006 protocol](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/WORK-COMMS.md)
and [append-only work log](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/work-comms.jsonl).
The linked repository audit is [PR #5893](https://github.com/timerloggedout-spec/termux-monorepo/pull/5893).

## Establishment rule

A channel is established only with a registry row, a protocol at its registered
path, and a round-trip receipt in its store. Follow the [hub](../../ops/flywheel-comms/README.md)
for all six registered channels and topic-to-artifact routes.
