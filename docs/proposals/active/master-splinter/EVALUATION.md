# Master Splinter — Reconciliation Evaluation

[MUSEai]@{role:{appid-migration-plan}} · 2026-11-03 · verdict: **ADAPT — control plane over the existing family; NOT a replacement identity, NOT a 9th App under this brief**

## Evidence per point (fleet state of record)

1. **The "one reusable app" premise collides with a deliberate design.** The fleet runs **8 specialist AppIDs** (SSOT `ops/github-apps/PROCESS.json`): Collector 5535733 · Publisher 5537873 · Reviewer 5539430 · Gate 5539499 · Lifecycle 5539639 · Swarm 5560920 · CrossReference 5564430 · RepoStory 5565297 — each with its own 5,000/h bucket, least-privilege manifest, and separate custody (plan `docs/ops/GITHUB-APP-MIGRATION-PLAN.md` §1/§3). Collapsing to one App merges buckets, erases per-function attribution (a weighted fleet signal), and repeals the design of record. The author's own text preserves separate Apps where isolation justifies ⇒ the compatible reading is the one ADAPT takes: Splinter = control plane (inventory · permission snapshots · replay lineage · usage join), identity stays plural.
2. **The gap it names is real.** No unified control surface exists today: inventory lives in PROCESS.json + `ops/github-apps/registry.json` + per-connector custody; the permission-drift audit (MAINT-01) is unbuilt; migration lineage lives in `MIGRATION-ITEMS.md` + PR trail; usage truth is split across the app-telemetry emitter, QUE, and quota censuses. A read-only control plane over those is a genuine missing layer, and inventory-first matches the brief's gates.
3. **api_usage overlap — one telemetry of record.** The proposed `api_usage_events` store duplicates two standing planes: **QUE** (PR #4624, owner mandate — queue system whose ADMISSION leg generalizes the PAT flow-governor = the fleet's usage-measurement plane) and the github-app-telemetry emitter (app-side census of record, TEL-03 closed 2026-11-02). Rule: Splinter **consumes** QUE + telemetry receipts + lane-events; it never writes a parallel usage store. Its schema survives as a **join/view spec** (see SPEC.md), not a table of record.
4. **Webhook/cache sync overlap — map, don't duplicate.** Event capture already lands in the **lane-events Neon store** (project dawn-breeze-73523999; rows verified live 2026-10-28) fed by recorder workflows, with integration-mesh polling on top. Splinter's sync = read model / cache over those stores. A new webhook receiver fleet is out of scope (receiver surface changes are separately gated fleet work).
5. **Replay overlap — planes stay separate.** Repo Replay and Commit Replay own their engines and stores (replay-store/v1 ≁ commit-store/v1, no index merge). Splinter's "replay" is scoped to **migration dry-run replay**: re-execute a recorded migration wave against an inventory snapshot in simulation (no write tokens minted), diff vs the recorded outcome, emit a G4-shaped receipt. That is a control-plane function; it absorbs neither replay system's engine or store.
6. **Access route.** The canonical route today = vault PAT helper (fallback) + per-App installation tokens (primary). The control plane reads via Collector (read-only ×6) — no new credential, no cutover, consistent with the brief's gates.
7. **Name.** Unruled. Registry consulted 2026-11-03 (submission 87294247): TMNT/trademark + tone vs moniker discipline · "master" vs master-branch ambiguity · family label `github-appid-v1`. Until the ruling: attributed use in this intake only.

## What ADAPT changes vs the proposal as relayed

- Standalone repo + own App: **deferred to owner gate** (not created; control plane starts as spec + inventory read-model inside existing surfaces).
- App permission manifest: **none new** — control plane is software over Collector reads; any future write need routes to the existing family App for that function.
- DB schema: kept, demoted to read-model/join over lane-events + telemetry + PROCESS snapshots (SPEC.md).
- Dry-run replay contract: kept, scoped to migration waves (point 5).
