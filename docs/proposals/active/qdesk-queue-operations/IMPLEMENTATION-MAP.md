# QDesk implementation map

This file is a working integration map for issue [#5432](https://github.com/timerloggedout-spec/termux-monorepo/issues/5432). It is deliberately a map of existing owners and hand-offs, not a second source of operational state.

| Capability | Existing owner / evidence to reconcile | QDesk adapter contract | First-release mode |
|---|---|---|---|
| Queue population, tiers, admission | QUE feeds, admission evaluator, #4979 | source-native rows + as-of + collector freshness | read-only |
| Priority score/rank/order | #5283 and its owner decision stamp | consume method/version/factor contributions; expose delta and override proposal | read-only until policy endpoint |
| Claim, lease, executor | #5176/#5246, watchdog and executor receipts | claimed vs observed executing, exactly-once claim lineage | read-only |
| Throttle/quota | #5219, #5232, quota registry and throttle gauges | normalized gauge with numerator/denominator/window/reset/source | read-only |
| Worker identity | arm registry, provider/role identity, workflow/run/session evidence | declared vs claimed vs live-observed identity | read-only |
| Escalation | existing QUE/SIE policy thresholds | typed reason, due time, owner, dedupe key, next action | read-only |
| WagerTome | canonical wagering-book feed and owning allocation ledger; reconcile #5212's stale-feed evidence | immutable allocation projection and ledger reconciliation | read-only |
| SIE repair | #5210/#5212/#5214 and qdesk-self-repair workflow | failure lineage, diagnosis, candidate, verification, promotion receipt | read-only |
| DoE | #5146 / PR #5145 and DoE registries | independent design/allocation/verification provenance | read-only |
| Portfolio/observatory | #5271 and QDesk Observatory | source manifest and current-master evidence | read-only |
| Dependency plan / Gantt | `docs/proposals/active/gantt-dependency-phases/` | stable DAG IDs, baseline + append-only adaptive revisions | visualization only |
| GitHub Projects | `docs/ops/GITHUB-OBSERVABILITY.md` (ProjectV2 GraphQL) | stable ProjectV2/item IDs and field mapping | read-only |
| Browser quarantine | `timerloggedout-spec/quarantine-browser-clerk` (separate project/repo) | sanitized, signed execution receipts only | no direct access |
| Intake validation | new `qdesk-intake/v1` schema in this proposal | deterministic ALLOW/HOLD/REJECT/ESCALATE envelope gate | validate only; QUE admission remains separate |

## Source reconciliation checklist

Before wiring any adapter:

1. Fetch current master and the exact latest commit SHA for each source.
2. Identify the canonical producer, schema version, generated_at, observed_at, refresh cadence and last successful run.
3. Determine whether the source is a feed, ledger, policy, event, UI projection or historical artifact.
4. Record identity/join keys and classify joins as exact, derived, candidate or unmatched.
5. Preserve null/unknown and surface contradictory counts.
6. Verify whether a write endpoint exists and who owns its authorization.
7. Add fixtures for stale, missing, duplicate, partial, contradictory and malformed data.
8. Never count simulated pulses as worker activity, progress or completion.

## First thin vertical slice

1. Render source freshness and evidence levels from existing read-only feeds.
2. Render the existing priority list with ranker provenance and explanation; do not compute a new score.
3. Render worker rows with the declared/claimed/executing distinction.
4. Render wait reason and escalation clocks only when source fields exist; otherwise show `unknown-not-recorded`.
5. Render throttle and WagerTome values only after ledger/source reconciliation.
6. Add deterministic ingress schema/policy tests; do not connect an intake write path until QUE accepts the envelope and returns an admission receipt.

## Hard stop conditions

- Missing or stale quota/reset evidence for provider-dependent work.
- Missing/ambiguous authorization or owner decision.
- A write would bypass QUE admission, claim/lease, or exact-once executor semantics.
- Browser payloads request arbitrary fetch, code execution, credentials or external side effects.
- A simulated event would be represented as live execution or completion.
- The same policy/ledger/registry is already owned by another active issue or PR.
