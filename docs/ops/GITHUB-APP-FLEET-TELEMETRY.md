# GitHub App fleet telemetry — comparative proposal

Status: open comparative PR; declaration telemetry and mesh integration are implemented on this branch. Live token minting and permission readback remain gated.
Related records: `docs/ops/GITHUB-APP-MIGRATION-PLAN.md`, `ops/github-apps/MIGRATION-ITEMS.md`, `ops/github-apps/PROCESS.json`, `ops/quota/registry.json`, and standing integration-mesh issue #1505.

## Objective

Make provisioned GitHub Apps discoverable even when they emit no check suites, comments, or pull requests. Keep checked-in declarations, live installation evidence, effective permissions, runtime health, and quota measurements as distinct evidence classes.

## Implemented on this branch

- `ops/github-apps/registry.json`: non-secret app registry, canonical manifest pointers, expected installation scope, promotion gates, and four role slots reported by the owner as in flight but not independently verified.
- `scripts/github/github_app_telemetry.py`: validates registry structure and derives permissions/events directly from each referenced manifest (manifest is the declared-permission SSOT). Optional manual probes accept an ephemeral installation token; credentials are never serialized.
- `scripts/github/test_github_app_telemetry.py`: tests manifest-derived permissions/events, role-state labeling, duplicate slugs, invalid manifest data, successful/failed probes, and token redaction.
- `scripts/github/integration_mesh_poll.py`: adds the checked-in app registry and manifest declarations to the existing census. Registry changes become structural diffs. Old snapshots without this field remain compatible; unavailable registry data is degraded, never interpreted as removal.
- `scripts/github/test_integration_mesh_poll.py`: tests registry census, change detection, old-cache compatibility, and degraded-state handling.
- `.github/workflows/github-app-telemetry.yml`: PR validation, manual dispatch, and a weekly declaration census artifact.

## Provisioning truth and four in-flight role slots

The owner reports four additional apps are in flight. The registry records role candidates for publisher, reviewer-ops, gate-ci, and lifecycle as `owner_reported_in_flight_unverified`. It deliberately does not invent App IDs, installations, live permissions, or credentials.

**Reconciliation required:** the current `ops/github-apps/PROCESS.json` naming section still marks these candidate slugs as conference draft / DO NOT PROVISION pending naming conference and owner close. The provisioning/AppID lane must reconcile that record before any candidate slug is treated as final or any workflow begins minting tokens. This telemetry registry is not permission to bypass that gate.

## Evidence contract

- `checked_in_declaration`: registry and manifest facts only.
- `observed`: live API evidence with timestamp and source.
- `not_observed`: not checked.
- `probe_failed_*`: an attempt failed; it is not proof that an app, permission, or repository is absent.

Every field must distinguish unknown from empty. Missing sections and partial API failures are degraded/unknown, not removals.

## Security invariants

1. Never collect, print, cache, upload, or commit private keys, JWTs, installation tokens, PATs, raw authorization headers, secret values, or token-bearing URLs.
2. Secret-store census remains names-only.
3. Never store a long-lived installation token as an Actions secret; mint short-lived tokens at runtime from protected credentials.
4. The workflow intentionally does **not** mint a token or read a token from a secret while SEC-01/SEC-02 provisioning is unverified. The optional manual probe is not a substitute for the sanctioned minter or production adoption gate.
5. Keep the Collector read-only. Do not add permissions or webhooks to solve an observability gap.
6. Treat manifest configuration as declared state and GitHub API reads as observed state.
7. Do not automatically revoke, rotate, uninstall, or broaden permissions in response to drift. Alert and open review work instead.

## Rollout gates

### P0 — registry and census
- [x] Add non-secret app registry.
- [x] Derive declared permissions/events from the manifest SSOT; remove duplicated permission declarations from the registry.
- [x] Add tests for the registry, manifest derivation, safe probe behavior, and four unverified role slots.
- [x] Integrate registry declarations into the existing mesh census/diff with backward-compatible old-cache handling.
- [x] Add weekly declaration-only artifact workflow.
- [ ] Run updated branch CI and review artifacts.
- [ ] Reconcile four role-slot statuses with AppID/PROCESS.json source of truth.

### P1 — live proof (blocked by secret provisioning)
- [ ] Resolve SEC-01: verify whether `APP_PRIVATE_KEY` is actually provisioned at the correct scope; the referenced name is not proof.
- [ ] Resolve SEC-02: verify per-app secret names before any workflow references them.
- [ ] Use the sanctioned minter or SHA-pinned token action only after provisioning is verified.
- [ ] Capture token-mint outcome, rate-limit readings, workflow run ID/attempt/SHA, duration/conclusion, and API status counts without credentials.
- [ ] Read back active installation scope and effective permissions; compare them with manifest declarations.
- [ ] Pass migration gates G1–G5 for each workflow before cutover, including shadow parity, bucket proof, and one-cycle fallback.

### P2 — maintenance and fleet expansion
- [ ] MAINT-01: weekly permission-drift audit, with drift opening/updating one issue and no automatic correction.
- [ ] MAINT-02: weekly per-app rate-limit census feeding quota readings via the #1884 route; missing readings stay null.
- [ ] Add webhook lifecycle evidence only when a receiver and protected webhook secret are ready; validate signatures and deduplicate delivery IDs.
- [ ] Keep app-repository/lane registry fragments discoverable from the hub, preserving owner/install boundaries.
- [ ] Prove actual app-token collection does not consume the owner PAT bucket before marking any app standing.

## Collaborator lanes

- **Integration Mesh / Muse:** registry and manifest census now exists in this proposal; review snapshot/diff behavior and cache compatibility. Standing thread #1505.
- **Quota Specialist / convergence / cadence / gaps:** use observed per-installation readings and measured calls/run in the #1884 meta-pool only after live bucket evidence exists.
- **AppID / provisioning:** reconcile the four reported in-flight roles with PROCESS.json; verify secret scope and active permission grants.
- **Research-Astute and search-astute-ly:** when those lanes provision apps, publish a registry fragment and a discoverable capability document in the app's home repository, then link it here.

## Acceptance criteria

A read-only collector appears in telemetry without check suites/comments; permissions come from manifest SSOT; live state is never inferred from declarations; four unverified role slots remain clearly non-authoritative; mesh snapshots detect registry changes without false removals on old/degraded snapshots; tests pass; and production token adoption is only declared after G1–G5 evidence and a real bucket proof.

This branch remains separate until comparative review and explicit merge.
