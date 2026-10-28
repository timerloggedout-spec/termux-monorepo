# catalog-api — Platform201 blueprint (Pilot 1)

Read-only catalog API: serves the fleet's Platform201 blueprint index as
JSON. Bounded Pilot 1 service per `docs/ops/PLATFORM201-BLUEPRINT-ADAPTATION-PLAN.md`
§6.1/§6.4. **Packaged only — NOT deployed** (owner $-rule, plan §7: deploy
stays frozen until credit intake is obtained).

## Graph table (console assembly order)

| Directory | Node type | Name | Binding / setting |
|---|---|---|---|
| `api/` | container | api | Python 3.12 (Dockerfile), port 8080, env: `PORT` only |
| — | gateway | gateway | `GET /` → api (all paths; service is GET-only) |

No queue, no database, no scheduler, no secrets. Data is bundled
(`api/blueprints.json`); the repo is the source of truth (§6.2 export rule).

## Runtime policy (plan §6.4, declared)

environments 1 · services 1 · billing request-based · min instances 0 ·
max instances 1 · task timeout 60s · max attempts 2 · external model calls
per task 0 · writes disabled (non-GET → 405). Region europe-west2
(platform-chosen in managed mode).

## Endpoints

- `GET /health` → `{"status": "ok", "service": "catalog-api"}`
- `GET /blueprints` → full catalog
- `GET /blueprints/{id}` → one entry, 404 JSON otherwise

## Task record (plan §6.5)

Not task-bearing: read-only, no submissions, no state. §6.5 task record
(idempotency/lease/checkpoint) lands with the first task-bearing service
(Pilot 2, planning-queue).

## Benefit statement (plan §3 rule 4 — required before any deploy)

Benefit: proves the blueprint packaging → console graph assembly → deploy
pipeline end-to-end on a real (if small) fleet artifact at $0 observed
metering, and gives lanes a machine-readable catalog of what blueprints
exist and their status instead of doc-diving. De-risks Pilot 2
(planning-queue) packaging, whose template this validates.

Kill criterion: comes down if no lane has consumed `/blueprints` by the
time Pilot 2 packaging starts, or if Usage metering exceeds $0.00
attributable to it (plan §6.3 threshold review).

## Local validation

`cd api && python3 -m unittest test_server` — 5 tests (health, catalog,
single entry, 404, writes-disabled 405).
