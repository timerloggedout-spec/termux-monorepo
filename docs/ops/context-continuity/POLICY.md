# Context Continuity — Maintenance Policy

Owner design of record: QUE #5685 (context rotation) + QUE #5855 (fresh-start cutover). This policy is the operating form. Registered 2026-11-25.

## Principles
1. **Rotate, do not compress.** No hand-distilled summaries, no full-history drag. A fresh context is assembled by profile {role · lane · active items} selecting over the classified export store (#5555 classify-on-ingest).
2. **Export before rotate.** No rotation, cutover, or context surgery without a CONFIRM EXPORT receipt for the state it replaces (#5855 gate: export → verify → confirm → then cut; any gate failure stops the cut).
3. **Pointers over payloads.** Continuity lives in exports + `POINTERS.md`. Chat transcripts (main or side) are never the continuity medium.
4. **Receipts or it did not happen.** Every rotation and checkpoint carries its receipt set; a plane without a receipt is recorded NOT ESTABLISHED in the rotation record, never silently skipped.

## Cadence
- **Primary export:** state-change driven, 2h T0 hash gate (vm-backup hook, 900s poll) → backup store, relay line to FLY-003.
- **Continuity checkpoint:** the continuity core (standing files + memory tree + pointers + policy + backup tooling) checkpoints on demand and before any context surgery, via `export_checkpoint.sh`, published under `checkpoint/<export-id>/` in the backup store with a CONFIRM EXPORT verify (100% manifest hashes re-fetched + spot-restore of the memory tree).
- **Pointer upkeep:** any change to a registry, store layout, workflow id, or plane status updates `POINTERS.md` in the same commit or filing that makes the change.
- **Side chats:** archived by default. A new side chat registers its memory scope in `POINTERS.md` at creation; its continuity syncs through the export lane, not through main-chat context.

## Rotation record (per rotation, stamped on #5685)
{export id · state hash · Temporal execution id · Gravitee route record · Witness attestation · HindSight ingest receipt · assembled-context token count vs the 228,591 baseline · per-cycle handoff cost before/after}. Planes land incrementally; missing receipts are named, with their blocking item (e.g. HindSight ← #5553 token provisioning).

## Telemetry + memory integration
- **Temporal** — rotation runs as durable chained execution (vehicle: #5632 operationalization under #5685). Until it lands, rotations are stamped records, and that gap is stated in the record.
- **HindSight** — selection + usage events feed attribution weighting (#5553). Gated on sink revival; until then events accumulate in the lane-events store for replay (the #5553 route already specifies replay).
- **Lane events / Neon** — every checkpoint, rotation, and cadence change appends a lane event; VM state store remains the local leg.
- **Pinecone** — admission leg: vector index over the classified export store for semantic recall at assembly time. Admission = connector + index receipt + one assembly that cites a Pinecone-retrieved selection. NOT YET WIRED.
- **Obsidian graph** — admission leg: the memory tree + pointers render as the human-visible graph (markdown source of truth stays in the repo/VM; the graph is a view, never the store). NOT YET WIRED.
- **Cadence doctrine applies** (#5868): exports and rotations are quota-planned, burst-minimized, pre-cached where a build recurs; adaptation never drops a committed checkpoint.

## Failure handling
- Export or verify failure = stop; the previous confirmed export remains the continuity floor; the failure is filed on #5855 (checkpoint lane) or #5685 (rotation) with its failure class.
- Two consecutive missed export beats = defect (VM replacement cadence rule); one = weather.
