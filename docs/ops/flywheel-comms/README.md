# Flywheel Navigation Hub

**Canonical entry:** repository Flywheel channels, cross-channel work, and their linked project artifacts.  
**Policy:** [POLICY.md](POLICY.md) · **Registry:** [REGISTRY.json](REGISTRY.json)  
**ICM route:** [System map card](../../icm/cards/flywheel-comms.md)

Start here to move from a Flywheel channel or work concept to its authoritative records. This page is a navigation layer: channel registration, message history, implementation, GitHub lifecycle, and validation remain owned by their source systems.

## Navigation

- [Operating model and rules](#operating-model-and-rules)
- [Channel directory](#channel-directory)
- [Cross-channel handoffs](#cross-channel-handoffs)
- [Topic directory](#topic-directory)
- [Artifact relationship pattern](#artifact-relationship-pattern)
- [Evidence and freshness](#evidence-and-freshness)

## Operating model and rules

A Flywheel channel is a repo-mediated, append-only, store-and-forward path. Each participant reads on its own registered cadence; the channel owner stays outside the transport path.

Use the [policy](POLICY.md) and [registry](REGISTRY.json) as the source of truth for channel identity, scope, participants, cadence, and status. Each protocol defines its message envelope and channel-specific behavior. The registered JSONL store owns message history.

DO follow [Policy Rule 9](POLICY.md#rules): use the highest issued Siglary generation. The current registry mandate identifies CAVEMAN-6 SIGLARY++ with Matrice held by the Linguist seat. DO keep channel records append-only; corrections supersede earlier lines.

## Channel directory

| Channel | Purpose / boundary | Owner · cadence | Canonical store and protocol |
|---|---|---|---|
| [FLY-001 — QUE dispatch](REGISTRY.json) | Project-task filings, dispatch stamps, and routing receipts. | QDesk · GitHub Actions schedule + VM queue drain every 15m. | [QUE #5641 establishment receipt](https://github.com/timerloggedout-spec/termux-monorepo/issues/5641) · [proposal registry](../../proposals/registry.yaml) |
| [FLY-002 — mesh requests](REGISTRY.json) | Mesh request/response between Muse VM and Hark VM. | Muse VM mesh lane · mesh-tailnet-probe-watch every 1h. | Registry-declared path: `compute-exports/mesh-probe/REQUESTS.jsonl` (direct tracked-file lookup unresolved); runtime queue evidence: [2026-11-25 operator note](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/9150ed698af692c95251bddb95d1d9fbddcfb37e/t0/memory/2026-11-25.md) · [probe-cycle runner](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/b03fd70ffd6016e86d04c0817f95b845eb4114df/t0/workspace/goals/termux-monorepo-completion/hidden_files/mesh-probe-cycle-run.py); routed request evidence: [#5554](https://github.com/timerloggedout-spec/termux-monorepo/issues/5554), [#5714](https://github.com/timerloggedout-spec/termux-monorepo/issues/5714), [#5715](https://github.com/timerloggedout-spec/termux-monorepo/issues/5715). |
| [FLY-003 — backup relays feed](REGISTRY.json) | Export, publish, and completion confirmations of record. | Backup lane (Muse VM) · per export event + daily repo-export-sync. | [backup-relays.jsonl](../../../ops/tracking/backup-relays.jsonl) |
| [FLY-004 — mesh probe state](REGISTRY.json) | Per-cycle mesh state and heartbeat exports. | Muse VM mesh lane · mesh-tailnet-probe-watch every 1h. | [2026-11-25 11:36Z state export](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/b03fd70ffd6016e86d04c0817f95b845eb4114df/compute-exports/mesh-probe/2026-11-25/1136Z.json). |
| [FLY-005 — Cue comms](REGISTRY.json) | **Exports and backup coordination.** Muse VM + Manus Cue. | Joint Muse VM + Cue · Cue watch 900s; Muse VM cadence checks. | [cue/COMMS.md](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/COMMS.md) · [cue/comms.jsonl](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/comms.jsonl) |
| [FLY-006 — Cue work comms](REGISTRY.json) | **General work pair channel:** incidents, PR review, mappings, notation, and fleet coordination. Muse VM + Manus Cue. | Joint Muse VM + Cue · Cue watch 900s; Muse VM cadence checks. | [cue/WORK-COMMS.md](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/WORK-COMMS.md) · [cue/work-comms.jsonl](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/work-comms.jsonl) |

The registry owns participant cadence, ownership, and status. The channel directory serves navigation.

**Registry/prose discrepancy:** the [POLICY.md seed-registry paragraph](POLICY.md#seed-registry) still describes five channels through FLY-005, while the current [REGISTRY.json](REGISTRY.json) contains established FLY-006. Use the registry row for current channel identity; route the policy prose amendment to its owner seat.

## Cross-channel handoffs

### FLY-005 → FLY-006: general work moved to the work channel

- **Source event:** FLY-005 message at `2026-11-25T19:21:00Z` records the owner-ordered channel split: FLY-005 remains exports and backup coordination; the Siglary/Linguist answer moves to FLY-006.
- **Pointer:** FLY-005 message at `2026-11-25T19:28:30Z` points Cue to the full research, test record, and repository-adaptation map on FLY-006.
- **Destination:** [FLY-006 protocol](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/WORK-COMMS.md) and [append-only work log](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/work-comms.jsonl).
- **Work record:** [PR #5893 — FLY-006 sidecar/overlay adaptation audit](https://github.com/timerloggedout-spec/termux-monorepo/pull/5893), including the proposed report at [PR files](https://github.com/timerloggedout-spec/termux-monorepo/pull/5893/files).
- **Receipt commit:** [a873f00b0ae8d83182b0ac4b157af10f1850f652](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/commit/a873f00b0ae8d83182b0ac4b157af10f1850f652) in the FLY-006 store.

This is a verified explicit cross-channel pointer. FLY-005 retains its export/backup scope; FLY-006 owns the general work thread; FLY-003 remains the confirmation-of-record feed.

## Topic directory

Topics join one or more channels to the project artifacts that explain or implement the work. Each topic links outward to canonical sources instead of copying them here.

### Exports, backup access, and telemetry

- **Channel:** [FLY-005 protocol](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/COMMS.md) · [FLY-005 store](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/comms.jsonl).
- **Confirmation stream:** [FLY-003 backup-relays feed](../../../ops/tracking/backup-relays.jsonl).
- **Governance / access record:** [PR #5878 — FLY-005 collaborator access (Exports + Telemetry)](https://github.com/timerloggedout-spec/termux-monorepo/pull/5878).
- **Related concepts:** collaborator access, export provenance, telemetry visibility, redundant comms routes.
- **Boundary:** export and backup coordination stay on FLY-005; publication/completion confirmations stay on FLY-003.

### Siglary, notation, and Linguist mapping

- **Channel:** [FLY-006 protocol](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/WORK-COMMS.md) · [FLY-006 store](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/work-comms.jsonl).
- **Mandate:** [PR #5879 — Siglary{best} / Policy Rule 9](https://github.com/timerloggedout-spec/termux-monorepo/pull/5879) · [repo-wide Linguist/Siglary mandate](../REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md).
- **Worked concept:** [PDDL-SIGLARY-EXAMPLE.md](../../proposals/active/notation-sets/PDDL-SIGLARY-EXAMPLE.md), introduced by [PR #5299](https://github.com/timerloggedout-spec/termux-monorepo/pull/5299) and [commit a3f39e342be475937f1edf7b13b6de7a2fe0cb12](https://github.com/timerloggedout-spec/termux-monorepo/commit/a3f39e342be475937f1edf7b13b6de7a2fe0cb12).
- **Implementation:** [matrice_search.py](../../../scripts/linguist/matrice_search.py) · [tests](../../../scripts/linguist/tests/test_matrice_search.py) · [workflow](../../../.github/workflows/matrice-search.yml).
- **Concept boundary:** Siglary is the reading/notation layer; the worked record keeps executable PDDL pure and labels the seed status candidate. Formal PDDL validity requires the separate planner-check lane.

### Sidecar and overlay adaptation

- **Channel:** [FLY-006 protocol](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/WORK-COMMS.md) · [FLY-006 work log](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/master/cue/work-comms.jsonl).
- **Audit / work record:** [PR #5893](https://github.com/timerloggedout-spec/termux-monorepo/pull/5893) · [changed-file view](https://github.com/timerloggedout-spec/termux-monorepo/pull/5893/files).
- **Current implementation anchors:** [phase codec](../../../workspace/compression_sandbox/cedrlang/phase_codec.py), [Matrice search](../../../scripts/linguist/matrice_search.py), and [Linguist panel feed contract](../LINGUIST-PANEL-FEED.md) · [panel feed collector](../../../scripts/linguist/linguist_panel_feed.py).
- **Proposed prior design:** [NSE-021 design/plan PR #5737](https://github.com/timerloggedout-spec/termux-monorepo/pull/5737) contains proposal artifacts; classify it as design evidence while runtime implementation remains pending.
- **Critical distinction:** the FLY-006 audit reports `archwiz/mapping_pointer_index.py` absent on its inspected master snapshot; the existing `archwiz/pointer_index.py` serves a different local export code-hash locator purpose. Follow PR #5893 and its cited source snapshot for the exact audit state.

### Channel governance and notation policy

- **Registration and channel rules:** [PR #5867](https://github.com/timerloggedout-spec/termux-monorepo/pull/5867) · [POLICY.md](POLICY.md) · [REGISTRY.json](REGISTRY.json).
- **Siglary mandate:** [PR #5879](https://github.com/timerloggedout-spec/termux-monorepo/pull/5879).
- **Channel access and route resilience:** [PR #5878](https://github.com/timerloggedout-spec/termux-monorepo/pull/5878).
- **Source authority:** registry rows, protocol docs, and append-only stores establish channel facts; PRs record proposed/accepted repository changes according to their current GitHub state.

## Artifact relationship pattern

For each new work topic, add a compact route in this order:

1. **Concept:** the problem, capability, or design domain.
2. **Channel:** the registered FLY ID and exact protocol/store path carrying the work.
3. **Canonical documents:** specifications, runbooks, architecture records, or source reports.
4. **Work tracking:** issue, proposal item, and PR with current state.
5. **Implementation:** exact repository paths and immutable commit SHAs.
6. **Verification:** test paths/commands and SHA-bound workflow/check evidence.
7. **Consumers:** downstream systems, reports, or surfaces that consume the result.

Use `verified` for explicit references or source/API evidence, `candidate` for bounded similarity or unreviewed hypotheses, and `unknown` when the source record is absent. Keep every artifact link typed and preserve its actual lifecycle state.

## Evidence and freshness

- **Channel facts:** [POLICY.md](POLICY.md), [REGISTRY.json](REGISTRY.json), the channel protocol, and the channel's append-only store.
- **Repository work:** canonical source files, proposal items, GitHub issues/PRs, immutable commits, tests, and current checks.
- **Relationship index:** [Context Relationship Graph contract](../CONTEXT-RELATIONSHIP-INDEX.md) and [committed manifest](../../../workspace/llm_map/context_relationships/manifest.json). The manifest currently reports collection at `2026-10-26`, partial history coverage, and `next_start_page=2`; treat it as a historical metadata snapshot until refreshed.
- **Generated projections:** use as discovery aids and follow their source links. The projection retains the source's confidence and freshness limits.

DO update this hub when a channel scope, topic handoff, canonical artifact, or work lifecycle changes. DO keep the registry and channel stores as the sources of truth.
