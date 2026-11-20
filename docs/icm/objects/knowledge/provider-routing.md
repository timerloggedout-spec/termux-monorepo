# Provider Routing Governance

| Field | Value |
|---|---|
| Type | object |
| Cluster | knowledge |
| Universe | live |
| Status | initiated |
| Entity | A repository-native documentation resource for provider-routing evidence, observations, and deferred execution review |

## What this is

This card governs how ICM describes evolving LLM-provider routing without becoming a second router. The nested [`../../routing.md`](../../routing.md) resource links current configuration, workflow history, and reviewed provider observations. It recognizes OpenRouter, Omni, and Gemini as evidence records only where the existing repository configuration already identifies them.

The operative runtime remains outside this card: machine-readable provider configuration, Actions workflows, secrets, and invocation code have their own owners. This ICM work does not modify them.

## Routing rule

Read [`../../routing/CONTEXT.md`](../../routing/CONTEXT.md), then the smallest relevant provider registry or observation record. Use [`../../_meta/master-rebuild-integration-evidence.md`](../../_meta/master-rebuild-integration-evidence.md) when reviewing inherited workflow alternatives. Stop before any code or workflow path unless a separate post-ICM proposal authorizes that work.

## First-order impact

**Hits:** routing documentation, provider evidence references, CCTV status cards, and future human review of provider observations.
**Does not hit:** provider API calls, secrets, schedules, GitHub Actions, routing code, model selection, budgets, device access, or deployment automatically.

## Evidence

[1] [`../../../../.github/connectors/llm-peers.yaml`](../../../../.github/connectors/llm-peers.yaml) is the repository’s current machine-readable provider inventory.
[2] [PR #97](https://github.com/timerloggedout-spec/termux-monorepo/pull/97) and [PR #123](https://github.com/timerloggedout-spec/termux-monorepo/pull/123) preserve merged provider-routing history.
[3] [Issue #94](https://github.com/timerloggedout-spec/termux-monorepo/issues/94) records unresolved fallback, success-matrix, and governance work.
