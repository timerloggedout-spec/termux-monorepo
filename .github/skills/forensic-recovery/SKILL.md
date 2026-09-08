# Forensic Recovery Skill

## Purpose
Recover repository material without confusing deletion, rollback, supersession, or generated evidence.

## Classification
Every removed path is classified as one of: authoritative source, generated evidence, intentional replacement, archival/historical, or unknown.

## Safe procedure
1. Record base/head SHAs and exact path set.
2. Preserve recoverable blobs and provenance before cleanup.
3. Compare ancestry and content, not filenames alone.
4. Restore only evidence-backed material.
5. Stop on conflicts or ambiguous intent.
6. Validate restored material against canonical tests and indexes.
7. Record replacement/supersession links.

## Forensic adapters
ArchWiz, Perfect Trunk Builder, fragment matcher, reverse-pointer indexes, Chrono/time-loop evidence, and ML replay preservation may implement this contract. No adapter may force-push, rewrite history, or invent historical telemetry.
