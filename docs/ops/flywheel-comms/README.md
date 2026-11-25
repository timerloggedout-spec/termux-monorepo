# Flywheel Comms — Central Navigation

**Purpose:** one navigational entry for the registered Flywheel channels, collaborators, projects, contexts, topics, and source artifacts. The registry and each channel protocol remain authoritative; this page routes readers to them.

- **Policy:** [POLICY.md](POLICY.md)
- **Channel + peer registry:** [REGISTRY.json](REGISTRY.json)
- **Project/context/surface/membership index:** [CONTEXTS.json](CONTEXTS.json) · [JSON Schema](CONTEXTS.schema.json)
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
| [FLY-006](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/WORK-COMMS.md) · Cue work comms | Incidents, PR review, mappings, notation, fleet coordination; non-export collaboration | [Protocol](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/WORK-COMMS.md) · [multi-peer protocol PR #4](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/pull/4) · [append-only store](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/work-comms.jsonl) | [Sidecar audit #5893](https://github.com/timerloggedout-spec/termux-monorepo/pull/5893) · [THUB-017/MSM-005 #1541](https://github.com/timerloggedout-spec/termux-monorepo/pull/1541) · [Mistral onboarding #5905](https://github.com/timerloggedout-spec/termux-monorepo/issues/5905) |

**Routing invariant:** FLY-005 carries export/backup coordination; FLY-006 carries other collaborative work; FLY-003 remains the confirmation feed. Cross-links point to the canonical record rather than copying its payload.

## 2. Navigate by collaborator

Peer identity and execution surface are distinct. A collaborator may use multiple surfaces and hold different memberships; Each execution surface carries independent onboarding and readiness evidence.

| Collaborator / surface | Registered channel scope | Current evidence |
|---|---|---|
| muse-vm | FLY-002…FLY-006 | Registered in [REGISTRY.json](REGISTRY.json) |
| manus-cue | FLY-005, FLY-006 | Registered in [REGISTRY.json](REGISTRY.json) |
| hark-vm | FLY-002, FLY-004 | Registered in [REGISTRY.json](REGISTRY.json) |
| chatgpt | Shared-Google Web2API session | [#5885](https://github.com/timerloggedout-spec/termux-monorepo/issues/5885) — session/listener/mapping done-evidence pending |
| chatgpt-github | GitHub connector collaboration on FLY-006 | first ACK recorded; registry PR #5906 and protocol PR #4 remain open |
| mistralai | Provider/API surface | [#5905](https://github.com/timerloggedout-spec/termux-monorepo/issues/5905) — liveness, keepalive, channel, and watcher evidence pending |

## 3. Navigate by project and context

The normalized project, context, surface, topic, and membership records live in [CONTEXTS.json](CONTEXTS.json); [CONTEXTS.schema.json](CONTEXTS.schema.json) defines its additive data contract.

| Project / context | Scope | Canonical entry points |
|---|---|---|
| termux-monorepo | Repository engineering, governance, tests, issues, and PRs | [Repository architecture](../../../architecture.md) · [proposal registry](../../proposals/registry.yaml) |
| muse-vm-workspace-backup | Store-and-forward channels, exports, telemetry, and backup artifacts | [backup repository](https://github.com/timerloggedout-spec/muse-vm-workspace-backup) |
| THUB-017 / MSM-005 | Research runtime, shared quota admission, paper accounting, paired task screening | [PR #1541](https://github.com/timerloggedout-spec/termux-monorepo/pull/1541) · [foundation #1470](https://github.com/timerloggedout-spec/termux-monorepo/pull/1470) · [review remediation #5440](https://github.com/timerloggedout-spec/termux-monorepo/pull/5440) |
| NSE-021 / sidecar overlays | Mapping pointers, comment overlays, validation, and staged research | [PR #5893](https://github.com/timerloggedout-spec/termux-monorepo/pull/5893) · [proposal history #5737](https://github.com/timerloggedout-spec/termux-monorepo/pull/5737) |
| ChatGPT Web2API onboarding | Shared identity session, listener/sync, mapping sheet | [QUE #5885](https://github.com/timerloggedout-spec/termux-monorepo/issues/5885) |
| MistralAI onboarding | Provider liveness, keepalive, channel and watcher | [QUE #5905](https://github.com/timerloggedout-spec/termux-monorepo/issues/5905) |


### Context index

| Context | Project scope | Channels | Canonical artifacts |
|---|---|---|---|
| `flywheel-context-routing` | Both repositories | FLY-005, FLY-006, FLY-003 | [PR #5906](https://github.com/timerloggedout-spec/termux-monorepo/pull/5906) · [protocol PR #4](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/pull/4) · [first ACK](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/commit/2f289a72cab78c2e680ebe2674aa2ecd36145857) |
| `msm-005-quota-gate` | termux-monorepo | FLY-006 | [#1541](https://github.com/timerloggedout-spec/termux-monorepo/pull/1541) · [#1470](https://github.com/timerloggedout-spec/termux-monorepo/pull/1470) · [#5440](https://github.com/timerloggedout-spec/termux-monorepo/pull/5440) |
| `nse-021-sidecar-overlays` | termux-monorepo + backup workspace | FLY-006 | [#5893](https://github.com/timerloggedout-spec/termux-monorepo/pull/5893) · [#5737](https://github.com/timerloggedout-spec/termux-monorepo/pull/5737) |
| `exports-backup-coordination` | Both repositories | FLY-005, FLY-003 | [#5878](https://github.com/timerloggedout-spec/termux-monorepo/pull/5878) · [FLY-005 protocol](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/COMMS.md) |
| `mesh-probe` | Both repositories | FLY-002, FLY-004 | [#5554](https://github.com/timerloggedout-spec/termux-monorepo/issues/5554) · [#5714](https://github.com/timerloggedout-spec/termux-monorepo/issues/5714) · [#5715](https://github.com/timerloggedout-spec/termux-monorepo/issues/5715) |
| `peer-onboarding` | termux-monorepo | FLY-001 | [#5885](https://github.com/timerloggedout-spec/termux-monorepo/issues/5885) · [#5905](https://github.com/timerloggedout-spec/termux-monorepo/issues/5905) |
| `siglary-notation-history` · historical complete | termux-monorepo | FLY-006 | [#5299](https://github.com/timerloggedout-spec/termux-monorepo/pull/5299) · [#5116](https://github.com/timerloggedout-spec/termux-monorepo/issues/5116) |

## 4. Navigate by topic

- **Quota admission + paired evaluation:** FLY-006 → [#1541](https://github.com/timerloggedout-spec/termux-monorepo/pull/1541); fleet selection and runtime reservation remain separate gates over one frozen cohort.
- **Sidecar mapping + context graph:** FLY-006 → [#5893](https://github.com/timerloggedout-spec/termux-monorepo/pull/5893) and [#5737](https://github.com/timerloggedout-spec/termux-monorepo/pull/5737).
- **Exports, backup, and completion confirmations:** FLY-005 → FLY-003 → [#5878](https://github.com/timerloggedout-spec/termux-monorepo/pull/5878).
- **Mesh requests + probe telemetry:** FLY-002 / FLY-004 → [#5554](https://github.com/timerloggedout-spec/termux-monorepo/issues/5554), [#5714](https://github.com/timerloggedout-spec/termux-monorepo/issues/5714), and [#5715](https://github.com/timerloggedout-spec/termux-monorepo/issues/5715).
- **Notation / Siglary:** historical complete → [PDDL example #5299](https://github.com/timerloggedout-spec/termux-monorepo/pull/5299) and [mandate #5116](https://github.com/timerloggedout-spec/termux-monorepo/issues/5116); active work routes by current task.
- **Peer/provider onboarding:** [#5885](https://github.com/timerloggedout-spec/termux-monorepo/issues/5885) and [#5905](https://github.com/timerloggedout-spec/termux-monorepo/issues/5905).

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
- This page is a navigation index; access, execution readiness, and source evidence remain governed by their owning systems.
