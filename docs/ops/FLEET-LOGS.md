# Fleet Logs — separate append-only logs repo

**Repo:** [`timerloggedout-spec/fleet-logs`](https://github.com/timerloggedout-spec/fleet-logs) (public, created 2026-10-30, owner order; plan + decisions `[MUSEai]@{role:{certifications}}`)

## Why

Append-only machine logs churn this repo's history (refresh-PR cycles, rewrites of large state-adjacent files). Machine-written log streams get their own repo with a clean, append-only audit history; everything authored or consumed in place stays here.

## What lives there

Per its `manifest.json` (fleet-logs-manifest/v1):

| Stream | Status |
|---|---|
| Challenge OSINT snapshots + coverage (`osint/challenge/`) | **mirrored-pilot** — byte-exact copies; blob shas match source (snapshots `136492ab9d6d`, coverage `49a8aa303ee6`) |
| Telemetry / Provenance / HindSight ledgers (`telemetry/`) | pending-landing — ingest built 2026-10-28, not yet on master; outputs home there when landed |
| Certification raw artifacts (`certifications/`) | ready-empty — receipts/notebooks land there; the cert index stays here |

## What stays here (do not move)

- `ops/challenge/coordinator.json` — state, not a log; gates consume it in place (entries lane single-writer)
- `docs/ops/CHALLENGE-ENTRIES-LOG.md` — authored log
- `apps/help-wanted-dashboard/data/delphi-ledger-feed*.json` — consumer-bound; the live dashboard reads them in place
- Roadmaps, Role Requirements Plans, ICM knowledge objects, `LEARNINGS`, `SKILL.md` — authored knowledge/definitions, context-bound to the code
- Certification index (cert ID / date / verify link in `guides/certifications-*` + issue #506) — public verifiability lives in the docs

## Rules

- Until a stream's manifest status reads `cutover`, **this repo is the source of truth** and fleet-logs is a mirror.
- Cutover = the owning lane changes its writer workflow + a fresh mirror refresh; a separate decision per stream, recorded in the manifest.
- fleet-logs is public-data only, append-only: corrections are new entries, never rewrites.
