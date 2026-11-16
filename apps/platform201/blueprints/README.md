# Platform201 blueprints (fleet-packaged)

Local index mirroring the upstream `shoal-platform/blueprints` README
table format (plan §3 rule 5). One top-level folder per blueprint; inside,
one folder per service (self-contained). No graph manifest — the graph is
assembled in the console from these folders. Deploy status is recorded in
`docs/ops/PLATFORM201-LIVE-2026-10-27.md`, never asserted here ahead of
live evidence.

| Directory | Blueprint | Description | Notes |
|---|---|---|---|
| `catalog-api/` | Catalog API | Read-only API serving this blueprint catalog | Pilot 1 (plan §6.1); packaged, NOT deployed ($-rule §7) |
| _(pending)_ | Planning Queue | 4-service planning queue adapted from shoal-platform/message-queue-demo | Pilot 2; deferred, consumer-gated |
