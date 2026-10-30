# GitHub App fleet telemetry proposal

Status: comparative proposal on branch proposal/github-app-telemetry-fleet-registry. This is not a live permission audit.

## Purpose

Make provisioned GitHub Apps discoverable even when they emit no check suites, comments, or pull requests. Keep checked-in declarations, observed installation state, effective permissions, runtime health, and quota measurements as distinct evidence classes.

## Proposal contents

- ops/github-apps/registry.json: non-secret app identity, purpose, manifest/profile pointers, declared permissions/events, expected installation scope, and promotion gates.
- scripts/github/github_app_telemetry.py: validates the registry and emits timestamped, evidence-labelled JSON. Optional installation-token probes record rate-limit fields and repository names; the token itself is never serialized.
- scripts/github/test_github_app_telemetry.py: validates declaration-vs-observation, duplicate slugs, invalid permission values, successful probes, and failed probes.
- .github/workflows/github-app-telemetry.yml: runs tests on pull requests and uploads a 30-day declaration-only artifact.

## Data contract

Each app should ultimately include stable identity, declared permissions, observed permissions, expected and observed repository scope, provisioning state, token-mint outcome, workflow run ID/attempt/SHA, duration/conclusion, API request counts by status/route class, rate-limit remaining/reset, drift, source reference, evidence reference, and confidence.

Every field must distinguish unknown from empty. A 403/404 or missing credential is not proof of absence. Missing sections are degraded/unknown, not removals.

## Security invariants

1. Never collect, print, cache, upload, or commit private keys, JWTs, installation tokens, PATs, raw authorization headers, secret values, or token-bearing URLs.
2. Secret-store census remains names-only.
3. Mint short-lived installation tokens at runtime from protected app credentials; never store a long-lived installation token as an Actions secret.
4. Keep the pilot read-only. Do not add webhook or write permissions to solve an observability gap.
5. Treat manifests as declared state and GitHub API reads as observed state, with timestamps and provenance.
6. Do not automatically revoke, rotate, uninstall, or broaden permissions in response to drift. Alert and open review work instead.

## Rollout

### P0 — inventory and proof
- [x] Add non-secret app registry.
- [x] Add telemetry serializer and unit tests.
- [ ] Run tests in Actions and review results.
- [ ] Wire telemetry into integration-mesh snapshot/diff with backward-compatible cache handling.
- [ ] Verify active installation and repository scope with a freshly minted installation token.
- [ ] Read back effective installation permissions and compare with manifest declarations.
- [ ] Capture run ID, token-mint outcome, quota before/after, API status counts, and artifact reference.

### P1 — drift and quota attribution
- Add a reachable webhook receiver only when a protected webhook secret is ready. Subscribe minimally to installation and installation_repositories, verify signatures, deduplicate delivery IDs, and record permission and repository-scope changes.
- Reconcile webhook events against periodic API observations.
- Prove a real app-token batch does not reduce the owner PAT bucket.

### P2 — fleet expansion
- Require each app repository/lane to publish a machine-readable registry fragment and public capability/readme page; link it from the hub registry.
- Preserve owner/installation boundaries and do not expose private repository names in public artifacts.
- Add retention, deletion, opt-out, health, and support policies before external-install promotion.
- Keep collector, reviewer, and publisher as separate least-privilege trust boundaries.

## Collaborator lanes

- Integration Mesh / Muse: inventory and snapshot diff; standing issue #1505.
- Quota Specialist, quota convergence, cadence optimizer, quota gaps: use measured app-vs-PAT API spend as a meta-pool input.
- GitHub App provisioning: update registry when an app is created, installed, re-scoped, or retired.
- Research-Astute and search-astute-ly: publish registry fragments in each app's home repository.
- Future app repositories: link this hub document and add their registry pointer to the hub.

## Acceptance criteria

A read-only collector appears without producing a check suite or comment; output labels declarations versus observations; failures are visible without credential disclosure; repo scope and effective permissions can be compared; old cache snapshots do not produce false removals; tests pass; scheduled telemetry emits an artifact; and a real token batch demonstrates quota attribution.

This branch remains separate until comparative review and explicit merge.
