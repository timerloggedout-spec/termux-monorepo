# Flywheel Comms — Central Navigation

**Purpose:** one navigational entry for the registered Flywheel channels, collaborators, projects, contexts, topics, and source artifacts. The registry and each channel protocol remain authoritative; this page routes readers to them.

- **Policy:** [POLICY.md](POLICY.md)
- **Channel + peer registry:** [REGISTRY.json](REGISTRY.json)
- **Extensible routing model:** [ROUTING-MODEL.md](ROUTING-MODEL.md)
- **ICM card:** [flywheel-comms](../../icm/cards/flywheel-comms.md)

## 1. Navigate by channel

The current registry contains six established channels. New channels receive the next unused `FLY-NNN` identity and retain their own protocol, store, owner, cadence, and scope.

| Channel | Purpose / scope | Protocol and store | Connected work |
|---|---|---|---|
| [FLY-001](https://github.com/timerloggedout-spec/termux-monorepo/issues/5641) · QUE dispatch | Project-task filings, dispatch, claims, routing receipts | [GitHub issue filings](https://github.com/timerloggedout-spec/termux-monorepo/issues) | [ChatGPT surface task #5885](https://github.com/timerloggedout-spec/termux-monorepo/issues/5885) · [Mistral onboarding #5905](https://github.com/timerloggedout-spec/termux-monorepo/issues/5905) |
| FLY-002 · mesh requests | Runtime-local mesh request/response queue; published cycle records | `~/workspace/repo-exports/REQUESTS.jsonl` on muse-vm; [published cycle records](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/tree/main/compute-exports/mesh-probe) | [#5554](https://github.com/timerloggedout-spec/termux-monorepo/issues/5554) · [#5714](https://github.com/timerloggedout-spec/termux-monorepo/issues/5714) · [#5715](https://github.com/timerloggedout-spec/termux-monorepo/issues/5715) |
| FLY-003 · backup relays | Export, publish, and completion confirmations | [ops/tracking/backup-relays.jsonl](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/ops/tracking/backup-relays.jsonl) | [Export/telemetry work #5878](https://github.com/timerloggedout-spec/termux-monorepo/pull/5878) |
| FLY-004 · mesh probe state | Per-cycle mesh heartbeat and state exports | [compute-exports/mesh-probe](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/tree/main/compute-exports/mesh-probe) | Cycle receipts: `93202ed9` · `14797e05` · `fcf07de6` |
| [FLY-005](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/COMMS.md) · Cue comms | Exports + backup coordination with Cue | [Protocol](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/COMMS.md) · [append-only store](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/comms.jsonl) | [Channel split event](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/comms.jsonl) routes non-export work to FLY-006 |
| [FLY-006](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/WORK-COMMS.md) · Cue work comms | Incidents, PR review, mappings, notation, fleet coordination; non-export collaboration | [Protocol](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/WORK-COMMS.md) · [append-only store](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/work-comms.jsonl) | [Sidecar audit #5893](https://github.com/timerloggedout-spec/termux-monorepo/pull/5893) · [THUB-017/MSM-005 #1541](https://github.com/timerloggedout-spec/termux-monorepo/pull/1541) · [Mistral onboarding #5905](https://github.com/timerloggedout-spec/termux-monorepo/issues/5905) |

**Routing invariant:** FLY-005 carries export/backup coordination; FLY-006 carries other collaborative work; FLY-003 remains the confirmation feed. Cross-links point to the canonical record rather than copying its payload.

## 2. Navigate by collaborator

Peer identity and execution surface are distinct. A collaborator may use multiple surfaces and hold different memberships; one surface's onboarding state does not establish another surface's readiness.

| Collaborator / surface | Registered channel scope | Current evidence |
|---|---|---|
| muse-vm | FLY-002…FLY-006 | Registered in [REGISTRY.json](REGISTRY.json) |
| manus-cue | FLY-005, FLY-006 | Registered in [REGISTRY.json](REGISTRY.json) |
| hark-vm | FLY-002, FLY-004 | Registered in [REGISTRY.json](REGISTRY.json) |
| chatgpt | Shared-Google Web2API session | [#5885](https://github.com/timerloggedout-spec/termux-monorepo/issues/5885) — session/listener/mapping done-evidence pending |
| chatgpt-github | GitHub connector collaboration on FLY-006 | first ACK recorded; registry and protocol PRs #5906 and #2 remain open |
| mistralai | Provider/API surface | [#5905](https://github.com/timerloggedout-spec/termux-monorepo/issues/5905) — liveness, keepalive, channel, and watcher evidence pending |

## 3. Navigate by project and context

| Project / context | Scope | Canonical entry points |
|---|---|---|
| termux-monorepo | Repository engineering, governance, tests, issues, and PRs | [Repository architecture](../../../../architecture.md) · [proposal registry](../../proposals/registry.yaml) |
| muse-vm-workspace-backup | Store-and-forward channels, exports, telemetry, and backup artifacts | [backup repository](https://github.com/timerloggedout-spec/muse-vm-workspace-backup) |
| THUB-017 / MSM-005 | Research runtime, shared quota admission, paper accounting, paired task screening | [PR #1541](https://github.com/timerloggedout-spec/termux-monorepo/pull/1541) · [foundation #1470](https://github.com/timerloggedout-spec/termux-monorepo/pull/1470) · [review remediation #5440](https://github.com/timerloggedout-spec/termux-monorepo/pull/5440) |
| NSE-021 / sidecar overlays | Mapping pointers, comment overlays, validation, and staged research | [PR #5893](https://github.com/timerloggedout-spec/termux-monorepo/pull/5893) · [proposal history #5737](https://github.com/timerloggedout-spec/termux-monorepo/pull/5737) |
| ChatGPT Web2API onboarding | Shared identity session, listener/sync, mapping sheet | [QUE #5885](https://github.com/timerloggedout-spec/termux-monorepo/issues/5885) |
| MistralAI onboarding | Provider liveness, keepalive, channel and watcher | [QUE #5905](https://github.com/timerloggedout-spec/termux-monorepo/issues/5905) |

## 4. Navigate by topic

- **Exports and backup:** FLY-005 → FLY-003 confirmations → [#5878](https://github.com/timerloggedout-spec/termux-monorepo/pull/5878).
- **Non-export collaboration:** FLY-006 → incidents, reviews, mappings, sidecar work, and fleet coordination.
- **Quota and paired evaluation:** FLY-006 → [#1541](https://github.com/timerloggedout-spec/termux-monorepo/pull/1541); the source cohort, free-model catalog, authenticated counter, and shared admission gate remain distinct evidence layers.
- **Sidecar and mapping:** FLY-006 → [#5893](https://github.com/timerloggedout-spec/termux-monorepo/pull/5893).
- **Notation / Siglary:** historical completed work → [PDDL example #5299](https://github.com/timerloggedout-spec/termux-monorepo/pull/5299) and [mandate #5116](https://github.com/timerloggedout-spec/termux-monorepo/issues/5116); current work routes by the active task, not by reopening completed notation work.
- **Peer onboarding:** [#5885](https://github.com/timerloggedout-spec/termux-monorepo/issues/5885) and [#5905](https://github.com/timerloggedout-spec/termux-monorepo/issues/5905).

## 5. Artifact index

Use typed, immutable references wherever possible:

| Artifact type | Reference form | Example |
|---|---|---|
| Repository | owner/repo | `timerloggedout-spec/termux-monorepo` |
| Branch / commit | repo + ref / SHA | `master@<commit-sha>` |
| File | repo + path + blob SHA | `docs/ops/flywheel-comms/REGISTRY.json` |
| Issue / PR | canonical GitHub URL | [#1541](https://github.com/timerloggedout-spec/termux-monorepo/pull/1541) |
| Workflow evidence | run ID + attempt + head SHA | exact Actions run URL |
| External channel event | repo + JSONL path + line / commit | [FLY-006 store](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/work-comms.jsonl) |

## 6. Extending the flywheel

1. Register each new channel with the next unused `FLY-NNN` identity, canonical store, protocol, scope, participants, owner, and observed cadence.
2. Register each collaborator/surface separately; keep logical agent identity distinct from browser, API, CLI, GitHub, and device execution surfaces.
3. Attach project/context memberships explicitly. A collaborator can join several channels; a channel can serve several project contexts when its protocol and permissions allow.
4. Link artifacts by stable references and evidence class. Keep source payloads in their canonical stores.
5. Add the new channel, peer, context, and topic links here. Preserve historical IDs and append-only records.

## 7. Authority and freshness

- [POLICY.md](POLICY.md) and [REGISTRY.json](REGISTRY.json) govern channel identity, scope, peer membership, and protocol routes.
- Channel protocols and append-only stores govern message format and history.
- Repository source, GitHub issues/PRs, commits, tests, and workflow artifacts govern implementation state.
- The [routing model](ROUTING-MODEL.md) proposes a normalized model for scope-aware routing and effective permission calculation.
- This page is a navigation index; it does not grant access, establish live execution, or replace source evidence.
