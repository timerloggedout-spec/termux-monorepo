# Free-Tier Use Value Board

**Status:** initial public presentation and calculation contract. The session-value headline remains unavailable until validated public session rows exist.

## Goal

Estimate the paid API list-price equivalent of eligible no-cost repository engineering sessions, compare providers on identical token workloads, and keep time-investment opportunity cost separate from provider cost.

This is a SHE/Moneyball projection over repository-owned evidence, not a new source of truth, billing system, provider entitlement feed, or task-quality score.

## Current evidence state

- The provider-call contract in [HEX-MONEYBALL-INTEGRATION.md](HEX-MONEYBALL-INTEGRATION.md) defines provider/model, input/output token counts, cost, latency, and attempt linkage.
- The initial public data file contains a pricing snapshot and zero session rows. The public session feed is not yet wired to a validated export; this does not mean zero sessions or zero usage.
- A row contributes to paid-equivalent totals only when validation_status=VALIDATED, basksweep_status=PASS, publication_status=PUBLIC_SAFE, and outcome_status is SUCCESS or SUCCEEDED. The browser enforces an explicit public session-field allowlist and ignores price rows with missing, non-numeric, negative, or non-finite rates. A row contributes to verified free-tier value only when it additionally has billing_status=VERIFIED_NO_COST.
- Public exports must omit prompts, completions, tool payloads, credentials, private balances, and personal identifiers.

## Formula

paid_equivalent_usd = input_tokens × input_usd_per_million / 1,000,000 + output_tokens × output_usd_per_million / 1,000,000.

This is a counterfactual API list-price estimate, not cash spent or guaranteed savings. It excludes cached-token discounts, batch pricing, tools, search/grounding, taxes, subscriptions, negotiated rates, and non-token fees unless explicitly modeled.

Time opportunity cost is separate:

- time_invested_value = minutes_invested / 60 × chosen_hourly_rate
- potential_time_value = estimated_hours_saved × chosen_hourly_rate
- net_time_scenario = potential_time_value - time_invested_value

Time saved is a scenario input until established against a comparable baseline. Do not add it to provider cost or label it realized ROI.

## Price snapshot

The checked-in pricing examples are source-linked and dated 2026-10-23. Re-verify official rate cards before use. These are model/API-specific, not generic provider-wide rates:

- OpenAI API gpt-5.3-codex standard rate card: $1.75 input / $14 output per million tokens in this snapshot: https://developers.openai.com/api/docs/pricing
- Google Gemini API gemini-3.8-flash standard paid tier through 2026-12-31: https://ai.google.dev/gemini-api/docs/pricing
- Anthropic Claude API Claude Opus 4.8 global standard: https://platform.claude.com/docs/en/about-claude/pricing
- DeepSeek API DeepSeek-V4.1-Flash off-peak, cache-miss input: https://api-docs.deepseek.com/quick_start/pricing/

Price comparisons do not imply quality equivalence, free-tier availability, or that any listed model executed a repository session.

## Session row contract

Each public row is bounded metadata only: opaque session/run ID; workflow and source ref/SHA; observed UTC time; provider/model display labels plus a stable `canonical_model_id`; input/output tokens; elapsed seconds; outcome; evidence URL; validation status; Basksweep status; publication status; billing status; and pricing ID. Every pricing record must also declare a unique `canonical_model_id`. A session contributes only when its `canonical_model_id` exactly matches the canonical ID on the valid pricing record referenced by `pricing_id`; raw provider strings are not identity keys.

The upstream export/filter step must validate attribution, token fields, source identity, privacy, and Basksweep result. The browser is a projection and defensive filter, not a replacement for that validator. Unvalidated rows may be displayed only if they already passed the public-safety export gate; they never contribute to headline totals.

## Acceptance criteria

1. Missing session feed is labeled clearly and headline KPIs remain unavailable until at least one validated successful session exists; missing evidence is never rendered as zero realized savings.
2. Identical input/output token counts are used across all price rows.
3. Price sources, snapshot date, model identity, price basis, and assumptions are visible.
4. Human time and provider-equivalent costs are separate.
5. Headline totals include only validated, Basksweep-passing, public-safe rows.
6. No prompts, completions, tool payloads, credentials, private balances, or personal identifiers are published.
7. Existing quota and telemetry contracts remain authoritative; no poller, runtime admission rule, or scheduler is added.
8. Static deployment navigation and page are validated before promotion.
9. External evidence and pricing links are accepted only over HTTPS; unsafe or malformed URLs render as unavailable.
