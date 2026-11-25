# Central Flywheel Navigation — Design

**Date:** 2026-11-25  
**Proposal item:** REPO-ARCH-007  
**Status:** implementation design  
**Owner:** Repository Architecture / ICM

## Intent

Give every collaborator one central, nested navigation entry for the repository's Flywheel system. A reader starts from the hub, selects a channel or work topic, and follows direct links to the authoritative artifacts behind it: protocol, append-only store, concept, source document, issue, pull request, commit, test, and validation evidence.

The hub serves human and agent navigation. It makes the existing work graph discoverable while message payloads and source-system authority stay in their canonical stores.

## Goals

- Publish `docs/ops/flywheel-comms/README.md` as the central Flywheel navigation hub.
- Enumerate the registered channels FLY-001 through FLY-006 from the canonical registry.
- Preserve channel scopes and boundaries:
  - FLY-005: exports and backup coordination.
  - FLY-006: general work pair channel, including incidents, PR review, mappings, notation, and fleet coordination.
  - FLY-003: confirmations of record.
- Make the FLY-005 pointer at 2026-11-25T19:28:30Z resolve directly to FLY-006's work-comms protocol and append-only store.
- Organize cross-channel work by topic, then link its source concept, channel, canonical documents, GitHub work records, commits, tests, and evidence where those records are verified.
- Route root architecture and ICM navigation through the hub.
- State source authority, confidence, and freshness so readers can tell canonical records from derived indexes and candidate relationships.

## Scope boundaries

- Keep channel identity, membership, and lifecycle under their registered owner seats.
- Keep FLY-005/FLY-006 appends, message delivery, and participant cadence under their existing channel owners.
- Link JSONL stores while message bodies remain in their registered repositories.
- Reuse the existing channel transport, relationship graph, and cadence machinery.
- Treat GitHub PR status, a dashboard projection, or the Context Relationship Graph as the source of truth for a channel.
- Keep THUB-011 checker implementation as a separately authorized work item.

## Verified starting state

- `docs/ops/flywheel-comms/REGISTRY.json` contains established FLY-001…FLY-006.
- FLY-005 is `cue-comms`, backed by `timerloggedout-spec/muse-vm-workspace-backup/cue/comms.jsonl` and `cue/COMMS.md`; its scope is exports and backup coordination.
- FLY-006 is `cue-work-comms`, backed by `cue/work-comms.jsonl` and `cue/WORK-COMMS.md`; its scope is general pair work beyond export operations.
- The FLY-005 line at 2026-11-25T19:28:30Z points to the full research, test record, and adaptation map on FLY-006.
- FLY-006 carries the sidecar/overlay adaptation record and links to monorepo PR #5893 and `docs/linguist/FLY-006-SIDECAR-OVERLAY-ADAPTATION.md`.
- FLY-006 also carries the Siglary/Linguist work record referencing PR #5299, the PDDL example, Matrice tooling, and its tests.
- `docs/icm/cards/flywheel-comms.md` still names only FLY-001…FLY-005 and is stale relative to the registry.
- The committed Context Relationship Graph manifest reports collection at 2026-10-26, partial history coverage, and `next_start_page=2`. It remains a metadata-only evidence index and requires refresh before current-history claims.

## Approaches

1. **Extend only the ICM card.** Lowest change cost; the card remains a shallow route and the nested artifact directory stays unserved.
2. **Dedicated Flywheel hub with ICM and architecture entry links — selected.** The hub owns curated channel/topic navigation; existing registry, channel stores, docs, GitHub, commits, and tests remain canonical while the hub supplies the central entry.
3. **Generated graph/UI as the primary navigation.** Deferred. The existing graph is metadata-only, stale, and historically incomplete; using it as the primary directory would misstate freshness and conflate navigation with evidence collection.

## Navigation model

The hub has two top-level branches:

- **Channels:** one route per registered FLY ID, showing purpose, owner, participants, cadence, store, protocol, and relevant cross-channel boundaries. Registry values remain canonical.
- **Topics:** curated routes for work that crosses channels. Each topic follows the same relationship spine:

  `concept → channel(s) → canonical source docs → issue/PR → commit(s) → tests/checks → downstream consumer`

Each link is labeled by artifact type. Classify missing or unverified relationships as `unknown`; classify bounded heuristics as `candidate`.

## Source authority

1. Channel registration and scope: `REGISTRY.json`.
2. Channel message schema and operating rules: each channel's protocol document.
3. Message history and pointer events: append-only JSONL in the registered store.
4. Implementation and technical facts: canonical repository source, tests, and exact commit.
5. Work lifecycle: GitHub issue/PR and immutable SHA-bound checks.
6. Navigation: this hub and its entry-point links.
7. Context Relationship Graph: supplemental metadata-only relationship evidence; preserve its confidence labels and freshness bounds.

## Constraints

- Preserve append-only channel history and existing FLY IDs.
- Keep FLY-005, FLY-006, and FLY-003 scopes distinct.
- Use explicit GitHub URLs and full repository paths for durable links.
- Link to source stores; keep message bodies in their registered store.
- Use verified/candidate/unknown distinctions for relationship claims.
- Keep the hub curated and concise; link deeper rather than cloning full documents.
- Keep repo-wide Siglary/DO-first communication policy in force for Flywheel messages and repo-owned communications.
- Limit edits to navigation, architecture pointers, and proposal records.

## Acceptance

- The hub lists all six registered channels and links each to its canonical registry row/store/protocol where applicable.
- FLY-005's pointer to FLY-006 is directly visible and resolves to FLY-006 protocol/store and the linked work record.
- Topic routes connect at least the verified export/telemetry, Siglary/notation, and sidecar/overlay work to their documents, PRs, commits, and tests.
- Root `architecture.md`, `docs/icm/CLAUDE.md`, and the ICM Flywheel card route to the hub.
- All local links resolve; external links use exact known repository paths and GitHub IDs.
- DO keep JSONL payloads in their registered stores and relationship evidence in the existing graph.
- Documentation checks, proposal validation, repo gate, Termux smoke, and required PR checks are recorded against the same candidate SHA.
