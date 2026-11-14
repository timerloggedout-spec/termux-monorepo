# Mesh Resiliency & Free-Compute RFP

**Tracking:** [Issue #1622](https://github.com/timerloggedout-spec/termux-monorepo/issues/1622) · Vercel capacity/failover acceptance: [Issue #1314](https://github.com/timerloggedout-spec/termux-monorepo/issues/1314) · quota allocation: [Issue #1884](https://github.com/timerloggedout-spec/termux-monorepo/issues/1884)

**Status:** implementation scaffold; no alternate production lane is verified.

## Objective

Preserve service continuity while minimizing avoidable builds, quota exhaustion, cross-provider coupling, idle compute, and repository integration overhead. The mesh is a set of independently deployable workload lanes—not a requirement to keep every provider running.

## Existing authorities to reuse

- `docs/DEPLOYMENT-LANES.md`: deployable identity, root directory, source branch, domain and provenance.
- `ops/quota/registry.json` + `scripts/quota_poll.py`: documented limits and existing observations. The Vercel deployment listing is explicitly known to undercount enforcement; it is not authoritative admission evidence.
- `docs/ops/QUOTA-REGISTRY.md`: existing poller and private/public boundary. Do not create another poller or publish private balances.
- `docs/ops/INTEGRATION-MESH-MATRIX.md` + existing six-hour census: integration reachability and observed wiring, not proof of application readiness.
- `docs/ops/ROUTING-ORCHESTRATION-MAP.md`: model/provider routing is distinct from application hosting failover.
- `docs/ops/AGENT-TEAM-ORCHESTRATION.md`: quality and integrated outcome outrank nominal zero-cost capacity.

## Workload classes and failover compatibility

| Workload | Minimum continuity contract | Static Pages eligible? |
|---|---|---|
| Static dashboard/docs | immutable source SHA, URL, content hash, cache policy | Yes |
| HTTP API | exact source SHA, compatible runtime/env, domain/TLS, health check, secrets, durable state | No |
| MCP endpoint | HTTP API contract plus MCP transport/protocol compatibility, auth semantics, session/state dependencies | No |
| Worker/job | idempotent claim, durable queue/checkpoint, bounded retry and replay semantics | No |

A fallback must be independently deployable and independent in the failure domain being mitigated. Two hostnames pointing to the same provider/account/build pipeline are not provider redundancy. The evaluator requires an explicit non-Vercel provider and `independent_failure_domain: true`; that declaration must be backed by source/configuration evidence before the candidate is trusted. A static mirror is not an MCP replacement.

## Admission and failover policy

1. Path-scoped Vercel ignored-build selection remains the first waste-control layer. Unknown project, missing SHA, and Git errors fail open to build so relevant source changes are not silently skipped.
2. Optional deployment admission is separate from CI correctness. Quota exhaustion/unknown state blocks optional deployment but must not fail unrelated tests or repository gates.
3. The existing quota registry supplies documented safety policy. A numeric listing, stale observation, ambiguous shared bucket, or undocumented reset is not an authoritative remaining-capacity proof. In particular, the current Vercel deployment-list reader undercounts enforcement; it cannot grant quota admission.
4. A candidate alternate is selectable only when project, root, domain, secrets, health, protocol, durable-state dependency, and exact source SHA are all verified for the requested workload.
5. If no alternate meets the contract, return `BLOCK_OPTIONAL_DEPLOYMENT`; do not route traffic, retry, or claim continuity. Existing production continues serving its last known-good deployment.
6. Recovery requires a fresh authoritative quota observation or verified candidate health/source evidence, followed by a new decision. No automatic traffic mutation is implemented by the policy evaluator.

`scripts/ci/deployment_admission.py` is a pure decision function. It consumes supplied evidence; it does not poll providers, read secrets, deploy, or mutate routing. Unknowns fail closed. Its fixture tests are offline.

## Quota allocation

Use the existing pool × focus × percentage allocation model from #1884. Per pool, allocations must sum to at most 100%; the remainder is reserve. Never combine unlike units (deployment count, build minutes, bandwidth, instance hours, requests, tokens, credits). A free entitlement is not an observed balance; a provider-wide shared bucket cannot be split among projects without keyed evidence. No paid fallback or automatic account provisioning.

## Recovery / anti-thrashing

- One decision per immutable `(source_sha, project, quota_window_id, policy_version)`; duplicate events are idempotent.
- No blind retries after 429/limit responses. Respect provider reset evidence; jittered backoff belongs to the owning adapter, not this pure evaluator.
- Keep the last known-good deployment serving. Never replace it with an unverified candidate.
- Require a stable healthy interval before re-admission; require consecutive failures plus bounded timeout before any future automated failover controller is considered.
- Rollback means restoring the last source-verified deployment, not merely pointing a DNS record at an unknown service.

## Provider shortlist — current evidence classification

| Surface | Current repository status | Permitted role now |
|---|---|---|
| Vercel | live application hosting; build-rate-limit failures observed; quota listing undercounts enforcement | Primary where available; preserve path filtering; no claim that quota admission is authoritative |
| GitHub Pages | configured static publication; current URL + SHA health not verified | Static-only candidate after exact publication verification |
| Render | candidate; no production project/root/domain/health proof in deployment SSOT | Not eligible for automatic failover |
| Cloudflare | candidate; exact product/project/source/domain not verified | Not eligible for automatic failover |
| Hex | analytics/evidence consumer, not application hosting | Never a runtime fallback |

No current alternative is asserted production-ready for MCP/API continuity.

## Acceptance sequence

- [x] Establish a single source-backed design and explicit evidence boundaries.
- [x] Add offline fail-closed admission evaluator and deterministic fixtures.
- [ ] Prove the Vercel ignored-build selector on both irrelevant and relevant provider-eligible events.
- [ ] Obtain authoritative Vercel enforcement/reset evidence (or keep admission closed).
- [ ] Verify one independent alternate end-to-end for a specific workload and exact SHA.
- [ ] Verify shared state, secrets, protocol, domain, health and rollback on that lane.
- [ ] Run a bounded failover/recovery drill with no paid fallback.
- [ ] Only then enable automated routing or production promotion.

## Explicit non-goals

No new poller, scheduler, quota ledger, secret store, account signup, paid spend, provider key hopping, automatic DNS mutation, production migration, or claim of guaranteed free capacity. Existing integration and quota authorities remain canonical.
