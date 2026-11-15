# Agent Loops

Reusable, bounded agent workflows for `termux-monorepo`. Follow the loop's scope, acceptance checks, finite boundary, and stop conditions. A loop run is one finite pass; it is not a background scheduler.

## QUE provider validation and activation

- **Loop ID:** `QUE-PROVIDER-ACTIVATION`
- **Purpose:** Reconcile the complete inference-provider population, validate every configured inference arm, classify quota versus daily-pool access correctly, project eligible arms into QUE, and verify end-to-end dispatch.
- **Trigger:** Explicit owner request such as `/continue`, `BIUDL`, or a manually initiated run.
- **Finite run boundary:** One pass over the current canonical provider catalogs, provider protocol/extension registries, exact admission-policy entries, configured build arms, and the separately identified g4f model-pair population. Each exact policy-admitted native provider/model receives at most one bounded health invocation in a run. The g4f population is processed only in explicit offset batches; never sweep all 9,588 pairs automatically. Stop when every discovered/configured entry has an explicit disposition or a stop condition is reached.

### Population boundaries

Keep these populations distinct; never substitute one denominator for another:

1. `ops/challenge/desk-feed.json → dispatch.provider_catalog`: canonical dispatch provider accounting.
2. `scripts/provider_model_catalog.py`, `provider_catalog_protocols.py`, `provider_extension_catalogs.py`: catalog adapters and protocol/extension surfaces.
3. `llm_api_hub/server/research_providers.py`: exact-model native provider admission and protocol-normalized invocation.
4. `provider-invoke.yml`: current 31-choice native/catalog menu; this is not the complete provider universe.
5. `ops/dispatch/build-arms.json`: current build-arm registry; its current seven-arm shape is not the provider universe.
6. g4f universe and working-pair datasets: separate population. Historical sandbox success is not current inference validation.

Deduplicate provider aliases and aggregators while preserving each independently routable endpoint/model pair. Mark catalog-only or unsupported adapters explicitly; never silently omit them.

### Required arm validation

Every configured arm must pass the same validation baseline, regardless of quota class:

- Provider, configured instance, exact endpoint and exact model identity.
- Invoke adapter/protocol compatibility and current reachability from the actual execution environment.
- Exact current admission-policy entry, configured credential or explicitly supported public access.
- No-cost evidence, current pricing source, accepted-terms assertion/source, capability evidence, data-classification and expiry/recheck.
- Health/inference receipt with timestamp, source revision, safe reason code, latency and usage when returned.
- Explicit quota classification and evidence.
- Explicit dispatch disposition.

Policy values such as `terms_accepted` and `free_account_verified` are owner assertions, not independent provider verification. Receipts must say `policy_asserted`, never provider-verified.
The shared validator rejects future or stale evidence timestamps: pricing ≤30 days, capability ≤90 days, terms ≤365 days. The same validator is used by the smoke and execution paths.

### Quota and pool semantics

Treat quota as a separate dimension from validation:

- `provider_quota_backed`: use authoritative provider/account quota evidence and current remaining/reset snapshot where required.
- `daily_pool_no_provider_quota`: do not require or fabricate a provider quota counter. Require a stable `pool_id`, source evidence, current shared-pool allocation/usage snapshot, reset metadata, and complete pool coverage.
- `quota_unknown`: may be catalogued or receive a separately bounded, explicitly authorized metering probe only if the exact no-cost, policy, terms and capability gates pass; it is never dispatch-eligible.
- `quota_not_applicable`: require evidence that neither a provider quota nor shared pool applies.

A daily-pool arm is dispatch-eligible only when the shared pool snapshot and cadence are current and show allocation available. Absence of a provider quota counter is not evidence of exhaustion and is not evidence of unlimited capacity.

### Bounded execution rules

- Use `.github/workflows/provider-inference-validation.yml` for the dynamic matrix of all native provider adapters. With `N` discovered adapters, a default run consumes `N + 2` jobs (discover + N validate + census); enabling stamps adds one stamp job and can fan out up to N additional workflow runs. Include those executions in the shared Actions budget; stamping remains opt-in.
- Use `.github/workflows/g4f-inference-smoke.yml` for explicit no-auth g4f batches. Default to the historical `working` source; for `universe`, require an explicit source/offset/limit selection and keep concurrency/timeout bounded. A g4f smoke receipt is health evidence only; it has `quota_class=unclassified` and `dispatch_eligible=false` until pool policy and allocation are independently established.
- The matrix is policy-gated. If `LLM_API_HUB_PROVIDER_POLICY_JSON` is absent or has no exact admitted entry, no catalog or inference request is made for that provider.
- At most one exact admitted model per provider per run; maximum parallelism 2; health prompt only; maximum output 16 tokens; one attempt; no paid fallback; no model fallback; no retries.
- Catalog-only observations must remain `inference_status=not_attempted`.
- Scoring-plane stamp fan-out is opt-in and defaults off. Never turn it on implicitly.
- Never accept provider terms, create accounts, change credentials, spend money, harvest browser credentials, bypass provider controls, or change production routing weights automatically.
- No live inference call without a current exact policy entry and source-backed no-cost, terms and capability evidence. A `quota_unknown` arm may receive only the separately bounded probe described above; it remains non-dispatchable until current quota/pool evidence exists.
- If Termux device preflight is unavailable, mark device validation blocked. Do not claim device smoke passed.

### Loop steps

1. **Observe:** Capture base/head revision, workflow/check state, provider catalogs, availability receipts, admission policy, quota registry, pool allocations/snapshot, arm census, cadence feed, queue claims, and QDesk feed.
2. **Inventory:** Build the deduplicated population with explicit source and denominator. Separate native providers, catalog-only entries, protocol extensions, aggregators, and g4f pairs.
3. **Admit:** For each exact provider/model, validate policy fields and source evidence. Missing/expired policy, terms, credentials, capability, or no-cost evidence becomes `approval_required` or `deferred`; do not invoke.
4. **Validate:** Run the bounded catalog/inference smoke only for admitted native pairs. When explicitly requested, run one bounded g4f offset batch and record its sanitized receipt. Never persist completion text or secrets.
5. **Classify:** Resolve provider quota versus daily-pool/no-provider-quota versus unknown/not-applicable. Check current snapshot freshness, allocation, reset, and coverage.
6. **Project:** Reconcile validated exact models into the canonical build-arm projection. Reuse `research_providers.complete` adapters; do not create a parallel provider registry or auth/protocol implementation.
7. **Gate:** Intersect provider policy, inference receipt freshness, capability, arm census, and `pool-cadence/v1`. Only the intersection may become dispatch-eligible.
8. **Dispatch:** Preserve claim-before-fire and exactly-once semantics. The arm claimed by `dispatch_executor.py` must be the exact arm invoked by build-dispatch; no second selector may silently substitute a provider.
9. **Reconcile:** Capture invocation, usage, artifact, verification, and terminal-state receipts against the same provider/model/arm identity.
10. **Publish and debrief:** Update QDesk with the complete denominator, explicit dispositions, freshness, quota/pool class, and dispatch eligibility. Report the run receipt in the conversation and identify the next safe blocker or action.

### Acceptance check

A run is **complete** only when:

- Every canonical provider/endpoint/model candidate has an explicit disposition and evidence reference.
- Every arm labelled inference-active has a current successful exact-model inference receipt.
- Every dispatch-eligible arm passes policy, capability, health, entitlement, census, and quota-or-pool cadence gates.
- Daily-pool/no-provider-quota arms can qualify without a provider quota counter and with authoritative shared-pool evidence.
- `quota_unknown` arms remain deferred.
- The exact claimed arm is the exact arm invoked, with reconciled usage/outcome and terminal receipt.
- QDesk reports accurate denominators and receipt freshness.
- Required contract tests and relevant CI gates pass.

### Stop conditions and terminal states

Stop the current run when any of the following occurs:

- Exact policy entry, owner terms assertion, source evidence, or required credential is missing or expired.
- The provider is paid-only, pricing is ambiguous, or the no-cost condition cannot be proven.
- Quota/pool classification is unknown, pool allocation evidence is missing, or the snapshot is stale/incomplete for dispatch/activation. A separately bounded quota-measurement probe may proceed only under the exact policy/no-cost/terms/capability gates and never converts the current filing into a dispatch.
- Protocol adapter is missing, endpoint is unhealthy, or capability/data policy fails.
- CI fails, the Termux preflight is unavailable for a required device-side check, or any secret exposure is suspected.
- Further action would require provider signup, terms acceptance, credential mutation, paid spend, production routing-weight changes, or another explicit owner approval.

Terminal states:

- `complete`: all acceptance checks pass.
- `partial`: safe progress made; remaining entries have explicit blockers.
- `approval_required`: owner/provider input is required before the next action.
- `blocked`: infrastructure, CI, device, or evidence dependency prevents progress.
- `failed`: a contract or execution failure needs repair before another pass.

A successful inference smoke alone is never terminal success for QUE activation. It proves endpoint/model response only; dispatch eligibility remains false until the separate census and quota/daily-pool cadence gates pass.

### Current linked work

- [#5454 — Full inference-arm validation and activation](https://github.com/timerloggedout-spec/termux-monorepo/issues/5454)
- [#5459 — Policy-gated inference smoke and daily-pool cadence](https://github.com/timerloggedout-spec/termux-monorepo/pull/5459)
- [#5470 — g4f bounded offset-batch validation](https://github.com/timerloggedout-spec/termux-monorepo/issues/5470)
- [#5468 — Full multi-protocol build-arm projection](https://github.com/timerloggedout-spec/termux-monorepo/issues/5468)
- [#5151 — Multi-arm build routing](https://github.com/timerloggedout-spec/termux-monorepo/issues/5151)
- [#5160 / #5152 — Free inference pool and per-arm quota ledger](https://github.com/timerloggedout-spec/termux-monorepo/issues/5160)
- [#5283 — Task-plane priority and claim order](https://github.com/timerloggedout-spec/termux-monorepo/issues/5283)



### Population count definitions and census artifact

The current `master` desk-feed snapshot distinguishes these counts:

- **110** distinct providers across all lanes; this includes non-model service lanes.
- **89** distinct providers in the model lane, represented by **91** model-lane records.
- **92/93** inference-wiring records accounted as wired; the remaining one is excluded by kind. These are wiring records, not unique provider counts.
- **7,341** provider×model endpoint verified floor, counted **2026-11-01**. This is a historical census floor, not current live activation proof.
- g4f: **60** fork-catalog provider rows, **4,242** raw model rows / **4,241** distinct fork pairs; the separate universe enumerates **9,588** pairs across **160** providers. The historical probe attempted 9,588 and recorded **160** inference successes. None of these historical successes is current activation evidence.
- The current build-arm registry has **7** arms. The single-provider menu has **31** choices; the dynamic validation matrix covers all **29** native admission adapters, while Felo/Omni remain catalog-only. Neither menu nor matrix is the provider universe.

Use `scripts/ops/provider_population_census.py` to regenerate a source-hashed census. The native validation workflow uploads a `provider-population-census` artifact after provider receipts are collected; the g4f workflow uploads a separate census artifact that includes its current bounded-batch receipt. Always preserve the definitions above when reporting counts; never label 7 arms, 31 menu choices, 92 wiring records, or 9,588 enumerated g4f pairs as the full active endpoint population.

- The same desk-feed also contains **95 inference-availability records**: 23 wired-unproven, 2 triggerable, 65 inference-only, and 5 proven. Only 16 are covered by the provider-availability probe, 1 is secret-only, 74 are not covered, and 14 have a batch endpoint wired. These are registry-record classifications, not live success counts.
