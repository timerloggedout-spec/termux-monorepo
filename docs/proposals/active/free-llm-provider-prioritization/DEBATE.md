# DEBATE — free-llm-provider-prioritization

**Purpose:** Research/RFP feedback prioritization voting matrix for the free-LLM-provider follow-through. This is a proposal for human prioritization, not a record of votes, consensus, provider approval, or runtime authorization. `docs/proposals/Docs Proposals Delphi Oracle Method Debate.md` was not present in the checkout; this document applies the clarified intent within the repository's existing `DEBATE.md` convention.

## Proposal: prioritize evidence closure before provider expansion

Use a Delphi-style, independent human ranking to decide the next scoped work items. Do not treat model counts, directory rankings, agent recommendations, or existing adapters as votes. The ordering below is the **driver's proposed starting order**, subject to human ballots; it is not consensus. Priorities apply to work sequencing only, not provider eligibility.

| Proposed rank | Work item | Evidence / rationale | Proposed disposition and exit evidence |
|---|---|---|---|
| 1 | **Close account and terms admission gaps (HITL)** | [Research brief](../../../ops/FREE-LLM-PROVIDER-RECON.md#free-tier-claims-versus-availability) says catalog labels and public limits do not prove account entitlement; [batch policy](../../../ops/PROVIDER-BATCH-IMPLEMENTATION.md#explicit-account-admission) requires explicit exact-model, account, terms, public-data, and expiry admission. | Operator verifies account identity, no-cost status, terms, data policy, and model eligibility through provider's own account surface. Keep routes disabled if any item is unknown; retain evidence without secrets. |
| 2 | **Observe Hugging Face credential-name parity in production** | All four authorized aliases are now wired consistently across batch, catalog, native chat, and availability paths with offline regressions. [Issue #184](https://github.com/timerloggedout-spec/termux-monorepo/issues/184) records historical canonical `HF_TOKEN`; naming support alone is not proof of a configured secret. | Use the trusted names-only inventory and catalog observation. Never read or print values; missing authorization means unavailable evidence, not proof that the provider or account is absent. |
| 3 | **Close provider-family evidence gaps after direct transport completion** | The [latest expansion](../../../ops/PROVIDER-SERVICE-EXPANSION.md) preserves 117 exact model claims, 6 aggregates and 37 static provider references. All 117 have chat transport coverage; catalog support covers 15/16 families (14 published contracts plus runtime-observed ModelScope). SambaNova is separately integrated; no automatic admissions are asserted. | Preserve exact identities and prove actual account/model availability. Z.ai's catalog remains unverified. Public OVH/ModelScope discovery and keyless research service access need no invented signup, but are not free-account inference evidence. |
| 4 | **Evaluate only admitted, public-data candidates** | [Safe adoption pattern](../../../ops/FREE-LLM-PROVIDER-RECON.md#safe-adoption-pattern-proposal-not-enabled) separates discovery, health, evaluation, and routing; no live inference/account entitlement was established by the research. | Optional, explicitly authorized synthetic/public-data evaluation with bounded requests; publish timestamped outcome and provenance. Evaluation cannot itself activate routing. |
| 5 | **Consider broader proxy/adoption work** | The [research brief](../../../ops/FREE-LLM-PROVIDER-RECON.md#security-privacy-and-terms-risks) treats proxy security/features as claims and warns against cookies/HAR, account hopping, and unreviewed third-party deployment. | Defer unless a separate proposal demonstrates a compelling capability gap, supply-chain review, and provider-sanctioned access. Never default to third-party proxy execution. |

### Decision rule

For a later voting round, each eligible human voter should independently rank the rows (1 = highest priority), identify any disqualifying risk, and cite evidence or explain uncertainty. Registrar publishes anonymized aggregate only after collecting ballots, preserves individual ballots as authorized, and records missing/nonresponse separately. Any tie or unresolved P0/security concern returns to discussion; do not infer consent from silence, comments, author count, or an aggregate ranking. A ranking decides order, not acceptance or activation.

## Term open

```text
term: free-llm-provider-prioritization/rank/1
subject: rank proposed research/RFP follow-through work items
tier: 2 (Light) — ranking only; any activation or security disposition requires its own review
status: open for human ballots
ballot: rank 1–5 independently, or abstain; cite evidence and conflicts
opened: 2026-10-20
```

## Votes

_(none yet — no human votes have been cast or supplied)_

## Attributable feedback and continuation evidence

The authorized repository-admin-capable connector successfully collected all pages for PR #1297 against its head: **0 submitted formal reviews, 21 conversation comments, 0 inline comments, 1 commit**. These are event/provenance counts, not votes or independent prioritization decisions. [The API diagnostic](../../../ops/GITHUB-FEEDBACK-API-DIAGNOSTICS.md) distinguishes the original exhausted installation-token request from the working authorized user path and the trusted-default-branch operator feedback step. No broad token is introduced into PR-code execution or provider requests.

Driver recommendations, not ballots: use keyless public research where available; prioritize verified hard-stop free services before uncertain paid-overflow plans; retain account/terms and Origin-device gaps as explicit HITL items. [Service research](../../../ops/PROVIDER-SERVICE-EXPANSION.md) records current official evidence for Firecrawl, Linkup, Exa and Tavily, and rejects retired GitHub Models. The proposal's ranking remains open and unchanged until genuine independent ballots arrive.

## Open questions

1. Following alias-code parity, which account/terms and production-observation gap should be resolved first?
2. Which provider/model, if any, can an authorized account holder establish as genuinely no-cost and eligible for the intended public-data use?
3. Who is the named human registrar for collecting and publishing independent ballots?

## Scope and guardrails

- This file proposes research/RFP feedback priorities only. It does not amend routing policy, model weights, catalog eligibility, account policy, or deployment authority.
- All implemented adapters are distinct from evidence of invoked models or free accounts. Existing OpenRouter/Felo/Omni routing weights remain unchanged; the user's authorized code work does not supply missing account-entitlement evidence.
- Do not enter API keys, secret values, personal data, or unredacted account screenshots in ballots or repository files.
- No consensus is claimed. Binding outcomes must be recorded through the proposal process and attributable votes; see [PROCESS](../../PROCESS.md) and [consensus tiers](../../CONSENSUS.md).

## MSM-018 — current executor reconciliation (not an independent ballot)

The current Cue-assisted implementation session curates [the quota/participation audit](../../../ops/PROVIDER-QUOTA-PARTICIPATION-AUDIT.md). Existing issues #86/#87/#88/#272 and rate-limit-rotation RL-09/RL-16 remain the historical owners; open #1441 owns triage quota integration. The separate [OpenRouter RFP ledger](https://github.com/timerloggedout-spec/termux-monorepo/issues/1426#issuecomment-6310432412) contains generated `via: rubric` scores, not independent provider-model votes. No new priority score, consensus or independent ballot is asserted. Coverage metadata, a private fail-closed quota check, existing dashboard repairs and rubric-only Delphi safeguards implement the authorized engineering slice; account quota integrations and independent ballots remain unresolved.

## MSM-022 — expanded source discovery (executor evidence, not a ballot)

The user's continued request for broader providers exposed an ingestion defect, not missing Gemini/Groq adapters. Reprocessing the existing hash-verified source files with a bounded static parser surfaces 35 omitted registrations: 72 FreeLLMAPI references and 195 total research records. Exact model claims remain 117. Source-specific aliases connect 16 references to existing chat families; a separate disposition preserves 54 unmapped services, one fixed-public-research adapter and one custom configuration placeholder. [Current expansion notes](../../../ops/PROVIDER-SERVICE-EXPANSION.md#continued-discovery-35-registrations-were-being-skipped) link the pinned registry and official Typhoon/LongCat follow-up evidence. Independent code review identified a helper-spoof provenance edge; the parser rejects shadowed/reassigned helpers and non-standalone calls. This work adds discovery and reporting, not credentials, live inference, free-account entitlement, ranking votes or consensus. Gemini free-tier and quota PR #1441 remain separate and untouched.

## MSM-023 — Typhoon contract implementation (executor evidence, not a ballot)

The [official-contract review](../../../ops/TYPHOON-FREE-API-CONTRACT.md) establishes Typhoon's documented $0 light-use hosted text API, bearer-auth request/response protocol and public 5-RPS/200-RPM model ceilings. A separate pure offline adapter and synthetic fixtures implement this contract without adding an HTTP transport or active registry entry. The existing source identity now links as `offline_protocol_legal_hold`, leaving 53 unmapped service references; the 117 model claims, 16 chat-family mappings and runtime-ineligible state are unchanged. Terms require review because of input-training rights, personal-data prohibition, benchmarking/training/account-sharing restrictions and ambiguous bot language; no signup, legal acceptance, new credentials, provider calls or user/repository data transfer occurred. Conflicting context claims and undocumented quota scope/reset/counters remain unknown. LongCat's current official PAYG instructions require paid balance and its discretionary test credits do not prove recurring free access, so no LongCat adapter is enabled. This authorized implementation does not alter proposal votes, account admission, PR #1441, Gemini free paths, runtime routes or schedules.

Scoped independent code review (separate execution context; not a human ballot or GitHub formal review) identified one medium request-role validation edge case: list/dict roles could raise raw TypeError. Type-first validation and four malformed-role cases close it; huge numeric sampling values also produce fixed safe errors. The final 40 new protocol/discovery tests and complete 512-case provider pytest suite plus 9 legacy unittests pass locally. This is implementation evidence, not provider-account acceptance or live execution.

## MSM-024 — operational provider batch (executor evidence, not a ballot)

The owner's implementation direction supersedes MSM-023's offline-only development scope. Seven fixed-endpoint native transports are implemented together: Typhoon, UnoRouter, Routeway, Requesty, xKiro, xfyun Spark Lite and SEA-LION; five have documented catalog adapters. The FreeLLMAPI source now maps 23 existing service references to actual chat transports, with 47 still unmapped; its 72-reference denominator and the separate directory's 117 exact model claims are preserved. Existing Felo mappings/code are not duplicated or counted as additions. The compatible, completed Gemini exact-key free-smoke helper and its tests are folded into the same batch, default-off; PR #1441 and production Gemini routing are unchanged.

Synthetic tests exercise real hub dispatch, fixed HTTP URLs, strict text/response validation, admission denial, free-only model paths, malformed/overflow inputs and sanitized failures. A read-only local run successfully fetched the documented anonymous Routeway, Requesty and xKiro model catalogs. It sent zero inference requests and did not establish an account, balance, verified project, or production admission. Independent scoped code review found no additional severe issue; stale catalog-schema tests it identified were corrected. The full provider-contract suite and dual gates are required on the exact published head before promotion.

No signup, key creation, external acceptance, personal/user/repository inference payload, paid request/fallback or new inference schedule was performed. Existing Actions secrets are resolved only by trusted-master checks; missing credentials remain explicit blockers rather than fabricated operational completions. Gemini's account/project-read binding is unavailable and the helper is not executed. These are implementation and verification facts, not independent model ballots or governance consensus.

Local CI-equivalent provider parity passes 667 pytest cases and 9 legacy unit tests. Indexed repo-gate, termux-smoke and the 39-proposal registry validator pass. Public catalog checks returned success for Requesty, Routeway and xKiro with zero completion requests. Hosted checks must still be verified on the final PR head before promotion.
