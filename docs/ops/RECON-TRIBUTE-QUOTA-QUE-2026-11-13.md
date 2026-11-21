# Tribute, quota-publication, and QUE leverage recon

**Cut:** 2026-11-13  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Status:** evidence-backed findings; implementation follow-through remains in progress.

## Corrected owner intent

Public quota/usage telemetry is an intentional published surface and a marketing asset for the public repository. Do not classify the published quota pages, public quota feeds, provider/model value designations, or their SEO/link graph as private by default. The earlier framing of this work as protecting private account quota information was incorrect and is withdrawn.

The defect to fix is drift that suppresses, mislabels, hides, or fails to refresh the intended public information. Preserve the intended public disclosures and their provenance. Do not invent a privacy boundary or remove fields merely because they are quota-related. Credential material and unrelated secrets remain outside publication; this report does not authorize publishing credentials.

## Confirmed owner records

- [QUE #5318](https://github.com/timerloggedout-spec/termux-monorepo/issues/5318) explicitly establishes a marketing taxonomy/link-callback lane across all published surfaces, naming `quota-swarm` and `quota-usage` as first stale-surface defects. Its rule is that staleness is a defect and pages must render from their feeds or carry a stamped as-of value.
- [QUE #5160](https://github.com/timerloggedout-spec/termux-monorepo/issues/5160) concerns a separate DoE execution-arm eligibility gate: exact provider/model/route availability, no-cost entitlement, headroom, data classification, and provenance. It is not authority to reclassify the public quota marketing surfaces as private.
- [QUE #5177](https://github.com/timerloggedout-spec/termux-monorepo/issues/5177) and [PR #5179](https://github.com/timerloggedout-spec/termux-monorepo/pull/5179) establish the Billion Tokens marketing page and referral surface. The merged page exists; the issue lifecycle still needs reconciliation with its completion evidence.
- [PR #4888](https://github.com/timerloggedout-spec/termux-monorepo/pull/4888) is the merged Surfaces Map implementation checkpoint. [PR #4898](https://github.com/timerloggedout-spec/termux-monorepo/pull/4898) is a later serve-step proposal and must be reconciled as a subsequent stage, not substituted for #4888.
- [PR #5246](https://github.com/timerloggedout-spec/termux-monorepo/pull/5246) merged the admitted-to-dispatch executor. [PR #5291](https://github.com/timerloggedout-spec/termux-monorepo/pull/5291) merged auto-claim and auto-resolve at escalation. These existing mechanisms must be used rather than creating a competing QUE dispatch path.

## Direct source observations

### Public quota data freshness

At this cut, `ops/quota/usage-series.json` was generated at `2026-11-13T09:04:13Z`, but its `github` series last point is `2026-11-02T06:30:06Z`. Its Jules points are from October 31. The recently generated wrapper therefore does not mean the underlying observations are current.

`ops/quota/quota-usage.json` was generated at `2026-11-13T03:32:29Z`, but its GitHub API core series also ends at `2026-11-02T06:30:06Z`. The feed itself labels the bucket as the shared PAT bucket and explains that points are observations, not continuous samples. Retain those semantics; do not turn sparse observations into continuous measurements.

The usage-series generator lists multiple inputs, including the quota usage pack, Vultr usage, desk feed, allocation plan, rate-limit events, nested-family tracking, routed-dispatch DoE records/stamps, and 3L0 intake. Freshness must be computed per source/series, not inferred from the top-level generated timestamp.

### Navigation and version registry

The current shared navigation `apps/tribute-dashboard/site-nav.js` is a manually maintained links array and includes a legacy Vercel destination under the old Help-Wanted naming. The current fallback page inventory in `apps/tribute-dashboard/versioning.js` is another independently maintained list. This is a source of drift.

The nav contains Quota, Quota usage, Quota graphs, and Swarm quota as explicit destinations. Do not remove or hide these public surfaces as a privacy "fix". Reconcile canonical route identity and migration aliases separately from content/domain ownership.

## Required engineering direction

1. Treat Tribute as the current published surface identity while preserving historical Help-Wanted URLs only as explicit compatibility aliases where required. Do not rename unrelated domain classes, route identifiers, feed schemas, or ownership taxonomies merely because the site path changed.
2. Build/identify one canonical surface registry and derive or validate shared nav, versioning fallback inventory, sitemap, surfaces map, and preview routing against it. Keep primary navigation curated; the registry/sitemap can enumerate the full estate.
3. Keep public quota/usage publication enabled according to owner intent. Repair producers and refresh triggers; expose per-series observation timestamps, source provenance, freshness verdicts, and gaps. A new generated_at with stale points must visibly remain stale.
4. Reconcile existing quota collectors and workflow owners before adding a new scheduler. No deliberate manual refresh dependency: use event/cron automation already owned by the relevant workflows, with failure receipts and alertable stale thresholds.
5. Keep marketing/public quota feeds distinct from DoE dispatch eligibility decisions. The latter may require exact live provider/model/account evidence for safe routing; that operational gate does not redefine the public pages' audience or purpose.
6. For every provider/model/endpoint role, publish an attributed value designation with its evidence basis and timestamp. Keep measured, reported, estimated, proxy, catalog-only, and unknown states distinct. Never invent a score or imply a provider was invoked when it was not.
7. Extend QUE through existing admitted-dispatch executor, watchdog, QDesk, and issue-trigger templates. Preserve exactly-once claim semantics, tier/rank order, escalation and hold reasons, and the existing merge-hand boundary. Do not introduce a parallel dispatcher.
8. For Billion Tokens and other marketing surfaces, reconcile issue completion from served-state evidence and current QUE lifecycle rules; do not close or relabel solely because a PR merged.

## Immediate follow-through

- Inspect the #5318 marketing taxonomy filing and its current QUE state; it is the correct home for the public quota freshness and SEO/link-callback work.
- Inspect the current producer workflows and run histories for quota usage, quota series, surface feeds, and deploy. Identify the exact missing producer/trigger leg before editing cadence.
- Reconcile #4888/#4898 map stages with current master and preserve the #4888 implementation lineage.
- Continue #5319 runtime nav repair; verify current checks before merge.
- Trace Help-Wanted rename contamination through commit/PR chronology and domain-owned paths. Produce a bounded remediation, not a global text replacement.

## Non-claims

This recon does not claim that all quota series are currently fresh, that every provider has verified live capacity, that #5318 has completed, that #5319 is merged, or that the published site has deployed a change. It records source-backed findings and the correct implementation direction.
