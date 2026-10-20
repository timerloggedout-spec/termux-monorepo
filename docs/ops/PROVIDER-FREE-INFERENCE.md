# Existing credentials and no-cost inference

## What the current Actions inventory proves

[Trusted run 39431075928](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39431075928), on master `99acf512fbaf82d6a2d12924d547fa791200fac2`, successfully used the existing authorized operator credential to inspect repository Actions secret **names only**. The provider credentials relevant to this implementation are already mapped correctly:

| Stored Actions secret | Supported provider environment variable | Verified outcome |
|---|---|---|
| OPENROUTER_API_KEY | OPENROUTER_API_KEY | Resolved in Actions; official model catalog observed. Account entitlement and inference require separate checks. |
| GEMINI_API_KEY | GEMINI_API_KEY | Resolved in Actions; official model catalog observed. No account-specific no-cost entitlement established. |
| FELO_AI_API | FELO_AI_API | Resolved in Actions; model catalog observed. No account-specific no-cost entitlement established. |

No `GROQ_API_KEY` or supported Hugging Face alias appears in the current repository Actions inventory. This is not evidence about an unbound organization or environment secret. The supplied Groq Free account context does not create an API key. No key was created, copied out of Actions, renamed, rotated, or assigned to a different provider. Unrelated service and GitHub administration credentials are not inference-token substitutes.

The inventory now derives `provider_credentials` from the reviewed catalog credential registry. It reports canonical environment-variable names, recognized stored aliases, and either `missing_secret` or `configured_entitlement_unverified`. A stored name never establishes valid authentication, remaining quota, or free-account eligibility. Incomplete inventory reads never publish partial provider diagnosis.

## A deliberately bounded inference path

The manual `execute_free_smoke` input in the provider-batch workflow defaults to **false** and runs only from the trusted default branch after contract tests. It binds only `OPENROUTER_API_KEY` to the smoke step. The script checks live account metadata through `GET /api/v1/key`, accepts only literal `is_free_tier: true`, and discards all labels, balances, identifiers, and account responses. This is a conservative eligibility check, not a claim that accounts with purchased credits cannot use free models.

It then requires one unambiguous live catalog record for the exact allowlisted model `liquid/lfm-2.5-2.6b:free`, with explicit zero prompt/completion pricing and no nonzero or unrecognized pricing value. A `:free` suffix alone is insufficient. Only then may it send **one** synthetic completion request, with at most 16 output tokens, no tools/plugins, no streaming, no retry, no alternate model, `allow_fallbacks: false`, `require_parameters: true`, and maximum prompt/completion/request/image prices all zero. Failure or uncertain response stops execution. No paid fallback is available.

A successful receipt additionally requires the expected synthetic reply, matching model identity, and explicit zero usage cost. Only sanitized booleans, fixed reason codes, the public model ID, and request counts are persisted. Neither account metadata nor inference response bodies are artifacts. See [OpenRouter key metadata](https://openrouter.ai/docs/api-reference/limits) and [provider routing and maximum prices](https://openrouter.ai/docs/guides/routing/provider-selection).

This smoke is not production admission, a quota reservation, a free-capacity guarantee, accepted new terms, or permission for recurring inference. It does not write `LLM_API_HUB_PROVIDER_POLICY`, routing weights, provider keys, or account settings. Native production admission remains exact-model, current, public-data-only, and fail-closed.

## Scheduled health is not inference authorization

Previously, the continuity probe could POST to Gemini based solely on a token and discovered model, and its OpenRouter POST lacked explicit maximum-price and no-fallback controls. The continuity path is now **catalog-only**. Gemini no-cost entitlement is unverified, so no Gemini completion is sent. OpenRouter smoke is available only through the explicit guarded manual path above. Strict continuity checks now judge catalogs, not unapproved inference.

Historical `inference_ok` values are not upgraded into current no-cost evidence. New receipts distinguish credential configuration, live catalogs, verification blockers, attempted requests, and successful zero-cost inference.
