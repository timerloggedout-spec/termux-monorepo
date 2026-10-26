# Gemini quota evidence: tier is not headroom

Gemini uses several independent quota dimensions. A tier label, an available model, or a public free price does not establish remaining quota or permission to run inference.

## What the code changes

`scripts/provider_quota_gemini.py` provides the offline Gemini evidence parser and quota evaluator. The existing `provider_quota_managers.normalize_observation` dispatches Gemini to that parser. `provider_quota_service.observe_gemini_quota` offers a network-free private service boundary; it is not registered as an authenticated GET service or an automatic collector. Its public projection reports unknown and never publishes supplied project, account, tier, entitlement, billing or counter observations.

The existing generic `provider_quota_coverage.evaluate` rejects Gemini's flat single-counter evidence. That schema cannot establish exact credential/project binding or simultaneous request and input-token headroom. The project evaluator is advisory and fail-closed, not an admission bridge. The shared-cap continuation below adds denial guards to the router and workflows, but does not enable production eligibility or smoke activation, change credentials/secrets, or activate alternate models.

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

## Shared cap and active workflow guard (continuation of #272 / #1441)

The original #273 implementation passed `GEMINI_API_KEY` to the Gemini CLI action. It was not CLI OAuth/account quota. Its active router incremented separate per-model counters, while the old 1450/day primary/backup quota action was not called by the active review, triage and invoke workflows. Changing models could therefore evade an intended aggregate local daily ceiling. Independent counters for two API keys also cannot establish independent capacity when those keys belong to the same project.

`scripts/gemini_shared_cap.py` implements one private local reservation ledger for an explicit operator-configured aggregate scope. All models, roles and declared primary/backup credential aliases consume the same bucket, even when their declared projects differ. This is a deliberately conservative operator policy, not a claim that Google enforces an additional account-wide or per-key quota. The provider-enforced project/model RPM, input TPM and RPD dimensions remain separate and are parsed by the existing `provider_quota_gemini` module; their limits are never replaced by this operator cap.

There is no 1450 default or inferred actual tier. A synthetic/offline policy uses schema `gemini-shared-cap-policy/v1`, `cap_kind: operator_configured`, a stable private `scope_alias`, a positive integer `limit`, the current `pacific_day`, an explicit timezone-aware `expires_at` no later than next Pacific midnight, and `credentials.primary.project_alias` (with optional `credentials.backup.project_alias`). These aliases are not keys or proof of credential binding. Missing, expired or malformed policy/state denies the check. Same-day scope replacement cannot reset the ledger, and an increased configured limit cannot undo an already pinned lower limit. Pacific-day resets use daylight-saving-aware dates. Reservations measure local intent, not actual model requests: a CLI turn may make multiple provider calls.

`scripts/gemini_quota_gate.py` reuses the project parser/evaluator, matches the requested credential alias/project/model before normalization, and requires source timestamps. It is called both before Gemini enters the router candidate pool and immediately before CLI dispatch in all four workflows: invoke, review, triage and after-peers second pass. Workflow dispatch requires the gate's explicit `skip == 'false'`; a missing output, missing file or gate error cannot allow the CLI step. Primary/backup switching is not introduced, and the existing primary secret expression is unchanged. Private inputs and ledger state are not placed in the shared Actions cache or public outputs.

**This continuation does not activate admission.** The gate deliberately has no enabling flag and always denies production dispatch, including for complete synthetic evidence. A local `flock`/atomic-file ledger coordinates only processes sharing that directory; fresh per-runner state or Actions cache restore/save cannot provide durable distributed accounting. No policy path is provisioned by the workflows. Before any later activation, separately reviewed work must provide exact credential/project binding, current applicable project/model quota and entitlement evidence, a durable cross-runner reservation authority and provider-request accounting, then obtain refreshed formal review and all required current-head gates. Offline local-cap checks can allow a synthetic reservation, but that result is never runtime eligibility.
