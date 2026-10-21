# Provider quota upgrade: shipped capability versus remaining gaps

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
