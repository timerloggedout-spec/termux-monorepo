# DEBATE — free-llm-provider-prioritization

**Purpose:** Research/RFP feedback prioritization voting matrix for the free-LLM-provider follow-through. This is a proposal for human prioritization, not a record of votes, consensus, provider approval, or runtime authorization. `docs/proposals/Docs Proposals Delphi Oracle Method Debate.md` was not present in the checkout; this document applies the clarified intent within the repository's existing `DEBATE.md` convention.

## Proposal: prioritize evidence closure before provider expansion

Use a Delphi-style, independent human ranking to decide the next scoped work items. Do not treat model counts, directory rankings, agent recommendations, or existing adapters as votes. The ordering below is the **driver's proposed starting order**, subject to human ballots; it is not consensus. Priorities apply to work sequencing only, not provider eligibility.

| Proposed rank | Work item | Evidence / rationale | Proposed disposition and exit evidence |
|---|---|---|---|
| 1 | **Close account and terms admission gaps (HITL)** | [Research brief](../../../ops/FREE-LLM-PROVIDER-RECON.md#free-tier-claims-versus-availability) says catalog labels and public limits do not prove account entitlement; [batch policy](../../../ops/PROVIDER-BATCH-IMPLEMENTATION.md#explicit-account-admission) requires explicit exact-model, account, terms, public-data, and expiry admission. | Operator verifies account identity, no-cost status, terms, data policy, and model eligibility through provider's own account surface. Keep routes disabled if any item is unknown; retain evidence without secrets. |
| 2 | **Observe Hugging Face credential-name parity in production** | All four authorized aliases are now wired consistently across batch, catalog, native chat, and availability paths with offline regressions. [Issue #184](https://github.com/timerloggedout-spec/termux-monorepo/issues/184) records historical canonical `HF_TOKEN`; naming support alone is not proof of a configured secret. | Use the trusted names-only inventory and catalog observation. Never read or print values; missing authorization means unavailable evidence, not proof that the provider or account is absent. |
| 3 | **Close provider-family evidence gaps after direct transport completion** | The [latest coverage](../../../ops/PROVIDER-BATCH-IMPLEMENTATION.md#full-direct-transport-completion) separates 117 exact model claims, 6 aggregates and 37 static provider references. All 117 have chat transport coverage (101 gated native, 16 legacy OpenRouter); catalog contracts cover 13/16 families. No automatic admissions are asserted. | Preserve exact identities and prove actual account/model availability. Z.ai, ModelScope and OVHcloud catalog contracts remain unverified. Cerebras has no exact pinned claim; static class references and code coverage are not invoked models. |
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

## Open questions

1. Following alias-code parity, which account/terms and production-observation gap should be resolved first?
2. Which provider/model, if any, can an authorized account holder establish as genuinely no-cost and eligible for the intended public-data use?
3. Who is the named human registrar for collecting and publishing independent ballots?

## Scope and guardrails

- This file proposes research/RFP feedback priorities only. It does not amend routing policy, model weights, catalog eligibility, account policy, or deployment authority.
- All implemented adapters are distinct from evidence of invoked models or free accounts. Existing OpenRouter/Felo/Omni routing weights remain unchanged; the user's authorized code work does not supply missing account-entitlement evidence.
- Do not enter API keys, secret values, personal data, or unredacted account screenshots in ballots or repository files.
- No consensus is claimed. Binding outcomes must be recorded through the proposal process and attributable votes; see [PROCESS](../../PROCESS.md) and [consensus tiers](../../CONSENSUS.md).
