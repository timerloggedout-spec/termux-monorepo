# Gravitee Self-Host — GitHub Workflows Surface

Owner ruling 2026-10-28: self-host = surfaces reachable via GitHub Workflows,
with resilient mesh redundancy sync, caching, fast boot. (Fleet VM cannot host
APIM: no docker, ~0.5G/7.7G RAM free — verified firsthand.)

## Shape

- Workflow: `.github/workflows/gravitee-selfhost.yml` — `workflow_dispatch`
  (+ weekly Mon 05:17 UTC boot-verify). Runner: `ubuntu-latest`.
- Compose: `ops/gravitee/docker-compose.selfhost.yml` — trimmed variant of the
  vendor quick-setup (gravitee-io/gravitee-api-management/docker/quick-setup/
  mongodb, Apache-2.0): mongodb + elasticsearch (single-node, 512m heap) +
  management_api + **gateway ×2** + mock-upstream. No Console/Portal UI, no
  mailhog (fast boot).
- Surfaces in-runner: mAPI `localhost:8083`, gateways `localhost:8082` +
  `localhost:8092`.

## Fast boot

- Image tarballs in Actions cache (`gio-images-<compose-hash>-<version>`):
  `docker load` on hit; pull + `docker save` on miss.
- Storage healthchecks gate API services (`depends_on: service_healthy`).
- mAPI readiness polled (10s × 72 max) instead of fixed sleeps.

## Mesh redundancy + sync

- Both gateways read the same Mongo repository; a deployment lands on both.
  `scripts/gravitee/ci_verify.py` requires **both** `:8082/mesh-echo` and
  `:8092/mesh-echo` to return the mock body before passing.
- Sync-in: repo seeds (`ops/gravitee/mesh-echo-api.json`) imported each boot
  via the connector helper (create-if-absent, idempotent).
- Sync-out: `api-export` saved to `gravitee-state/` → Actions cache
  (`gravitee-sync-` restore-keys) + artifact on failure. Ephemeral runs hand
  state forward; nothing is committed (mesh-poll pattern).

## Verification chain (ci_verify.py)

Default admin (vendor-documented `admin`/`admin`, fresh ephemeral instance
only) → `GET /management/user` → PAT minted via v1 tokens resource
(`POST /management/organizations/DEFAULT/users/{id}/tokens`, never printed or
persisted) → real connector helper (`docs/ops/gravitee-connector/gravitee.py`,
stubbed credential module in-process) runs ping/apis/create/plan/publish/
start/readback → dual-gateway data-plane proof → export.

## Limits

- Ephemeral: the instance dies with the job. This is a boot/verify/sync
  surface, not a persistent public gateway. A persistent surface needs an
  always-on host (owner infrastructure) — the same compose + helper apply
  unchanged, with the PAT registered in `custom.gravitee` via the vault.
