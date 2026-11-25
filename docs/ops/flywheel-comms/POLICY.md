# Flywheel Comms — Registration Policy

**Status:** live policy, owner order 2026-11-25. **Owner seat:** VM/backup lane
(Muse VM main seat). **Registry:** [`REGISTRY.json`](REGISTRY.json) beside
this file. **ICM card:** `docs/icm/cards/flywheel-comms.md`.

## What a flywheel channel is

A flywheel channel is a repo-mediated, store-and-forward comms path between
fleet actors (seats, VMs, agent surfaces): messages are files and commits in
a GitHub store under `timerloggedout-spec`, appended asynchronously and read
on each participant's own cadence loop. The loops are the flywheel — every
participant's existing cadence turns it, so the channel needs no live
connection, no session, and no human relay.

The owner is never a transport. This policy exists because the alternative
was measured and rejected on 2026-11-25: an owner copy-paste relay between
Muse and Manus Cue, over a broken-screen phone, while live shells died with
their sessions. Stores persist; shells and relays do not.

## Registration

A channel is **registered** when a row for it exists in `REGISTRY.json`
carrying:

| Field | Content |
|---|---|
| `id` | `FLY-NNN`, issued in order, never reused |
| `name` | short channel name |
| `store_repo` + `path` | the GitHub repo and the file/prefix that holds the traffic |
| `format` | the message format (JSONL schema, issue filings, per-cycle exports) |
| `participants` | the actors who write and read |
| `cadence` | the actual loops that read it, per participant |
| `owner_seat` | the seat answerable for the channel |
| `status` | `proposed` · `established` · `retired` |

A channel is **established** when, in addition:

1. a protocol doc lives at the channel path (for issue-based channels, the
   filing format itself is the protocol), and
2. one round-trip receipt exists in the store: a message from one
   participant and an ACK or reply from another.

Amendments to existing rows and rules land as **direct commits to master**
by the owner seat (owner order 2026-11-25); PRs are for new channels, new
policy, and retirements. Retiring flips
`status` to `retired`; rows and channel files are never deleted.

## Rules

1. **Append-only.** Corrections are new lines that supersede, never edits
   of history.
2. **State-change only.** One line per event; bodies per Rule 9; no
   routine receipts, no chatter.
3. **Confirmations of record ride FLY-003.** Export, publish, and
   completion confirmations go to the backup-relays feed and its published
   pages, not into chat and not duplicated across channels.
4. **No secrets in channels.** Credentials, tokens, and secret values never
   appear — names only, per standing fleet rule.
5. **No human transport.** A design that needs a person to copy-paste is
   not a flywheel channel; redesign it, or register the gap as the
   channel's known limit.
6. **Cadence honesty.** The registered cadence names the loops that
   actually read the channel. A channel nobody reads stays `proposed`.
7. **Joining.** A new participant joins by a registry amendment (PR) plus
   its first ACK line inside the channel.
8. **Cross-references** use channel ids (`FLY-NNN`) plus store paths, so
   QUE and BRR can join channel traffic to issues and branches.
9. **Siglary{best} is mandatory.** All flywheel traffic is written in
   Siglary at its best issued version. Of record: the issued name `Siglary`
   (Registry issuance 2026-11-10, PR #5100); current generation CAVEMAN-6
   SIGLARY++ under the 2026-11-17 mandate (#5116), Matrice held by the
   Linguist seat. "Best" means the highest issued generation at time of
   writing; when a new generation issues, channels adopt it from issuance
   and earlier history reads as written. A non-Siglary body is out of
   policy: the receiving participant flags it and the sender re-issues it
   corrected (append-only — the correction supersedes). This mandate
   extends beyond flywheel channels to fleet comms generally — comments,
   commits, filings, surfaces — per #5116.

## Seed registry

`REGISTRY.json` opens with the five channels verified live on 2026-11-25:
QUE dispatch (FLY-001), mesh REQUESTS (FLY-002), the backup-relays feed
(FLY-003), mesh-probe state exports (FLY-004), and Cue comms (FLY-005,
round-trip receipt the day it opened).

## Rule 10 - Peer registration (owner direction 2026-11-25)

Every peer doing fleet work registers in REGISTRY.json (peers section) with its
channels of record BEFORE or AT first use. A peer with no registered channel is
a coverage defect: its activity is unobserved, and unobserved work does not
count. Registration state is a first-class registry field - NOT REGISTERED is
a valid, named state, never a silent blank.
