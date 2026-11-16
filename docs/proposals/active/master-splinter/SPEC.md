# The AppID control plane (proposer title: "Master Splinter" — not adopted, see EVALUATION.md addendum) — Scoped Spec Package

[MUSEai]@{role:{appid-migration-plan}} · 2026-11-03 · status: spec only — no deploy, no repo, no App, no credential movement under this package

## 1. PRD (scoped)

- **Problem:** 8 AppIDs + PAT fallback are operated from flat files (PROCESS.json, MIGRATION-ITEMS) and per-lane memory; no single surface answers: what Apps exist, with what permissions (declared vs observed), which migration wave touched what, and what each identity spends.
- **Product:** a read-only control plane: (a) **Inventory** — Apps, installations, custody pointers (names only), SEC-03 pair presence; (b) **Permission snapshots** — declared (manifest of record) vs observed (installation-token readback), diff = the MAINT-01 drift feed; (c) **Replay lineage** — migration waves (M1–M10, MIG-01..11) as lineage nodes linking plan → PR → run → receipt; (d) **Usage join** — per-App usage view over QUE admission data + telemetry receipts + lane-events.
- **Non-goals:** holding credentials · minting write tokens · replacing any family App · replacing QUE/lane-events/telemetry stores · deploying anything under this spec.

## 2. Technical spec

- Sources of record (read-only): `ops/github-apps/PROCESS.json` · `ops/github-apps/registry.json` · `ops/github-apps/MIGRATION-ITEMS.md` · github-app-telemetry run artifacts · QUE (PR #4624 plane) · lane-events (Neon) · live probes via Collector token (inventory/permissions readback).
- Sync: cache-first read model refreshed by the telemetry cadence + on-demand probe; **no new webhook receivers** (point 4 of EVALUATION.md).
- Every figure carries provenance {source, observed_at, run/receipt ref}; declared ≠ observed kept as separate columns everywhere (registry.json policy).

## 3. DB schema (read model; stores of record stay where they are)

- `app_inventory(app_id, slug, role, installation_id, custody_ref, sec03_pair_present, observed_at)`
- `permission_snapshots(app_id, declared_json, observed_json, diff_json, observed_at, probe_run_ref)`
- `migration_waves(wave_id, items_ref, pr_refs, run_refs, receipt_refs, state)`
- `replay_runs(run_id, wave_id, snapshot_ref, plan_json, simulated_calls, diff_json, receipt_ref, created_at)`
- `usage_events` — **VIEW**, not a table: join over lane-events + telemetry receipts + QUE admission records, keyed {app_id, bucket, window}.

## 4. App permission manifest

- **None new.** Control plane reads with the Collector installation token (read-only ×6) and the PAT helper fallback — the fleet's existing routes. A future write requirement returns as a separate proposal routed to the family App owning that function.

## 5. Dry-run replay contract

- Input: {wave_id ∨ explicit step list, inventory snapshot ref}. Steps: snapshot → plan (ordered calls with bucket attribution) → simulate (no write tokens minted; read probes allowed) → diff vs recorded outcome → receipt (G4 fields: token source, identities, bucket readings, run ref).
- Exit states: MATCH · DRIFT (declared ≠ observed) · UNREPLAYABLE (missing snapshot/evidence) — each with the diff attached. A dry-run never mutates repo, App, or store state.

## 6. Gates

- Build/deploy/repo/App/credential steps: **owner-gated, outside this package**. Inventory-first ordering per the intake brief. Name use beyond attribution: Registry ruling first.
