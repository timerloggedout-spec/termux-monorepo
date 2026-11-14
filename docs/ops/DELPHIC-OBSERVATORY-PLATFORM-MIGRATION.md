# Delphic Observatory platform migration

Status: implementation in progress; Vercel Git project linked, Render feed service not yet provisioned.

## Ownership
- GitHub is canonical: source, lane registry, schemas, PRs, issues, Actions receipts and release provenance.
- Vercel serves `site/delphic-observatory` from the monorepo Git connection. Preview deployments are review surfaces.
- Render is the intended feed adapter/cache and scheduled aggregation plane. Do not repurpose existing legacy services: current services include README-only and older staging deployments without an Observatory ownership contract.

## Live feed contract
The UI polls public GitHub REST endpoints for open pull requests and recent Actions runs every 60 seconds. It reports partial/degraded states rather than substituting stale values. Unauthenticated GitHub API rate limits apply.

A Render adapter may be selected by setting `window.OBSERVATORY_API_BASE` before `observatory.js` loads. It implements:
- `GET /healthz` — health, service and schema identity.
- `GET /api/pulls` — normalized PR feed.
- `GET /api/actions/runs` — normalized Actions feed.
- Envelopes include source, observed_at, source_updated_at, source_ref and stale.
- Preserve native IDs and source URLs; never synthesize success.
- Cache public responses with bounded TTL; respect upstream rate limits and return explicit 429/503 states.

## Research lane matrix
The UI matrix is generated from the lane families in `docs/research/LANE-ARCHITECTURE.md`. `lane-registry.json` is a presentation index, not a second authority. Each lane links to canonical architecture; sibling organizations may publish evidence without granting the hub write access.

## Security and authority
Read-only public feeds only. No dispatch, credentials, quota use, paid fallback, wallet mutation, culling, or promotion authority. Do not expose private repository data through a public proxy. A GitHub read token, if ever needed for rate limits, remains server-side and least-privilege.

## Deployment sequence
1. Merge the source PR after required checks.
2. Confirm Vercel root is `site/delphic-observatory`, production branch matches repository default, and public deployment protection is intentional.
3. Provision Render via reviewed Blueprint plan; verify health and response envelopes.
4. Configure Render API base only after health check passes.
5. Verify Vercel production, feed freshness, optional GitHub Pages mirror and rollback.
6. Retire ShipStatic only after production URLs and feeds are verified.
