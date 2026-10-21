# Provider quota upgrade: shipped capability versus remaining gaps

## Current continuation: MSM-023 private OpenRouter current-key service

Baseline `5d54d22f` includes merged Ollama [PR #1462](https://github.com/timerloggedout-spec/termux-monorepo/pull/1462), merge `b92c0c5d`. Current-source inspection found the OpenRouter passive parser, legacy daily-counter reader and boolean-only diagnostic, but no equivalent complete private current-key service wrapper. MSM-023 adds only that missing opt-in observation, using the [official GET /api/v1/key contract](https://openrouter.ai/docs/api/api-reference/api-keys/get-current-api-key) and [limits semantics](https://openrouter.ai/docs/api_reference/limits). See the [service operating contract](PROVIDER-QUOTA-MANAGERS.md#msm-023-private-openrouter-current-key-observation).

**Exact capability delta:** two opt-in private service implementations (Ollama plus OpenRouter), still three mapped provider families, twenty static links, six passive parsers, eleven documentation-only and three unsupported families. Seventeen provider-family mapping gaps remain. OpenRouter was already mapped: this is not a fourth mapped family, twenty live managers or new inference capacity. Public live-account state remains unknown and private account values remain withheld.

The manual `provider-batch.yml` input `observe_openrouter_quota` hard-defaults false and permits only the trusted default branch after offline contracts. Only its private observation step receives the existing named key. Its exclusive private file is outside Git and removed at exit; it uploads no private artifact. Selecting the private input suppresses other provider jobs, including the free-smoke path; conflicting inputs fail closed without an account call. Pull requests and push contract tests receive no secret from this job. There is no schedule, health-check integration, completion/inference, retry, account/key hopping, paid fallback, router or production admission change.

Request-count triplets, monetary key/budget fields and account tier are distinct. `is_free_tier` is not model price. No daily request reset timestamp is invented; local freshness is not a reset. A private read verifies only its credential-selected source observation, not independent account identity or model entitlement.

Historical router [#1441](https://github.com/timerloggedout-spec/termux-monorepo/pull/1441) remains OPEN at `cd95c44848f066ef2a32cf9984b4e36c1172c856`; its earlier changes-requested review has not been superseded by comments. Consolidation [#1278](https://github.com/timerloggedout-spec/termux-monorepo/pull/1278) remains OPEN at `4eae2175c067664af67cb083e994080ef7863625`, explicitly review/do-not-auto-merge. Their router and cron changes are not part of this continuation. Continue owning issues [#86](https://github.com/timerloggedout-spec/termux-monorepo/issues/86) and [#272](https://github.com/timerloggedout-spec/termux-monorepo/issues/272); no duplicate issue or proposal is required.

The existing [collaborator capability map](PROVIDER-COLLABORATOR-CAPABILITY-MAP.md) remains authoritative for monikers, declared roles, workflow permissions, ICM context delivery and MCP bindings. Provider adapters do not confer GitHub agency; shared-account commits/comments do not identify a provider author. Delphi remains rubric-only without new independent ballots. This change supplies no new agent permissions or connector bindings.

Offline validation passed 149 focused quota/service/workflow/dashboard tests, 314 broader provider/runtime tests and nine market unittests; the existing unrelated `datetime.utcnow()` deprecation warning remains. Both local gates, snapshot freshness and the 39-proposal registry passed. Technical review findings for empty payloads, expired resets and key-specific scope were corrected with regressions. Exact-head CI and release/live-read receipts belong to this continuation's implementation PR, bound to exact source SHA. Earlier deployment or test receipts below do not certify this continuation.


## Historical continuation: MSM-022 private runtime service

Starting from `30ac753b` (after merged baseline [#1457](https://github.com/timerloggedout-spec/termux-monorepo/pull/1457)), this continuation adds the first explicitly opt-in private balance-service wrapper in `scripts/provider_quota_service.py`, using the [official Ollama Balance API](https://docs.ollama.com/api/balance). It performs a real supported HTTPS transport when explicitly invoked, unlike the prior injected-only transport. No provider account call was made during development. Source scope is credential-selected user/shared Team, with identity explicitly unverified because the endpoint returns no identity. USD balances, legacy percentages, source resets, freshness, request quota and entitlement remain distinct. See [runtime contract](PROVIDER-QUOTA-MANAGERS.md#msm-022-opt-in-runtime-balance-service).

| Evidence class | Before | After | Meaning |
|---|---:|---:|---|
| Canonical provider families / static adapter links | 20 / 20 | 20 / 20 | Complete roster, not account coverage |
| Actual model-provider service registry mappings | 2 | 3 | Adds implemented opt-in `ollama.balance`; Gemini and OpenRouter retained |
| Missing actual service registry mappings | 18 | 17 | One mapping/implementation gap closed |
| New opt-in private service-manager implementations | 0 | 1 | This explicit-activation service path only; not a census of legacy readers |
| Passive offline adapters | 6 | 6 | Not promoted to live accounts by this implementation |
| Documentation-only / unsupported quota contracts | 11 / 3 | 11 / 3 | Official source matrix unchanged |
| Live-account-validation gaps closed by this batch | 0 | 0 | All 20 public account states remain unknown; no new account was observed |

The prior 18 combined runtime/account gaps are **not** all closed: Ollama's production transport/persistence/freshness implementation is supplied, but its live credential-selected account and independent user/Team identity remain unvalidated. Seventeen families still lack provider-specific service registration. Eleven documentation-only families lack a complete source-backed remaining/reset contract; Aion, Felo and Omni remain unsupported. The [per-provider source matrix](PROVIDER-QUOTA-MANAGERS.md#evidence-reviewed) preserves the specific blockers. Groq/SambaNova require genuine response observations; Hugging Face Hub limits are not hosted-inference capacity; SiliconFlow monetary balances do not establish request quota/reset. Gemini's registry row is not a live manager.

The existing quota dashboard now shows opt-in private service implementations separately from quota-service mappings, static adapter links and passive parsers, with live accounts still unknown. Neither the dashboard nor a private balance record grants admission. The dedicated `model-balance` registry lane prevents the resource from entering legacy routing-weight generation. No inference, paid fallback, credential mutation, routing/admission/weight or schedule changes occurred; the new service is not inserted into `quota_poll.LIVE` or any automatic collector.

Existing [issue #86](https://github.com/timerloggedout-spec/termux-monorepo/issues/86), [issue #272](https://github.com/timerloggedout-spec/termux-monorepo/issues/272), [router PR #1441](https://github.com/timerloggedout-spec/termux-monorepo/pull/1441) and [consolidation PR #1278](https://github.com/timerloggedout-spec/termux-monorepo/pull/1278) remain the owning lanes; no duplicate issue/proposal was created. GitHub API verification observed #1441 OPEN at `cd95c44848f066ef2a32cf9984b4e36c1172c856`, merge commit absent; its earlier `CHANGES_REQUESTED` review is not superseded by later `COMMENTED` events. Public rendered-page ambiguity is not merge evidence.

Initial offline validation: 122 focused quota/service/dashboard/poller/Delphi tests, 314 broader provider/runtime tests and 9 market unittests passed. The broader suite reports one existing `datetime.utcnow()` deprecation warning in `deepcli/agent.py`, unrelated to this service. Coverage freshness and the 39-proposal registry validation passed. Current-head CI, independent technical review, merge and deployment receipts must be recorded on the implementation PR; the historical receipts below do not certify this continuation.

## Historical continuation: MSM-020 / MSM-021


This batch starts from current `master` in a separate worktree, preserving the prior checkout and unrelated worktrees. It implements one newly supportable official remaining-balance contract rather than inventing quota counters for the other providers:

- **Ollama:** [official Balance API](https://docs.ollama.com/api/balance), modern included/purchased USD pools and explicit UTC period bounds, or legacy session/weekly remaining percentages and reset timestamps. The uniform passive parser validates both variants and rejects malformed/mixed groups. `scripts.provider_quota_transport.observe_ollama_balance` supplies a fixed-URL GET interface with an explicitly injected trusted transport, bounded timeout/body contract, redirects disabled, sanitized errors, and no retries or default network client. All execution evidence is synthetic fixture testing, not live validation.
- **All twenty static adapter links:** `ops/quota/static-service-mappings.json` cites existing in-repo endpoint rosters and feeds the existing coverage/dashboard path. Static roster links are not runtime quota resources. The dashboard separately displays static links, actual service mappings, parser implementation and unknown live account state.
- **Official contract re-curation:** eleven families remain documentation-only and three unsupported. Cloudflare billing consumption, Kilo inference cost, Cerebras console exports, public ceilings and dynamic concurrency do not become fabricated remaining quota. See [source matrix](PROVIDER-QUOTA-MANAGERS.md).
- **Attribution:** refreshed [capability evidence](PROVIDER-COLLABORATOR-CAPABILITY-MAP.md) separates the Cue profile, repo roles, adapters and GitHub actors. Account-attributable commits/comments are not provider-authored contributions, and Delphi remains rubric-only with no new independent ballots.

**Exact gap accounting:** passive adapters increase **5 → 6**; documentation-only decreases **12 → 11**; unsupported stays **3**. Static adapter-link inventory becomes **20/20**, but actual quota-service mappings remain **2/20** and the **18 runtime service/account-manager gaps remain open**. This batch closes **zero live manager gaps**. The Ollama private transport is ready for a separately authorized integration, not registered as a live reader or fed into request-count admission. No account API call, inference request, paid fallback, credential mutation, router weight, production admission or schedule change occurred.

The focused manager/transport/coverage/dashboard/poller/Delphi suite passed 98 tests. A separate read-only technical review found no additional actionable issues; transport context/key/method/body-contract hardening has dedicated regressions. Existing provider CI now includes the new transport and static mapping paths. Exact-head CI, merge and publication receipts belong to this batch's PR timeline; no earlier deployment certifies these changes.

Existing router [PR #1441](https://github.com/timerloggedout-spec/termux-monorepo/pull/1441) remains open at observed head `cd95c44848f066ef2a32cf9984b4e36c1172c856` with the prior changes-requested review still recorded. Its owner reported fixes and requested renewed disposition. Consolidation [PR #1278](https://github.com/timerloggedout-spec/termux-monorepo/pull/1278), observed head `4eae2175c067664af67cb083e994080ef7863625`, remains a separate open lane explicitly marked review/do-not-auto-merge. Neither lane is duplicated, merged or activated here. Continue issues [#86](https://github.com/timerloggedout-spec/termux-monorepo/issues/86) and [#272](https://github.com/timerloggedout-spec/termux-monorepo/issues/272).

## Prior merged batch: historical MSM-019 receipt

Implementation and release receipts: [PR #1448](https://github.com/timerloggedout-spec/termux-monorepo/pull/1448). Its current-head checks, merge state and exact-source publication verification are authoritative; this checked-in snapshot is not a self-certifying release approval.

## What this upgrade supplies

All **20 canonical provider families** now have an explicit manager-evidence record in [`ops/quota/provider-managers.json`](../../ops/quota/provider-managers.json). This is complete inventory coverage, **not 20 live quota managers**. The existing service registry still contains 26 resources and only two model-provider mappings (Gemini and OpenRouter); the other 18 service-mapping/account-manager gaps are not silently declared closed.

- **Five passive offline adapters:** Groq and SambaNova documented request/token headers; Hugging Face Hub rate-limit metadata (not hosted inference quota); OpenRouter documented free daily counter/key budget fields; SiliconFlow monetary balance strings (not request quota, no assumed currency). No new account calls occur.
- **Twelve documentation-only families:** Cerebras, Cloudflare, Cohere, Gemini, Kilo, LLM7, Mistral, ModelScope, NVIDIA, Ollama, OVHcloud and Z.ai. Their official-source scope/reset evidence is curated, but a complete remaining-capacity parser/live manager is not claimed.
- **Three unsupported quota contracts:** Aion, Felo and Omni have first-party links but no sufficiently established quota counter/reset contract.

The [provider-by-provider evidence table](PROVIDER-QUOTA-MANAGERS.md) states precisely what each source supports. Monetary balance, cumulative usage, public limits, free-account entitlement and remaining request/token quota are distinct. Missing observations remain unknown; no reset instant is inferred. Scope supplied to a parser remains caller-declared and unverified.

The public dashboard distinguishes static manager capability, service mapping, documented scope/reset policy, unknown account evidence and unpublished balances. Manager ownership (`Manager`) and freshness ownership (`ChronoMancer`) remain the existing responsibility labels, not new autonomous agents or proof that a live collection/reservation system ran. The quota-only evaluator is still not wired into runtime admission.

## Dashboard publication evidence

The previously merged quota/dashboard revision from PR [#1446](https://github.com/timerloggedout-spec/termux-monorepo/pull/1446), merge `7c5e0c2b`, is now published through the existing [help-wanted deployment run 39576915984](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39576915984), source `09d59cc767e522e1f70a0c4a9aeb594027389699` (the intervening source changes did not change these quota assets). This resolves the formerly missing helper and JSON:

- [Public quota UI](https://timerloggedout-spec.github.io/help-wanted/quota.html)
- [Evidence helper](https://timerloggedout-spec.github.io/help-wanted/quota-evidence.js)
- [Coverage snapshot](https://timerloggedout-spec.github.io/help-wanted/data/provider-quota-coverage.json)

All three returned HTTP 200 and matched the workflow source bytes. That verification applies to the published MSM-018 revision, not automatically to a later unmerged implementation. MSM-019 publication must be tied to the final implementation merge/source SHA and fresh live-asset comparisons in its PR timeline. No Vercel deployment was requested; its optional workflow job was skipped. Public static assets do not prove a working account or fresh private quota.

## Private data boundary tightened

The existing quota-probe workflow previously uploaded raw quota records/routing weights and printed account counts in summaries. Its new `--public` path uploads only an allowlisted `quota-public-status.json`, with statuses `private_preflight` or `unknown`. Reader stdout/stderr, private counts, balances, reset observations, routing weights, retention records and hashes of private records are withheld. Public mode rejects a nonempty output directory so old private files cannot be accidentally included.

The default **private** CLI output and existing router behavior remain separate and unchanged. The public workflow no longer emits legacy numeric `QUOTA count24h=` lines; a consumer depending on those public logs must migrate to a separately authorized private execution path. No existing scheduled job or router was modified or dispatched here. Historical artifacts were not deleted or rewritten.

## Collaborator roles, tools and actual participation

The [collaborator capability map](PROVIDER-COLLABORATOR-CAPABILITY-MAP.md) lists all 20 provider monikers, declared roles/adapters/callable identities, concrete workflow permission scopes, context-delivery paths and MCP bindings. It separately identifies declarations, implementation, bounded observed GitHub activity and unverified attribution. Repository settings do not change a persistent assistant profile.

Provider transport does **not** grant GitHub agency. OpenRouter's `routeMesh` is an adapter-only routing/catalog/inference lane; no independent OpenRouter account participation is established by that declaration. Actual sampled review/comment/commit actors are cited in the capability map. A shared authenticated account or claimed model trailer does not establish which model wrote an action. A declared MCP service is not proof that a particular collaborator received or exercised it.

Delphi stays rubric-only: deterministic rubric scores are not model ballots, independent reviews or proposal consensus. Real human/independent ballots, review provenance and permission to involve live providers remain separate evidence requirements.

## Existing work curated, not replaced

Continue the existing [rate-limit issue #86](https://github.com/timerloggedout-spec/termux-monorepo/issues/86), [Gemini quota/routing issue #272](https://github.com/timerloggedout-spec/termux-monorepo/issues/272), and proposal items rather than opening 18 duplicate issues. Existing [router quota integration PR #1441](https://github.com/timerloggedout-spec/termux-monorepo/pull/1441) remains a separate lane (observed head `75e193033d29cbfc68d95f0be469215543ee2cee`, CodeRabbit changes requested); [consolidation PR #1278](https://github.com/timerloggedout-spec/termux-monorepo/pull/1278) was open at observed head `4eae2175c067664af67cb083e994080ef7863625`. Neither is merged or activated by this overlay.

MSM-019 implements the metadata/passive-parser/publication-safety slice under the existing model-selection proposal. It is not a claim that all historical proposal work is complete or that the 18 missing live managers are fixed.

## Validation and release requirements

The broad offline provider suite passed 314 tests, the focused manager/coverage/dashboard/poller/Delphi slice passed 88 tests, and the market unittest suite passed nine tests. The coverage snapshot freshness check, proposal registry validation (39 proposals), dashboard control-surface check, workflow-run contract and YAML parsing passed. A separate read-only technical review found the nested-public-signal allowlist and extreme UTC timestamp normalization needed hardening; both were fixed with regressions. A source-encoding check also keeps undocumented SambaNova reset units unparsed. This is technical review, not a formal GitHub review or independent Delphi ballot.

Promotion still requires both named automated gates on the **current** candidate SHA, provider-contract CI, mergeability and verified task outcome; prior green checks do not authorize a later head. The implementation PR/action receipts are authoritative for promotion and any later deployment. There were no inference calls, paid fallback, account/key hopping, credential/profile changes or production-admission changes.

## Still open

1. Obtain authorized, fresh, account/model/project-bound observations and precise source contracts before implementing additional live managers. Documentation-only/unsupported providers remain unknown at runtime.
2. Implement or reconcile the 18 missing provider service mappings, private freshness/reset handling and shared quota reservation in their existing lanes; passive parsing alone supplies none of these.
3. Complete separate router integration review and tests; do not treat a quota-only `allow` reason as execution permission.
4. Preserve authenticated GitHub action provenance and distinct actor/model attribution; collect genuine ballots where the proposal process requires them.
5. Verify every published revision against its own deployment SHA; a successful old deployment does not certify a newer snapshot.
