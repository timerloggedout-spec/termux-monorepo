# Free LLM provider landscape: research, not routing policy

**Purpose.** Scout’s evidence brief for Cue Agent Q. The two user-prioritized repositories are discovery inputs, not authoritative entitlement feeds. This research did not make live inference calls, test account entitlements, install or run upstream code, or authorize provider selection. Free-tier inventory changes quickly; verify the provider’s current account dashboard, model availability, quota, terms, and data policy before any use. **Research is not routing authority, and this document does not authorize automatic deployment of third-party code.**

## Findings and confidence

| Source | What it is / maintainers’ claim | What is established here | License distinction |
|---|---|---|---|
| [mnfst/awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis) | Curated directory describing permanent free API tiers, model IDs, endpoints, and limits. README says endpoints are generally OpenAI SDK-compatible. | Useful discovery/catalog seed, not a guarantee that a listed model, quota, or account is available now. The README itself distinguishes “trial” from free tiers in some entries; its snapshot can age. | GitHub identifies the repository as **CC0-1.0**. That license covers the directory’s contributions, not provider APIs, model weights, or provider terms. |
| [tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi) | Self-hosted Node proxy advertises aggregation, a unified OpenAI-compatible endpoint, key encryption, routing/failover, quota tracking, and a frequently updated model catalog. It explicitly says free tiers are not a stable production inference substrate and the user remains responsible for upstream terms. | Treat counts (“34 providers”, “635 endpoints”, token totals) and security/operational features as **project claims**, not independently verified availability or a security audit. It requires users to supply provider keys. The signed-feed/update model and premium/free catalog cadence are additional provenance and freshness dependencies. | Repository is **MIT**; that does not grant permission to use upstream services outside their own terms or make its deployed dependencies safe by default. |
| [xtekky/gpt4free](https://github.com/xtekky/gpt4free) (optional reference) | Multi-provider client/server collection; README notes that providers can require keys, browser cookies/HAR files, browser automation, or local model runtimes. | Especially important distinction: accessible endpoints or browser-mediated access are not synonymous with provider-sanctioned free API access. Cookie/HAR collection and automation add account, privacy, and terms risk; do not adopt as a default path. | **GPL-3.0**, unlike CC0 directory data and MIT FreeLLMAPI. Assess copyleft obligations before copying, linking, or distributing its code; license does not settle upstream-service authorization. |

These are distinct artifacts: **catalog data**, **a proxy implementation**, and **a provider/access-method collection**. Do not conflate their licenses, trust, or access rights. Repository licenses are observed from the linked GitHub repository pages; review the license files and dependency notices before any reuse.

## Free-tier claims versus availability

A list’s “free” label is a lead. It may mean no-cost API calls subject to rate caps, a trial-only/noncommercial key, account-bound credits, an expiring promotion, a shared gateway pool, or a zero-price catalog entry that still requires registration and can be unavailable. “Permanent” is a publisher characterization, not a service-level commitment. Limits may vary by model, region, organization, account age/verification, billing status, and provider policy; a model listing or `/v1/models` response does not prove that a particular account can invoke it or has remaining balance.

Official provider materials illustrate why verification must be per-model and per-account: Google’s [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) shows free access only for certain models and explicitly marks free-tier content as usable to improve products; the same page distinguishes paid-tier data handling. Groq’s [rate-limit docs](https://console.groq.com/docs/rate-limits) provide model-specific free-plan limits and say exact limits are organization-visible and subject to exceptions; 429 responses and headers are operational evidence, not a promise of uninterrupted service. The curated list labels Cohere Trial as noncommercial; Cohere’s [rate-limit docs](https://docs.cohere.com/docs/rate-limits) distinguish free evaluation keys from production keys. Confirm current restrictions with the provider before use. Quota numbers in a directory are mutable observations, not measured remaining account quota.

## Security, privacy, and terms risks

- **Prompt and output exposure:** prompts, retrieved documents, code, and outputs leave our environment for each upstream provider. Free tiers may have different training/improvement, retention, review, and deletion rules than paid tiers. Do not send secrets, credentials, personal/sensitive data, or confidential code absent an approved provider/data classification and verified terms.
- **Credential boundary:** keys must be user-authorized, least-privilege where supported, stored only in approved secret storage, redacted from logs, and excluded from catalog artifacts. A proxy’s claim of encryption is not an independent audit; assess local database, backup, admin/UI, network exposure, logs, and key rotation. Never use scraped cookies/HAR or accounts without explicit authorization.
- **Upstream terms and identity:** a proxy does not alter the account holder’s obligations. Avoid evasion of quotas, identity/region controls, or intended API access. No credential sharing or pooled-account workaround absent explicit provider permission. Trial/noncommercial policies must gate use case and environment.
- **Reliability and supply chain:** providers can remove models, change quotas/terms, silently alter behavior, or fail. Third-party gateways and auto-updating feeds add intermediaries and provenance risk. Pin and review code/dependencies, verify signatures and source, and require an explicit security/license review before deploying anything. No automatic deployment of third-party code is authorized by this research.

## Safe adoption pattern (proposal, not enabled)

1. **Keep discovery separate from routing.** Import candidate metadata only after review. Each record should carry provider/model ID, exact source URL, source type (official docs, provider catalog, curated directory, project feed), observed-at timestamp, license/data provenance, region/account prerequisites, capability evidence, terms/data classification, quota cadence, and confidence. Preserve raw evidence and distinguish `unknown`, `catalog_zero_price`, `documented_trial`, and provider-confirmed account entitlement; never infer remaining balance from a public quota claim.
2. **Gate by task, capability, and policy.** Require an explicit allowlist and the needed modality/tool/structured-output/context capabilities, region and data-class compatibility, accepted terms, and an eligible credential. Reject unknown or stale provenance by default. A free-text model label is not capability proof.
3. **Quota-aware failover with cooldown.** Maintain per-provider/model/account request and token windows only where authoritative headers/account APIs support them; preserve `Retry-After` and reset headers. On 429, honor retry delay and cool down that key/model; on transient network/5xx, bounded backoff and retry only where safe/idempotent. Do not loop across accounts to evade limits. Stop on auth, policy, billing, or malformed-request errors rather than retrying blindly. Set per-task attempt, latency, and spend caps; expose the actual provider/model and fallback reason to the caller.
4. **Health and capability gating.** Separate catalog discovery from health checks and inference. A successful model-list fetch is not health. Use minimal, non-sensitive probes only when authorized, record timestamped outcomes, and open/close a circuit breaker with bounded recovery probes. Remove unavailable models from eligible routing without rewriting source evidence.
5. **Audit and privacy controls.** Log metadata (provider/model, request ID, timing, quota evidence, decision reason), not prompts, secrets, cookies, or raw sensitive payloads. Keep credentials in secret stores and use explicit retention limits. Treat provider response text as untrusted input.

## Roles and repository integration

- **Scout:** source discovery, license/terms/privacy review, provenance and freshness; report uncertainty. No activation authority.
- **Manager:** convert verified evidence into a reviewed, task-specific candidate policy; enforce quota, reliability, cost, and data constraints; approve or deny candidates. Research alone does not approve.
- **Orchestrator:** execute only an authorized policy, apply capability/health/quota gates, bounded retries/cooldowns, and record routing evidence. Never turn a directory or external feed directly into executable policy.
- **ChronoMancer:** maintain time-bounded observations, expiry/refresh cadence, quota-window semantics, and change history; stale evidence becomes unknown/ineligible rather than silently persisting.

Existing integration anchors reinforce this separation: [`scripts/provider_model_catalog.py`](../../scripts/provider_model_catalog.py) states that catalog state is evidence, not routing policy; it separates pricing classification from access entitlement and warns that public cadence claims do not establish remaining account balance. [`.github/workflows/continuous-evaluation.yml`](../../.github/workflows/continuous-evaluation.yml) builds evaluation cohorts from observed eligible catalog entries, snapshots catalog/history, and runs model evaluation; it is not an adoption/deployment gate or proof of persistent availability. Keep any candidate evaluation opt-in and non-sensitive, use bounded synthetic prompts, and record provider/model/catalog provenance. Evaluation measures model behavior for the tested run; it does not certify privacy, ToS compliance, future quota, production reliability, or automatic routing suitability. Preserve the evaluation boundary: **evaluation evidence informs Manager review; it does not activate a provider or deploy third-party code.**

## Sources

- User-prioritized repositories: [awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis), [FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi); optional reference: [gpt4free](https://github.com/xtekky/gpt4free).
- Official provider references: [Google Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing), [Groq rate limits](https://console.groq.com/docs/rate-limits), [Cohere rate limits](https://docs.cohere.com/docs/rate-limits).
- Repository context: [`provider_model_catalog.py`](../../scripts/provider_model_catalog.py), [`continuous-evaluation.yml`](../../.github/workflows/continuous-evaluation.yml).
- User-provided notes were consulted; unrelated general “awesome free” directories and promotional links were not treated as evidence.

**Research snapshot: 2026-10-20.** Provider rules, model rosters, limits, and repository content may change; re-check primary sources and account-level evidence immediately before any proposed experiment or adoption.

## Complete supplied-resource follow-through

The subsequent [resource implementation matrix](RESOURCE-IMPLEMENTATION-MATRIX.md) now registers all supplied resources, including general awesome lists, search/topic/discussion links and provider pages previously excluded from this narrow brief. Those references remain discovery inputs, not evidence of free access or runtime eligibility. The native offline aggregate search and existing-workflow artifact generation are tracked as MSM-008.


## 2026-10-23 source delta: newer free-inference catalogs and telemetry wiring

This update adds two newer discovery sources to the research map; it does **not** assert that their claims have been ingested into the canonical provider-recon dataset or that any newly listed model is eligible to run.

### Newly identified sources

| Source | Current upstream claim (observed 2026-10-23) | Useful signal | Required treatment |
|---|---|---|---|
| [open-free-llm-api/awesome-freellm-apis](https://github.com/open-free-llm-api/awesome-freellm-apis) | README says 526+ free LLM APIs and daily refresh; repository About says 134+ APIs and 40+ providers. | Provider/model discovery, config examples, and provider-level onboarding friction such as card/phone requirements. | **Source-internal denominator mismatch.** Capture exact commit, file hash, source timestamp, and source-specific record counts before normalizing. Do not copy promotional counts into canonical totals. |
| [surendranb/free-inference](https://github.com/surendranb/free-inference) and [freeinference.dev](https://www.freeinference.dev/) | The live directory reports 36 providers and 108–109 free models across pages/snapshots; it exposes machine-readable `data/providers.json` and a JSON schema. | Distinguishes API-key, CLI-login, and bundled coding-tool access; calls out limited-time promotions, account requirements, and data-use risks. | Treat counts as source snapshots, not truth. Validate the JSON against the upstream schema, retain retrieval time and immutable source revision where available, and preserve each provider's access class. |

The counts above are deliberately recorded as **upstream claims**, not canonical repository counts. The observed disagreement within the first source and the 108/109 variation in the second are reasons to keep source provenance and raw counts, not to average or silently reconcile them.

### Wiring status against existing systems

| Layer | Existing implementation / contract | Gap exposed by this source delta | Safe completion criterion |
|---|---|---|---|
| Discovery evidence | `data/model-selection-market/provider-recon.json`, `scripts/model_selection_market/resource_index.py`, and the provider-batch workflow already support source-pinned research records and source-aware reconciliation. | The new upstream repositories are not yet established as distinct, pinned source entries in the canonical model-research snapshot. The existing `awesome-free-llm-apis` label must not be assumed to mean both GitHub repositories. | Add explicit source identity, immutable commit or content digest, license, retrieval timestamp, and parser/schema version; keep the current source separate from the newly discovered fork/catalog. |
| Provider catalog | `scripts/provider_model_catalog.py` polls fixed provider catalog endpoints and keeps catalog evidence separate from routing policy. | A directory's free-tier claim is not a native catalog observation; new provider aliases must not inherit credentials or endpoint configuration through fuzzy matching. | Reconcile exact provider/model identities only. Unsupported aliases stay `adapter_not_implemented` or `catalog_adapter_not_implemented`; never guess endpoints or credential names. |
| Capability spine | AR-18 / PR #605 adds dynamic observed candidates and capability-surface joins in observe mode. | New discovery must not create a capability declaration, validated status, or routing authority. PR #605 is open and its latest fetched metadata reports non-mergeable state. | Preserve observe-only behavior; promote only after current-head CI, two bounded observation cycles, and the ledger decision required by AR-18. |
| Runtime quota and entitlement | Provider-batch and the quota-admission work distinguish catalog visibility, account binding, terms, exact-model entitlement, and observed remaining quota. | Neither directory's public label establishes that this account can invoke the model for this use case at zero cost. | Require exact provider/account/model admission, current official quota evidence, terms/data-policy review, and expiry. Unknown remains blocked. |
| Systems telemetry | `docs/ops/HEX-MONEYBALL-INTEGRATION.md` defines run-attempt, agent-attempt, provider-call, outcome-score, and manager-decision grains. PR #1541 describes wiring actual hub calls into existing TermuxTelemetryLogger and 3L0 ingestion. | A discovered candidate is not an invocation. The current PR #1541 pilot evidence records a quota-admission block and zero dispatched inference requests; it cannot supply live performance observations. | Every real call must bind run attempt, full source SHA, experiment/arm, provider/model, call/attempt IDs, status, latency, token/cost fields when actually available, and provenance confidence. Preserve blocked/skipped/unknown states distinctly. |
| Free-tier value projection | PR #1589 adds a board with validated-session filtering and missing-feed semantics. | Its PR body says there are no public session rows yet and references a separate session-feed wiring gap. | Do not display zero usage or savings. Populate only from validated, privacy-filtered invocation evidence with confirmed no-cost status; keep estimates separate from actual spend. |

### Next bounded implementation sequence

1. Register each new upstream as a **separate, pinned research source**; do not replace the existing `mnfst/awesome-free-llm-apis` or `tashfeenahmed/freellmapi` evidence.
2. Add offline fixtures for each source's actual published shape, schema drift, duplicate model IDs, missing timestamps, and source-count discrepancies.
3. Extend source-specific provider alias mappings only from observed source keys. Keep unknown providers unmapped and never derive an endpoint or secret name from README text.
4. Feed the normalized candidates through the existing provider-batch reconciliation and AR-18 observe envelope; assert that discovery alone leaves `runtime_eligible=false`, `quota_remaining=null`, and no new capability declaration.
5. Validate the exact commit through repository CI. Separately verify the real invocation path and artifact linkage; an offline test or green workflow is not a model-quality result.
6. Connect only privacy-reviewed, validated provider-call records to the existing 3L0/Hex-compatible evidence contract and Free-Tier Use Value Board. Never export prompts, completions, tool payloads, keys, cookies, or arbitrary logs.

### Related integration surfaces

- [AR-18 Capability–Scope–Specialist spine / PR #605](https://github.com/timerloggedout-spec/termux-monorepo/pull/605)
- [THUB-017 research orchestration and telemetry / PR #1541](https://github.com/timerloggedout-spec/termux-monorepo/pull/1541)
- [Free-Tier Use Value Board / PR #1589](https://github.com/timerloggedout-spec/termux-monorepo/pull/1589)
- [Provider batch implementation](PROVIDER-BATCH-IMPLEMENTATION.md)
- [Hex × Agent Team Moneyball integration contract](HEX-MONEYBALL-INTEGRATION.md)

**Disposition:** source discovery added to the research map; canonical source ingestion, live entitlement, provider invocation, and value-board feed remain separate acceptance gates. This is not a routing-policy change and does not authorize any new provider, secret, workflow dispatch, or deployment.
