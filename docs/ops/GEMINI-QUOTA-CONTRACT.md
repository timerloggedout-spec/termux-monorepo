# Gemini quota evidence: tier is not headroom

Gemini uses several independent quota dimensions. A tier label, an available model, or a public free price does not establish remaining quota or permission to run inference.

## What the code changes

`scripts/provider_quota_gemini.py` provides the offline Gemini evidence parser and quota evaluator. The existing `provider_quota_managers.normalize_observation` dispatches Gemini to that parser. `provider_quota_service.observe_gemini_quota` offers a network-free private service boundary; it is not registered as an authenticated GET service or an automatic collector. Its public projection reports unknown and never publishes supplied project, account, tier, entitlement, billing or counter observations.

The existing generic `provider_quota_coverage.evaluate` rejects Gemini's flat single-counter evidence. That schema cannot establish exact credential/project binding or simultaneous request and input-token headroom. The new evaluator is advisory and fail-closed, not an admission bridge. Existing production provider selection, smoke activation, workflows' credentials and secrets are not enabled or changed by this implementation.

## Public semantics, not live account values

Google's [rate-limit documentation](https://ai.google.dev/gemini-api/docs/rate-limits) establishes RPM, input TPM and RPD as usual dimensions; exceeding any applicable limit can block a request. Limits are enforced per project, not per API key, and differ by exact model. Some models also have IPM or TPD. No numeric standard-tier table is used to fill missing project/model thresholds, usage or remaining values.

The [billing documentation](https://ai.google.dev/gemini-api/docs/billing) says projects inherit their linked billing account's usage tier and associated limits. Monthly billing-account spend caps aggregate across linked projects; these are not project request counters. The rate-limit page also describes account-dependent spend-rate limits over ten-minute windows. Paid capacity and spend limits are not a fallback in this implementation. Free, Tier 1, Tier 2 and Tier 3 remain labels separate from actual model quotas and entitlement; account standing and billing state are not inferred.

Google directs users to active limits in AI Studio and says actual capacity can vary. This code does not claim that a Gemini API key exposes an actual-quota endpoint. Caller-supplied evidence is an internal normalized contract, not a Google API response schema or an authenticated account observation.

## Time and scope

RPD resets at midnight Pacific time, according to Google's rate-limit page. The implementation uses `America/Los_Angeles`, not UTC midnight or a fixed UTC offset, so daylight-saving transitions are handled correctly. A calculated next midnight describes a public reset rule, not an observed counter replenishment: evidence must be refreshed after that boundary.

Minute and model-specific reset thresholds remain unknown unless explicit current evidence supplies them. The code does not invent rolling-minute behavior or apply the RPD rule to TPM, TPD, IPM, batch, priority or account spend windows. Batch and priority traffic have separate documented restrictions and are not supported by this interactive-quota evaluator.

Evidence keeps exact model, private project alias, tier, entitlement, source observation time, per-dimension counters and window validity distinct. A fresh service invocation cannot make old supplied evidence current. Expired, future, malformed, inconsistent, missing or scope-mismatched evidence cannot establish headroom. Counts and aliases remain private; decisions contain fixed reason codes, not upstream messages or values.

## Why live Gemini eligibility is still unknown

The exact Actions credential-to-project association has not been established. Prior account visibility did not resolve which project owns that credential or provide authenticated current project/model quota evidence. This ambiguity remains a concrete blocker, not an inferred Free tier.

There is no trusted live binding/actual-quota collector in this change. Caller assertions cannot promote binding to verified. The runtime therefore remains fail-closed even when a synthetic fixture contains complete counters. Any future bridge needs separately authorized exact credential/project binding, current applicable dimensions, entitlement evidence, privacy controls and review before production activation.

No inference, retries, paid fallback, key creation/rotation, OAuth grant, terms acceptance or live account lookup is required or performed by these offline code paths. Parser, service, Pacific reset, privacy and evaluator regressions run in the existing quota CI lane.
