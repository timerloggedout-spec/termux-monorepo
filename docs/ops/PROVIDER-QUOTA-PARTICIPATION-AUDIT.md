# Provider quota and participation audit

**Implements: MSM-018**
**Snapshot:** repository `master` at `b371f52` (2026-10-21); read-only GitHub inspection.
**Scope:** existing quota managers/dashboards, provider research and proposals, Scout/Manager/Orchestrator/ChronoMancer/SWE/Reviewer role and moniker contracts, context/connectors/MCP boundaries, and a bounded sample of GitHub activity. The audit separates the existing baseline from the implemented MSM-018 upgrade below; it is not a ballot, runtime authorization or live provider test.

## Baseline findings before this upgrade

### Quota and provider surfaces already exist

| Surface | Existing responsibility | Audit finding / boundary |
|---|---|---|
| [`ops/quota/registry.json`](../../ops/quota/registry.json) + [`QUOTA-REGISTRY.md`](QUOTA-REGISTRY.md) | Provider/service quota metadata with source, window/reset, live endpoint and planned-use notes; includes model/API, CI, deploy and data services. | Broad service coverage is not equivalent to exhaustive model-family coverage. Several service limits are explicitly unknown or based on stale/unrefetched planning notes. |
| [`scripts/quota_poll.py`](../../scripts/quota_poll.py) | Credential-gated, stdlib readers; writes quota records, hindsight records and 3L0 weights; no secret values in output. | Actual `LIVE` mapping is just GitHub API/cache, Vercel deployments and OpenRouter free-model usage, plus Render/Neon readers. Registry entries without reader coverage remain documented/unknown. Gemini soft budgets are maintained elsewhere, not through this poller. The poller sets `H0` when a live value exists and `H1` otherwise; absent readings must not be treated as live quota. |
| [Quota workflow](../../.github/workflows/vercel-quota-probe.yml) | Manual dispatch; read permissions, sparse checkout, artifact output (7-day retention), no scheduled second monitor or committed poll results. | Existing implementation/manager to extend; do not create another poller or dashboard. Workflow summary only prints records with non-null `used`; absence from summary is not an available balance. |
| [Free quota windows](FREE-QUOTA-WINDOWS.md) and [reset contract](QUOTA-RESET-CONTRACT.md) | Entitlements vs balance; cadence and authoritative reset observation. | Public entitlement is not account balance; unknown is a valid state, not reset or admission. No paid fallback or account hopping. |
| [Quota TUI](../../scripts/quota_tui.README.md), [help-wanted dashboard](../../apps/help-wanted-dashboard/quota.html) and [`quota.json`](../../apps/help-wanted-dashboard/data/quota.json) | Existing display surfaces. | Visibility is fragmented: generated poll artifact, TUI and quota page are separate; audit found no evidence that all provider families or age/unknown state are unified in one view. Upgrade an existing surface with explicit observed-at/source/status and stale/unknown labeling; do not replace it. |
| [Provider catalog](../../scripts/provider_model_catalog.py), [batch implementation](PROVIDER-BATCH-IMPLEMENTATION.md), [free-provider research](FREE-LLM-PROVIDER-RECON.md), [prioritization proposal](../proposals/active/free-llm-provider-prioritization/DEBATE.md) | Catalog and research evidence, adapter status and admission policy. | Current claims: 117 exact directory model claims have chat transport coverage across 16 families; catalog coverage 15/16; these are not 117 inferences, entitlements, or available quotas. The proposal says ballots are empty and runtime admissions zero. Preserve these distinctions. |

Quota is capacity evidence, not model quality or proof that an account may invoke a model. Dashboard improvements should present (at minimum) provider/model or service identity, source, observed UTC timestamp, reading/status (`observed`, `documented`, `unknown`, `stale`, `error`), reset basis, and whether the value is account-authoritative. Never turn a catalog claim or stale number into live remaining quota.

### Provider quota work already in flight: curate, do not duplicate

Known merged work:

- [PR #1321](https://github.com/timerloggedout-spec/termux-monorepo/pull/1321), merged 2026-10-20: verifies no-cost entitlement before existing-token inference and adds smoke/inventory validation.
- [PR #1325](https://github.com/timerloggedout-spec/termux-monorepo/pull/1325), merged 2026-10-20: records a verified free-token smoke and HTTP 429 blocker.
- [PR #1326](https://github.com/timerloggedout-spec/termux-monorepo/pull/1326), merged 2026-10-20: diagnoses 429 safely without another inference request.
- [PR #1441](https://github.com/timerloggedout-spec/termux-monorepo/pull/1441), **OPEN** at inspection: “reconcile official quota before dispatch.” Its head already contains quota preflight, live routing weight/cooldown, unknown-quota denial, local reservation reconciliation, and diagnostics work. It has a CodeRabbit `CHANGES_REQUESTED` review at the inspected head. MSM-018 explicitly must not duplicate this implementation. Curate a future scoped follow-up only after reconciling with this PR's latest head and review disposition.

These are GitHub PR state/content observations, not a claim that every behavior passed production or is deployed to every route. Their existing descriptions and implementation docs remain the more detailed source of truth.

### Roles, identities and context/connectors

The role architecture is present but spread across multiple SSOTs: [control-plane](../architecture/AGENT-TEAM-CONTROL-PLANE.md), [orchestration contract](AGENT-TEAM-ORCHESTRATION.md), [agent roster](AGENT-TEAM-ROSTER.md), [moniker SSOT](AGENT-MONIKERS.md), and [machine roster schema](../schemas/agent-roster.yaml). Relevant role responsibilities are:

| Role | Established scope | Evidence boundary / gap |
|---|---|---|
| **Scout** | Discover/normalize provider, model, task and source candidates; report provenance and uncertainty. | Discovery grants no activation authority. |
| **Manager** | Policy layer selects task decomposition, context scope, lanes, waiting, admission, integration and promotion/culling. | A declared manager policy is not proof of execution or improved outcome; compare attributable outcomes. |
| **Orchestrator** | Executes only an authorized policy, enforcing capability/health/quota gates and bounded retries/cooldowns; records routing evidence. | A selected route is not a run. Evidence must connect workflow/run, job, step, SHA and outcome. |
| **ChronoMancer** | Time-bounded observations, expiry/refresh cadence, quota-window semantics and change history; stale evidence becomes unknown/ineligible. | This is a named role in provider research, not an independent provider entitlement source. |
| **SWE / Builder** | Smallest useful implementation with commit/SHA and tests; development-lane docs use “Builder.” | SWE is not a provider/model identity; contribution is evidenced by code changes and tests. |
| **Reviewer / Review** | Correctness/security/regression critique and a recorded review disposition. | Bot comment, acknowledgement, or requested review is not approval; formal review state and commit must be recorded. |

Display monikers are intentionally distinct from callable handles and GitHub identities. `AGENT-MONIKERS.md` lists e.g. CodeRabbit display `codeHound` with callable `@coderabbitai`; provider lanes such as `routeMesh` and `feloForge` are explicitly non-callable display identities, not authors. Do not @-mention a display name as though it were a handle.

ICM's [routing map](../icm/CLAUDE.md) requires selective context loading: map → one relevant object/process card → cited sources. The provider-routing card ([`routing/CONTEXT.md`](../icm/routing/CONTEXT.md)) is documentation for observations and governance, **not runtime router configuration**; it states its poller is not configured and cadence not approved. Treat the system's connectors and workflows as separate executables: `.github/connectors/llm_providers.yaml` and provider workflows describe configured surfaces, while provider capabilities and credentials must still be explicitly admitted. [MCP risk split](../proposals/active/mcp-hub-risk-split/DEBATE.md) draws the boundary at stateless/read-only `mcp-hub` vs device-touching `hub_mcp`; presence of MCP documentation or a connector is not authorization to poll providers, operate a device, or route inference. The [provider capability registry](../schemas/provider-capabilities.md) describes contracts, not proof that each connector is configured or has run.

### Permissions versus actual activity

[Agentic permissions](../proposals/AGENTIC-PERMISSIONS.md) describes what an agent may do in principle (read repo/PRs, files/branches, PRs/comments/reviews/merge when allowed) and permission gaps/human-only edges. This does not establish that a connector actually holds each scope or that a particular role performed an action. Credential rotation, provider API keys/browser logins, history rewrite and first-time permission grants remain bounded human edges. Secrets are not part of this audit.

**GitHub sample and attribution method.** Read-only connector inspection covered four user-specified quota PRs (#1321, #1325, #1326, #1441), not a census of repository contributions. For each, inspected PR author/state/URL, commit author and headline, plus available formal review metadata. PR authorship was `timerloggedout-spec` for all four. Commit metadata in this sample: #1321's two commits and #1325's one commit list `cue-agent`; #1326's commit lists `timerloggedout-spec`; #1441's inspected commits list `timerloggedout-spec`. No formal submitted reviews were returned for the three merged PRs in this sample; #1441 has one CodeRabbit `CHANGES_REQUESTED` review. These distinguish PR account author, commit author and reviewer event; they do **not** prove the underlying model, prompt, account operator, or independent human authorship. PR comments include automated collaboration and platform status signals, not ballots or correctness evidence. No votes are inferred.

This task's attributable contribution is this audit document, authored by the current Cue-assisted documentation worker for the requested worktree and scope (2026-10-21). This attribution labels the work session, not an LLM/model identity or GitHub account. No independent vote is cast, no existing ballot is changed, and no provider model is claimed to have generated any source-code contribution.

## Existing work to curate, not recreate

Earlier [issue #86](https://github.com/timerloggedout-spec/termux-monorepo/issues/86), [per-model Gemini issue #87](https://github.com/timerloggedout-spec/termux-monorepo/issues/87), [OpenRouter issue #88](https://github.com/timerloggedout-spec/termux-monorepo/issues/88), and [leader issue #272](https://github.com/timerloggedout-spec/termux-monorepo/issues/272) establish that quota, rotation and per-model visibility are longstanding work, not newly discovered requirements. The existing [rate-limit-rotation items](../proposals/active/rate-limit-rotation/ITEMS.md) retain RL-09 (per-model dashboard) and RL-16 (shared global counter, deferred); this slice does not relabel either as deployed. [PR #1278](https://github.com/timerloggedout-spec/termux-monorepo/pull/1278) is separate cron-consolidation work marked review/no-auto-merge and remains untouched. [Issue #1314](https://github.com/timerloggedout-spec/termux-monorepo/issues/1314) owns Vercel pre-exhaustion admission/failover, not inference admission.

The existing service RFPs include [Gemini #1425](https://github.com/timerloggedout-spec/termux-monorepo/issues/1425), [OpenRouter #1426](https://github.com/timerloggedout-spec/termux-monorepo/issues/1426) and [vendor pool #1427](https://github.com/timerloggedout-spec/termux-monorepo/issues/1427). The inspected [OpenRouter ledger comment](https://github.com/timerloggedout-spec/termux-monorepo/issues/1426#issuecomment-6310432412), posted by `github-actions`, records five `via: rubric` role scores and a parked result. Those are real generated issue comments, **not independent model or human votes**. The provider-prioritization debate's independent-ballot gap must not be confused with the separate rubric RFP ledger.

## Implemented upgrade and residual gaps

MSM-018 derives coverage for **20 canonical provider families** and **26 registered service resources**. Only Gemini and OpenRouter have provider-specific model-quota registry mappings; only OpenRouter has an implemented reader among those mappings. The remaining **18 families** explicitly show missing model-quota mapping; Cloudflare D1/Queues allowance does not cover Workers AI inference. Registered readers are source capabilities, not fresh account evidence or deployed per-provider workers.

The web panel, terminal renderer and text snapshot now show safe coverage and evidence age/unknown semantics; model-account details stay private. A reusable private-input quota checker validates fresh confirmed scoped evidence, cooldowns and a one-request safety margin but is **not wired to runtime admission**. Separate exact no-cost policy remains mandatory. No distributed reservation lock or all-provider live quota API is claimed.

Audit found the existing Delphi workflow selected model mode from key presence, and its direct model path lacked the exact-model no-cost/quota admission boundary. This upgrade fixes the job to rubric-only, removes provider credentials from its environment, and makes the compatibility model-vote hook return no ballot even when legacy environment flags request one. No historical vote or RFP result is changed. Any future model-ballot implementation needs a separate validated admission contract; rubric signatures alone cannot establish independent participation.

Residual work, curated under existing items rather than duplicated:


1. Define exhaustive expected quota coverage by provider/model family and service, then report missing readers and unknown/stale states rather than implying registry breadth equals live coverage.
2. Reconcile the quota poller and dashboard/TUI with open PR #1441's live preflight behavior. Preserve the existing owner, safe semantics and surfaced failure states; do not add a competing dispatch gate or duplicate quota manager.
3. Make a dashboard expose timestamps, source/authority, unknown/stale/error and reset uncertainty consistently. Do not label documentation-only allowances as balance or admission.
4. Keep role, moniker, connector/MCP, GitHub actor and model/provider dimensions separate in any participation ledger. Correlate event, PR/issue, workflow/job/step, commit SHA and review/comment type; record attribution confidence and leave model null absent invocation-bound evidence.
5. Validate offline with exhaustive coverage, stale/unknown and privacy regressions. No live inference, paid fallback, additional provider request, credential exposure, fabricated ballot or invented participation.

## References and evidence limits

- Repository governance: [`CLAUDE.md`](../../CLAUDE.md), proposal [process](../proposals/PROCESS.md) and [permissions](../proposals/AGENTIC-PERMISSIONS.md); proposal [MSM-018](../proposals/active/free-llm-provider-prioritization/ITEMS.md).
- Role, identity, context and quota sources linked inline above; these are the checked-in contract snapshot at `b371f52`.
- GitHub evidence: linked PRs #1321, #1325, #1326 and #1441, sampled through the configured read-only connector. Attribution is limited to public PR/commit/review metadata visible at inspection; it is not a model identity audit, full historical participation census, or proof of successful runtime quota enforcement.
- No live models/providers were queried. No external comments, issues, or votes were created. The implementation also upgrades the existing quota surfaces and closes the implicit Delphi key-to-inference path; no independent ballot is claimed.

## Review disposition

A separate read-only review checked the quota checker, display helpers and Delphi safety diff with offline tests. It correctly noted that the private quota check trusts caller-supplied evidence provenance and is not end-to-end admission; the API must be fed only by an authenticated, authoritative private adapter. It does not authenticate a `confirmed` string or reserve shared quota.

The reviewer also suggested that TUI rendering still used unclassified raw statuses. That finding does not apply to this candidate: `render()` first replaces the input with `public_readings(services, readings)`, which applies timestamp/authority/privacy rules before either alert selection or service rendering. The full-render stale-OK regression guards this call-chain boundary, in addition to direct classifier tests. No model identity, independent ballot or formal GitHub approval is attributed to the review worker.
