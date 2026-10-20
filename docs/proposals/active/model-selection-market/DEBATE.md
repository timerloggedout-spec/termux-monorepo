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
