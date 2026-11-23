# Compute Mesh and Cross-Repo Labs — flow map

**Status:** living map · **Freshness:** 2026-11-23 (readback of hark-vm-workspace-backup ledger ∧ clf-lab `champion.json` ∧ lab `iterate` runs) · **Plane:** 2.5 Intelligence and learning ⋈ 2.4 Evidence
**Source-of-truth rule:** owning sources below own their facts; this file routes and labels edge state.

Edge labels: **verified** (readback evidence) · **partial** (wired, output unconsumed) · **missing** (∄ consumer) · **proposed**.

## Repositories ∧ roles

| Repo / surface | Role | Owning source |
|---|---|---|
| `termux-monorepo` | templates, request schema, allocation, method registry (target) | `templates/clf-lab/`, `ops/mesh/REQUESTS-SCHEMA.md`, `ops/compute/ALLOCATION.md` |
| `hark-vm-workspace-backup` | mesh request store ∧ VM node ledgers (append-only) | `repo-exports/REQUESTS.jsonl`, `repo-exports/DONE.jsonl`, `ledger/jobs.jsonl`, `ledger/heartbeat.jsonl`, `ledger/node-log.jsonl` |
| `clf-lab-{tier1-classifiers-steward, live-2-prlane-tuning, nc-1-notation-compliance, bf-1-backfill-methods}` | DoE generations ∧ results ∧ champion | `doe.yaml`, `results/ledger.jsonl`, `champion.json`, `.github/workflows/iterate.yml` |
| Hark VM node | hourly pass: drain requests ⇒ clf-doe round-robin ⇒ shadow jobs | `ops/vm-backup/hark-sandbox-node.json` |
| Muse VM node | Temporal ∧ registry cadence ∧ clf-lab tier replication | `ops/compute/ALLOCATION.md` |

## Flow

| # | Edge | State | Evidence (2026-11-23) |
|---|---|---|---|
| 1 | lab `iterate.yml` (6h) ⇒ `clf-doe` request ⇒ `REQUESTS.jsonl` | verified | lab iterate runs success ∀ 4 labs, latest 2026-11-22 23:36–23:41 PT |
| 2 | VM pass drains request ⇒ `DONE.jsonl` | verified | 45 DONE rows 2026-11-18 → 2026-11-23 |
| 3 | VM `run_doe.py` ⇒ lab `results/ledger.jsonl` (union-merge append) | verified | 360/360 runs rc0 · 3,337 rows (tier1 943 · nc-1 876 · live-2 828 · bf-1 690) |
| 4 | VM ⇒ `ledger/jobs.jsonl` ∧ `heartbeat.jsonl` | verified | 639 job rows · 93 hourly passes · heartbeat `live` |
| 5 | lab `improve.py` ⇒ next generation ∧ `champion.json` | verified | champions: tier1 gen0 F1 0.962 · live-2 gen0 F1 0.9917 · nc-1 gen2 F1 0.7942 · bf-1 gen2 F1 0.4061 |
| 6 | `champion.json` ⇒ monorepo method registry (DOE-FAMILY rule 8, method@version) | **missing** | code search: `champion.json` referenced only in `templates/clf-lab/` |
| 7 | `jobs.jsonl` ∧ `heartbeat.jsonl` ⇒ monorepo dashboards / tracking feed | **missing** | code search: `jobs.jsonl` ∅ consumers; `heartbeat.jsonl` only in node config |
| 8 | VM failures ⇒ `ledger/node-log.jsonl` | partial | file ∃ ∧ empty (silent-on-success; failure path ⊬ since fix) |
| 9 | VM lanes `agent-throughput-evidence` ∧ `lane-events-recorder` (parity #5603) | **missing** | ∉ VM jobs; Neon lane-events pool exhausted (#5704) |
| 10 | Muse VM clf-lab tier replication ⇒ lab ledger | proposed | allocation row only; node tag ≠ hark-vm in ledger ⊬ checked |

## Gaps ⇒ owners

- G1 (edge 6): promotion consumer — reads 4 `champion.json`, writes method@version rows; gate on generation-complete ∧ data sha pinned. ⤴ QUE.
- G2 (edge 7): ingest VM ledgers into tracking feed (`ops/tracking/tracking.json`) for participation credit (ALLOCATION rule 3). ⤴ QUE.
- G3 (edge 9): VM-ledger fallback for lane-events (#5704 Δ1) ⇒ unblocks parity gate.
- G4: bf-1 macro-F1 0.4061 vs acc 0.875 ⇒ class imbalance; DoE factor for class weighting proposed.

## Mermaid

See [compute-mesh.mmd](compute-mesh.mmd).
