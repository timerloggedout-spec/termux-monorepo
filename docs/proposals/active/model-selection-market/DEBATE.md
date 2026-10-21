# MSM-006 / MSM-007 implementation record

## Driver proposal: Q

Implement the user's prioritized free-provider research inside the existing model-selection-market package. MSM-006 ingests pinned public source metadata and proposes only research snapshot updates. MSM-007 computes offline advisory posteriors, signed-review summaries, observed transitions and dependency-aware Cadence plans. No production weights, provider eligibility, secrets, account balances, or merge authority are inferred from research or synthetic DSPy examples.

The workflow reuses the existing daily catalog completion event rather than adding another cron. Publication is restricted to one generated JSON path and explicitly requests the existing dual gates. The importer never executes upstream code or contacts imported endpoints. Full design and reproducible commands: [Provider research compounding](../../../ops/PROVIDER-RESEARCH-COMPOUNDING.md). Research sources and licensing: [provider brief](../../../ops/FREE-LLM-PROVIDER-RECON.md).

## Validation and disposition

Local module and workflow contract tests, repo-gate and termux-smoke are required. Live source ingestion is separate evidence from live inference, which is not part of this slice. Independent implementation review is requested before promotion. A green local test does not mean a deployed workflow or merged PR; remote run/commit evidence belongs in the implementation PR.

No proposal-wide acceptance or closure is claimed. Existing routing/promotion policy remains authoritative. Further provider adapters, causal DOE, DSPy optimization, authentic reviewer identity and real-outcome ingestion require separate scoped items and evidence.

## Independent implementation review

A separate read-only reviewer ran the focused suite (43 passed at the reviewed revision) and found no workflow-run trust-boundary issue. It identified a medium retry-state ambiguity for closed, unmerged refresh PRs. Resolution: a closed proposal whose snapshot is absent from master now raises an explicit terminal error; automatic reopening is deliberately unsupported so the loop cannot override a deliberate rejection. A regression test asserts no writes occur. This is an item-scoped technical review, not proposal-wide acceptance or an authenticated Delphi vote.

## MSM-008 — complete resource coverage and offline aggregate search

Q extends the existing package and workflow with a reviewed resource registry covering all 20 supplied link occurrences (19 canonical references), the five named service surfaces and the optional prior gpt4free reference. Native implementation paths and next actions are explicit. General directories, search queries, discussions, templates and provider pages retain distinct kinds; none becomes runtime authority. Hex remains one optional analytics projection alongside independent storage and compute surfaces.

The stdlib index joins registry references with existing commit-pinned provider claims, preserves source and input attribution, and supports deterministic offline AND-token search plus role/kind filters. The existing research collection job builds the combined index from its freshly collected provider snapshot and retains it as a same-run artifact. No new cron, provider account, secret scope, recursive crawler, routing mutation or publisher write path is added. Larger source ingestion and actual multi-provider runtime/failover require separate tested adapters and admission evidence.

Issue #184 and all 80 returned comments were consulted as a names-only authorization inventory. No service credential value was recovered or needed for this implementation. Repository Actions secret-name listing returned HTTP 403; service secret presence therefore remains unknown. No secret or permission was changed. The matrix links official product/pricing sources while explicitly avoiding a general free-tier or account-entitlement claim.

Promotion requires focused contracts, exact supplied-input coverage, CLI reproduction, independent review, local dual gates and SHA-bound remote dual gates. Run evidence and final disposition belong to the implementation PR; a local build alone is not deployment evidence.

### MSM-008 independent review and resolution

A separate read-only reviewer confirmed all supplied-link counts, same-run index construction, literal-false runtime eligibility, null candidate quota, offline stdlib behavior and unchanged workflow/publication trust boundaries. Its 15 focused resource tests passed. It found one P2 completeness issue: snapshot-level integration references and original blocking reasons were omitted from the aggregate. Resolution: preserve both as `provider_integration_references` and `provider_blocked_reasons`, with a regression using the real checked-in snapshot. No release-blocking security issue was found. Final local validation after the fix: 60 focused contracts plus nine legacy market tests; repo gate, Termux smoke and workflow-run contract pass. SHA-bound remote gate and deployment receipts remain recorded in the PR rather than inferred from these local results.

## MSM-009 — production GitHub anonymous-rate-limit recovery

MSM-008 merged as PR #1297 after current-head repo gate, Termux smoke and contracts passed on `515c47b620a64f5cc3574e2ba9a30b283a0aadb7`. Deployed run [39376417124](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39376417124) then passed contracts but failed collection with `HTTP Error 403: rate limit exceeded` during GitHub commit metadata resolution, before any snapshot/index output. Publication was skipped and no artifact existed. This negative outcome is retained; it is not reported as a successful deployed refresh.

The focused recovery uses the collect job's already read-only `contents: read` token, supplied explicitly through `PROVIDER_RECON_GITHUB_TOKEN` only to the collection step. Authorization is attached only when the entire URL exactly equals one of the two fixed upstream commit-metadata endpoints. Raw source downloads, arbitrary GitHub API paths, alternate ports and query variants receive no token; redirects remain prohibited. Malformed header credentials fail without echoing them. Local public collection remains possible without the optional token. No retry loop, permission grant, service activation, publisher path or production routing changes. Transport regressions exercise the exact allowlist and no-forwarding boundaries.

MSM-009 independent read-only review found no blockers: authentication was confined to the two exact metadata URLs; raw, other-repository, query-modified and alternate-port requests carried no authorization; malformed credentials were not echoed, and redirects remained blocked. Its ten collector tests passed before the additional workflow step-scope assertion. Final scoped regression suite contains 65 tests, plus nine legacy market unittests. Production success still requires a new successful deployed run; the original anonymous-rate-limit failure remains part of the evidence.

## MSM-010 / MSM-011 — native provider batch and review provenance

Q implements the user's follow-through request as official Groq, Mistral and Gemini catalog adapters plus native hub routes, gated by exact-model expiring account admission. All 160 research claims receive a source-preserving reconciliation disposition; unsupported families remain unimplemented, not claimed enabled. Existing evaluation defaults, production weights, publisher path and provider research eligibility remain unchanged. No upstream proxy is executed and no live inference or free account entitlement is asserted from directory labels. Design and primary API references: [provider batch](../../../ops/PROVIDER-BATCH-IMPLEMENTATION.md).

Production tests use the active native catalog and hub HTTP entry points, the real checked-in candidate identities, and actual GitHub API response structures. Initial live review reconciliation exposed two realistic gaps missed by synthetic fixtures: commit URLs use `/commit/<sha>` and PR commit objects have a SHA rather than a numeric ID. These are corrected with real-shape regressions before promotion. Native adapter review also checks qualified Groq IDs (`openai/gpt-oss-120b`), so a generic model-name test cannot hide a rejected harvested identity.

PR #1297's complete retrieved event population contains zero submitted formal reviews, 21 conversation comments and zero inline comments. Q/independent-review/Grok moniker narratives are recorded claims, not authenticated human authorship or formal consensus. MSM-011 adds an offline normalizer and a trusted read-only production collection lane, with separate event counts and null commit attribution preserved. No fabricated reviewer scores or observations enter Cadence or Moneyball.

A new manual default-branch observation uses Actions credentials only in the catalog step and the read-only job token only in the GitHub review step. No new cron, inference, external provisioning, secrets extraction, permission grants or routing activation occurs. Fresh research run 39377722728 passed all three jobs and its downloaded artifact contains 160 candidates and 185 aggregate records, confirming #1298 recovery independently of the still-denied secret-name API. Promotion still requires final exact-head dual gates, focused contracts and verified artifacts; receipts belong to the implementation PR.

### Independent batch review and resolution

A separate read-only technical reviewer passed 35 reconciliation/workflow tests and found two P2 provenance gaps: head pagination was not race-checked and retrieval time was missing. Resolution: the production collector records UTC collection start, re-fetches the PR head after all pages, and refuses changed heads or a commit list missing that head. The normalizer preserves each review commit ID and explicitly labels counts as PR-history counts, not current-head approvals; normalization time and collection time are distinct. New atomic-failure regressions cover both race and missing-head states. This local technical review is not counted as a submitted GitHub formal review.

### MSM-010 production credential-name reconciliation

PR #1299 merged after exact-head dual gates and batch contracts passed. Production run 39378596101 then passed contracts and observation; its artifact contains 578 live catalog rows (470 OpenRouter, 45 Felo, 63 Gemini) and 160 reconciled claims (22 observed matches, five catalog misses, 15 unavailable, 116 unimplemented, two aggregate labels). No runtime admission was activated. Groq, Mistral, Omni and the three previously accepted Hugging Face token names were missing in this Actions context. Saved-secret searches for these four services returned no matches. Inventory review found one remaining authorized alias, HF_TOKEN, already recognized by the native availability probe. The narrow follow-up accepts that alias as last precedence in the batch collector and local catalog only; it changes neither permission scopes nor token values. A new production observation determines whether that alias actually exists; naming support alone is not evidence of configured access.
