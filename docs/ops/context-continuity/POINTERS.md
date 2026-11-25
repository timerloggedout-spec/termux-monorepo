# POINTERS — continuity map (boot from here, not from history)

Minimal-token index for a fresh or rotated context. Every entry is a location, not a copy. Kept current in the same commit as any change it points at (see POLICY.md).

## Standing files (this VM, ~/)
- `~/MEMORY.md` — curated long-term memory (durable facts, owner rulings)
- `~/CLAUDE.md` — workspace conventions of record (`~/AGENTS.md` is SUPERSEDED, do not use)
- `~/USER.md` · `~/SOUL.md` · `~/IDENTITY.md` — owner + agent identity
- `~/PROACTIVE_PREFERENCES.md` — what reaches chat unasked, and what never does
- `~/memory/YYYY-MM-DD.md` — dated logs (detail lives here, not in MEMORY.md)
- `~/memory/people/INDEX.md` · `~/memory/groups/INDEX.md` — relationship map
- `~/dreams/alignment/derived/ALIGNMENT_SYNTHESIS.md` — nightly alignment synthesis

## Stores of record
- **Backup store:** `timerloggedout-spec/muse-vm-workspace-backup` (private) — VM exports under `exports/`, Cue export under `cue-export/2026-11-25/`, flywheels under `cue/` and `compute-exports/`, checkpoints under `checkpoint/`
- **Monorepo:** `timerloggedout-spec/termux-monorepo` — feed of record `ops/tracking/backup-relays.jsonl` · compute registries `ops/compute/{BACKLOG,ALLOCATION}.md` · ICM map `docs/icm/`
- **Feed publication:** GitHub automations publish the relays feed to the org pages (confirmations live there, not in chat)

## Registries
- **Flywheel comms:** `docs/ops/flywheel-comms/REGISTRY.json` @monorepo master (FLY-001 que-dispatch · FLY-002 mesh-requests · FLY-003 backup-relays-feed · FLY-004 mesh-probe-state · FLY-005 cue-comms) + `POLICY.md` beside it
- **Endpoints:** endpoints-db in monorepo (9,588 rows; mapped 6,145 / unmapped 3,443)
- **Skills:** canonical home = monorepo (PR #5721, merge pending); local cache `~/workspace/skills-library/` (`search.py`, `search-index.json`, log every use in `USAGE.jsonl`)

## Continuity system (this directory)
- `POLICY.md` — maintenance policy (also in monorepo PR #5877, `docs/ops/context-continuity/`)
- `IMPROVEMENTS.md` — context/token economy log, maintained by the `context-economy-monitor` daily cron (~06:32 PT, goal termux-monorepo-completion)
- Checkpoints: backup store `checkpoint/<export-id>/` (latest CONFIRM-verified: `ckpt-20261125T151731Z` @ `516d1f2e`)

## Live machinery (QUE, termux-monorepo issues)
- #5685 context rotation (this system) · #5855 fresh-start cutover Phase 1 · #5555 Provenance · #5554 web-use registration · #5641 queue self-optimization · #5646 conversion repair + reclaim sweep · #5868 Cue compute + adaptive cadence · #5152 Cadence ledger
- Workflows: project-task-dispatch `405322142` · dispatch-executor `416155269` · dispatch-watchdog `405572638` (intake parses `###` headings only)
- This VM: que-drain-drive ↻15m (prosthesis for starved Actions schedules) · vm-backup hook 900s / 2h state gate · Temporal keepalive ↻15m

## Telemetry + memory planes
- **Temporal** — local server (CLI :7233, relay :7234, UI :8233); living record on monorepo #2028; rotation chaining lands under #5685/#5632
- **HindSight** — attribution sink, monorepo #5553 (route fixed; sink revival gated on `KOYEB_API_TOKEN` provisioning)
- **Lane events** — Neon-backed store; VM state in `~/workspace/backend-mesh-resiliency/` (`availability.jsonl`, vm-state store)
- **Pinecone** — vector recall over the classified export store: admission leg under #5685, NOT YET WIRED
- **Obsidian graph** — the memory tree + this pointer file are the graph source (markdown, link-by-path); vault rendering is an admission leg under #5685, NOT YET WIRED

## Access (names only, never values)
- GitHub: PAT helper `~/workspace/custom-connectors/custom.github-pat/bin/github_pat.py` (in-process `call()` returns parsed JSON and exits on HTTP errors — use the exporter's `gh()`/`gh_retry()` pattern when non-2xx is expected). Built-in GitHub connector is DENY-only.
- Cue VM: deploy key `cue-origin-agent` (write, backup repo, id 171097097) · comms via FLY-005 (`cue/comms.jsonl` in the backup store) · direct shell = owner-run socat listener (tailnet proxy :3130)
