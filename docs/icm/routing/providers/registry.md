# Provider Evidence Registry

## Purpose

This registry is a **routing-governance index**, not a provider configuration file. It helps an editor trace current provider strategy to the authoritative configuration, existing GitHub work, and unresolved review items without copying executable rules into ICM documentation.

| Record | Canonical configuration or governance source | Current ICM interpretation | Runtime change in this PR |
|---|---|---|---|
| `omni` | [`.github/connectors/llm-peers.yaml`](../../../../.github/connectors/llm-peers.yaml); [Issue #94](https://github.com/timerloggedout-spec/termux-monorepo/issues/94) | Existing peer record; Issue #94 treats provider fallback and success matrices as unresolved strategy work. | None |
| `openrouter` | [`.github/connectors/llm-peers.yaml`](../../../../.github/connectors/llm-peers.yaml); [PR #97](https://github.com/timerloggedout-spec/termux-monorepo/pull/97); [Issue #94](https://github.com/timerloggedout-spec/termux-monorepo/issues/94) | Existing peer record with a merged free-tier fallback integration history; future performance observations require separate approval. | None |
| `gemini` | [`.github/connectors/llm-peers.yaml`](../../../../.github/connectors/llm-peers.yaml); [PR #123](https://github.com/timerloggedout-spec/termux-monorepo/pull/123) | Existing peer record; the merged dynamic-routing history is evidence, not a replacement runtime authority. | None |
| Cross-provider strategy | [PR #123](https://github.com/timerloggedout-spec/termux-monorepo/pull/123); [Issue #94](https://github.com/timerloggedout-spec/termux-monorepo/issues/94) | Preserve the distinction between dynamic-routing history, current runtime sources, and future reviewed observations. | None |

## Observation eligibility

A provider may receive a new observation record only after all fields below are declared in the proposal or a dedicated routing decision record.

| Required declaration | Why it is needed |
|---|---|
| Source URL or provider API operation | Prevents ambiguous or invented provider evidence. |
| Exact fields permitted for collection | Supports minimization and avoids accidental secret or prompt capture. |
| Cadence and trigger | Distinguishes a manual review from scheduled or persistent polling. |
| Credentials model | Ensures that credentials are held outside documentation and never copied into card files. |
| Failure and quota behavior | Prevents a failed observer from silently changing runtime routing. |
| Retention and redaction rule | Keeps observations reviewable without storing sensitive payloads. |
| Human reviewer | Establishes who accepts or rejects a candidate observation. |

## Related implementation boundaries

The repository’s current provider configuration and workflow behavior are intentionally not modified until the post-ICM code/workflow phase. The evidence archive at [`../../_meta/master-rebuild-integration-evidence.md`](../../_meta/master-rebuild-integration-evidence.md) preserves prior workflow alternatives for later scoped review.
