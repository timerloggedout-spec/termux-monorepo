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


## Crosswalk: inference discovery vs. backend capacity

The [Free-Tier Backend Recon (2026-10-21)](FREE-TIER-BACKEND-RECON-2026-10-21.md) answers a different question: which compute, workspace, storage, queue and edge entitlements may support the mesh, and which are actually present or measured. This document answers which upstream model/provider claims deserve research. Keep these dimensions orthogonal:

- **Backend capacity** is a provider/resource entitlement with its own cadence, expiry, account presence and live-reading method.
- **Inference catalog** is a candidate claim with source commit/content hash, access method, provider/model identity and freshness.
- **Runtime admission** requires both relevant backend/provider access evidence and task-specific policy/capability/data gates; neither recon grants it.
- **Value telemetry** is based on real authorized invocation/session records and validated attribution. Do not turn free-tier limits, catalog counts, missing sessions or zero dispatched requests into savings, balance or model-quality claims.

The [resource implementation matrix](RESOURCE-IMPLEMENTATION-MATRIX.md) tracks the two newly identified catalogs as separate discovery-only resource identities. Canonical ingestion still requires source-specific adapters and offline schema-drift tests; no automatic provider calls, account creation, or routing-policy change is implied.


## Implementation archaeology: existing provider work predates this catalog delta

**Correction to any reading of this recon as “only two providers exist” or “the providers are offline.”** The two newly registered entries above are only *new discovery-source identities*. They are not a count of implemented providers. The repository already contains a substantial live-capable remote-inference stack; the new catalogs must be reconciled with that stack rather than creating a parallel one.

### Merged implementation lineage

| PR | Status / scope evidenced by PR record | What it means for this recon |
|---|---|---|
| [#1321](https://github.com/timerloggedout-spec/termux-monorepo/pull/1321) and [#1325](https://github.com/timerloggedout-spec/termux-monorepo/pull/1325) | Merged: existing-token no-cost admission check and a bounded OpenRouter synthetic smoke attempt; the documented run received HTTP 429, so inference was **not** verified. | There is a real remote invocation path and a recorded provider-capacity failure; do not equate “attempted” with successful inference. |
| [#1463](https://github.com/timerloggedout-spec/termux-monorepo/pull/1463) | Merged: opt-in private OpenRouter current-key quota observation. | Account quota is a separate, privacy-sensitive observation; public catalog counts are not balances. |
| [#1466](https://github.com/timerloggedout-spec/termux-monorepo/pull/1466) | Merged: repairs 35 omitted source registrations; FreeLLMAPI static references 37 → 72, combined research records 160 → 195; 117 exact model claims unchanged; 54 service references initially unmapped in that repair. | Existing source ingestion and provider identity reconciliation already exist. Do not restart from a two-source/two-provider mental model. |
| [#1471](https://github.com/timerloggedout-spec/termux-monorepo/pull/1471) | Merged: seven additional fixed HTTP transports (Typhoon, UnoRouter, Routeway, Requesty, xKiro, xfyun Spark Lite, SEA-LION), five catalog adapters, plus default-off Gemini readiness checks; existing Felo/Gemini/Groq/OpenRouter preserved. | These are remote-capable adapters behind exact-model admission—not offline inference. A credential/readiness check or catalog GET is not itself a completion. |
| [#1481](https://github.com/timerloggedout-spec/termux-monorepo/pull/1481) | Merged: passive quota observation from supported catalog-response headers, status-only output, and Felo evidence reconciliation. | Existing quota readers and telemetry need reuse; unknown counters must remain unknown. |
| [#1504](https://github.com/timerloggedout-spec/termux-monorepo/pull/1504) and [#1511](https://github.com/timerloggedout-spec/termux-monorepo/pull/1511) | Merged: backend quota registry 28 → 64 service/metric records and publication of the dated free-tier backend recon. | Backend free-tier capacity has its own inventory. It is not the inference-provider catalog and cannot prove a model call is free or available. |
| [#1541](https://github.com/timerloggedout-spec/termux-monorepo/pull/1541) | Open, stacked on open #1470 at its recorded head; THUB-017 runtime/quota/telemetry implementation is not yet a merged production capability. | Keep this as a separate gated integration, not proof of a completed end-to-end research/inference loop. |

Further existing lineage includes the native provider batch and service-expansion contracts in [Provider Batch Implementation](PROVIDER-BATCH-IMPLEMENTATION.md) and [Provider Service Expansion](PROVIDER-SERVICE-EXPANSION.md). Their recorded baseline is 117 exact pinned directory model claims across 16 families, 23 source-mapped FreeLLMAPI chat-transport families, and 47 remaining unmapped service references (the later inventory's classification; not all 72 are free inference APIs). These counts have different denominators and must not be added together.

### What “offline” means—and what it does not

- **Offline tests/fixtures:** deterministic unit and regression tests exercise parsing, schema drift, identity mapping, quota normalization, request construction, admission-denial paths, and response handling without spending provider quota or transmitting prompts. This is deliberate test isolation.
- **Live catalog/readiness observations:** the existing provider-batch and operational-check workflows can make remote, bounded HTTPS requests to documented provider catalog/readiness endpoints when explicitly run in the authorized context. A catalog GET proves only that endpoint's observed response at that time.
- **Remote inference:** a completion/chat request is a distinct action. It requires an explicit approved execution path, an existing authorized credential where required, exact provider/model identity, verified no-cost terms/account admission, public-data eligibility, current quota/cooldown admission, bounded request/response handling, and sanitized outcome evidence. Do not run it merely to test a parser, and do not call a provider “operational” from a catalog GET.
- **Production proof:** a successful CI run against fixtures is not remote service proof; a successful catalog GET is not inference proof; an HTTP 429 is an observed capacity/rate-limit blocker, not a model-quality failure. Record each evidence class separately.

Thus “offline schema fixtures” means **test the new catalog adapters offline before enabling their ingestion**, not “run inference offline.” Once an adapter is validated, its catalog source may be fetched remotely under the existing trusted workflow controls; remote inference remains governed by the existing hub/admission and quota contracts.

### Actions consolidation chronology and risk

The Actions consolidation lineage is also already committed: [#1574](https://github.com/timerloggedout-spec/termux-monorepo/pull/1574) introduced the Tier-0 quota dispatch tree; [#1577](https://github.com/timerloggedout-spec/termux-monorepo/pull/1577) migrated nine more lanes to its decision structure; [#1579](https://github.com/timerloggedout-spec/termux-monorepo/pull/1579) added static drift enforcement; and [#1581](https://github.com/timerloggedout-spec/termux-monorepo/pull/1581) added the Vantage observer/Node H and repaired cadence drift. These changes centralize **when a lane is woken**, not the lane's provider credentials, endpoint contract, model admission, or invocation semantics. The consolidation must preserve those contracts and dispatch authority; the mere presence of a lane in a decision tree does not mean it has been dispatched or that a remote call happened.

### Required reconciliation before further provider additions

1. Reuse the existing 72-reference source ingestion, 195-record reconciliation, 117-model denominator, 23 transport mappings, exact-model hub routes, and canonical quota/admission readers. Do not create duplicate provider adapters or another scheduler.
2. For each of the two new catalogs, record the immutable source revision/content hash, schema, source-specific model/provider identity, access method and account/terms requirements. Keep the upstream directory's aggregate counts as claims.
3. Run offline fixtures for parser/schema and negative-admission behavior. Separately run a bounded authorized catalog fetch to validate the remote source. Neither step sends inference.
4. Only run remote synthetic inference through the already-reviewed operational gate, after no-cost account/model admission and quota reservation are proved. Capture run/job/request/attempt IDs and sanitized provider/model/status/usage evidence; never persist prompts, completions, keys, cookies, or raw private quota payloads.
5. Reconcile actual evidence into the existing provider-batch report and THUB-017/3L0/Free-Tier Value Board contracts. If there is no successful invocation record, report **not proved**, not “offline,” “zero usage,” “zero savings,” or “provider broken.”

## Priority validation extension: merged PR #1611 as an applied-science target

**Required target:** [PR #1611](https://github.com/timerloggedout-spec/termux-monorepo/pull/1611), merged to `master` at `e9319891c8dcde5963b1b4d80a1a3103e7ef56cd`. This is not just a historical citation: the merged AWS Free Tier + Strands Delphi Oracle proposal is a production-shaped test case for whether our evidence and workflow system distinguishes an experiment proposal from an executed experiment.

### Evidence observed at audit time

- PR #1611 is merged; its changed files include the active proposal's `RFP.md`, `EXPERIMENT-MATRIX.md`, `DEBATE.md`, `MANIFEST.md`, `ITEMS.md`, the proposal registry, and lifecycle metadata for `quota-aware-cadence-rfp`.
- Its experiment matrix explicitly says hypotheses only and no experiment has run. The PR states no AWS account/resources were created, no AWS invocation occurred, and no hackathon submission is claimed.
- The merged SHA's GitHub Actions check-runs endpoint returned 17 check runs. Observed checks include successes, skipped jobs, and a cancelled optional evidence-emission job; do not flatten that mixed result into “all checks passed.” Re-query the current merged SHA and current required checks immediately before release.
- The proposal-lifecycle workflow validates `scripts/proposals/validate_registry.py` on proposal-path pull requests and master pushes. Its `vote-hygiene` job is a PR-only advisory checklist and must not be treated as a binding vote or experiment result.

### Required test matrix (run on the current candidate SHA)

1. **Merged production regression:** run proposal registry/lifecycle validation against current `master`; assert PR #1611's proposal directory is registered, `MANIFEST.md` and `ITEMS.md` exist, and the pre-existing `quota-aware-cadence-rfp` entry remains valid.
2. **Applied-science provenance:** validate that the ten experiment IDs E-01 through E-10 have falsifiable hypotheses, methods, metrics, and rejection criteria; all results remain absent until actual receipts exist. Human ballots, model/provider observations, deterministic baselines, CI checks, and driver synthesis must remain distinct evidence classes.
3. **State-transition integrity:** reject any claim that `DESIGNED`, `COMMITTED`, `DEPLOYED`, `EXECUTED`, `VALIDATED`, or `PROMOTED` follows automatically from an earlier state. Require source SHA/config hash, fixture/cohort identity, timestamp/environment, result and failure classification, and sanitized receipt for each claimed transition.
4. **Safety negative tests:** assert that CI/proposal validation does not create AWS accounts/resources, dispatch cloud inference, submit the hackathon entry, infer consensus, or convert a model/provider run into a human vote. Paid or external execution remains behind its explicit approval/cost/security gate.
5. **Actions dispatch integration:** evaluate the current dispatch tree and its actual enabled workflow paths. Verify proposal-lifecycle validation is triggered by proposal path changes and master pushes; separately record skipped, disabled, unreachable, cancelled, and failed jobs. A scheduler node or successful workflow is not proof that an experiment or provider call ran.
6. **Provider evidence boundary:** keep offline fixtures, live catalog/readiness GETs, and remote inference as separate test lanes. Only an approved invocation receipt may count as inference evidence; catalog status, secret-name presence, CI success, or an HTTP 429 must not be upgraded into successful inference.
7. **Current-head verification:** pin every result to the candidate commit SHA, collect the current check-runs/workflow-run receipts, and re-check the head before publishing the verdict. The historical #1611 run is regression context, not a substitute for testing the current candidate.

### Full available repository scope and permission boundary

The connected repository metadata reports `admin=true`, `maintain=true`, `push=true`, `pull=true`, and `triage=true`; repository settings also report auto-merge and merge/squash/rebase methods enabled. This confirms repository-level connector scope, not every external provider entitlement or cloud account permission. Workflow job permissions are independently defined per workflow and remain least-privilege; do not widen them merely because the connector can administer the repository. GitHub Actions secret values are not retrievable through the supported secret APIs and must never be printed or copied into evidence.

### Release acceptance

The candidate is **not production-validated** until the current-head required gates are green, proposal registry validation passes, the state/provenance negative tests pass, and the current dispatch graph has been reconciled. Report the exact SHA, run URLs, passed/failed/skipped/cancelled states, and remaining blockers. No live AWS/provider inference is needed to validate offline lifecycle and evidence contracts; any separately approved remote experiment must have its own cost/security approval and sanitized execution receipt.
