# Typhoon: free API, offline adapter, legal hold

Typhoon's official hosted API is documented as **free to use**, not as purchased credits or a time-limited trial. This change implements a distinct, synthetic-fixture-tested **offline text protocol adapter**. It does **not** enable an HTTP transport, route, account, quota manager or live inference. No signup or binding terms were accepted.

## What is actually free

The [official overview](https://docs.opentyphoon.ai/en/) calls the Typhoon-hosted API a “Free Tier” with “Zero cost for light usage.” The [FAQ](https://docs.opentyphoon.ai/en/faq/) answers its cost question: “The Typhoon API is a research showcase and free to use.” Together these establish a public **$0 light-usage offer**, rather than a trial-credit or paid-top-up offer. They do not establish this user's account eligibility, continued availability, unlimited usage or a spending guarantee for an uninspected account.

The same overview separately labels **Typhoon API Pro via Together.ai** as pay-as-you-go. That partner service, OpenRouter, local model hosting, OCR and ASR are not this adapter's endpoint or entitlement. No paid fallback is provided.

## Account and legal boundary

The [quickstart](https://docs.opentyphoon.ai/en/quickstart/) and [authentication guide](https://docs.opentyphoon.ai/en/authentication/) require a registered, signed-in Playground account and a newly generated API key. The key is displayed only once. The public [API-key sign-in page](https://playground.opentyphoon.ai/api-key) states that logging in agrees to the API Terms and Conditions and links the SCB DataX privacy notice. We stopped before login/signup. The inspected public instructions do not establish a payment-card requirement, identity/phone-verification procedure, country eligibility or actual account-specific entitlement; absence of such instructions is not account verification.

The [current API terms](https://opentyphoon.ai/tac) are materially more restrictive than a generic “free API” label:

- **Section 2:** inputs must not contain personal or sensitive personal data. Outputs require human review before use, publication or reliance. Under-15 users require guardian consent/supervision.
- **Section 2:** bans using services/outputs to train or improve AI models/datasets and competitive benchmarking/model extraction without express written consent. It also restricts services similar to the provider's, third-party account use without written permission, and includes broad bot/crawler language. Compatibility of this repository's agentic/multi-user/evaluation use needs review or provider clarification; an official API example is not a waiver.
- **Section 4:** grants a perpetual royalty-free right to use inputs, including for developing/training the provider's models; outputs/content may also improve services. This is not a no-training service.
- **Sections 5–6:** token/rights assignment needs written consent; terms/features may change, and continued use accepts revised terms. **Section 14:** Thai law and Thai courts govern.

The [FAQ](https://docs.opentyphoon.ai/en/faq/) acknowledges usage-data collection for model/API improvement and says data will never be shared with third parties. The broader [Privacy Notice](https://opentyphoon.ai/privacy), version July 2026, nevertheless permits specified disclosures to affiliates, partners, service providers and authorities (section 5), international transfers (section 6), and retention as appropriate/necessary or legally required (section 7). It gives no API-specific fixed retention duration or verified training opt-out. Do not repeat the FAQ's assurance as a blanket contractual no-sharing guarantee.

**Hold:** legal/data-use review and explicit authority for any future terms acceptance are required before account setup or live use. No repository/user data was sent to Typhoon. A key's existence or an ordinary public-data admission flag would not resolve these restrictions.

## Exact text API contract

The [API reference](https://docs.opentyphoon.ai/en/api-reference/) specifies:

| Item | Official contract / implementation boundary |
|---|---|
| Host and method | `POST https://api.opentyphoon.ai/v1/chat/completions` |
| Authentication | `Authorization: Bearer <API_KEY>`; `Content-Type: application/json`. No credential is read or serialized by the offline adapter. |
| Configuration name | Authentication-guide examples use `OPENTYPHOON_API_KEY`; this is a name-only reference, not a provisioned secret. |
| Models | `typhoon-v2.5-30b-a3b-instruct`, `typhoon-v2.1-12b-instruct`, both listed on the official overview/rate-limit pages. No aliases to Gemini/Groq/OpenRouter. |
| Required JSON | Exact `model`; `messages` array of text `{role, content}`, with `system`, `user` or `assistant` role. |
| Documented options | `max_tokens`, `temperature`, `top_p`, `n`, `stream`, `stop`, `presence_penalty`, `frequency_penalty`, `repetition_penalty`, `user`. The implementation supports a deliberately narrower nonstreaming text subset; unsupported fields are rejected rather than silently forwarded. |
| Response | OpenAI-shaped `choices[].message` and `usage` with prompt/completion/total tokens; synthetic fixtures exercise parsing and safe errors. |
| Errors | Documented 400/401/403/404/429/500 and nested `error` object. Unknown/raw upstream text is not a public diagnostic. |
| Streaming | Official SSE support exists, but this offline slice does not implement it. |
| Model catalog | No verified list-models contract in the inspected reference. No guessed `/models` endpoint, catalog probe or fabricated catalog rows. |

**Conflicting context claims stay unresolved.** The overview lists 128K and 56K context windows, but the API reference describes 8192 shared prompt/completion tokens and the [tokens page](https://docs.opentyphoon.ai/en/tokens/) says 8K for all models. We do not select a convenient value, advertise an established output cap, or create capabilities/admission from these contradictory pages.

## Rate limits are not balances or resets

The [official rate-limit page](https://docs.opentyphoon.ai/en/rate-limits/) lists **5 requests/second and 200 requests/minute for each of the two text models**. Requests, including streaming requests, count against these limits; excess returns HTTP 429. Its example error contains `Rate limit exceeded. Please retry after 2024-01-01T12:00:00Z`.

These are documented public request ceilings, not a measured remaining allowance. The page does not establish account/key/project scope, fixed versus rolling windows, a daily/monthly free token allowance, reset timezone, remaining/reset response headers, a balance endpoint or account-specific counters. A timestamp extracted from the documented error pattern is only a **retry hint**; it is not a guaranteed quota reset. No quota-service registration or new poller is added, and unknown fields remain null/unknown. No OCR/ASR limits are imported into the text adapter.

## What the code and dashboard actually ship

- `llm_api_hub/server/typhoon_protocol.py`: pure request/response/error transformations and public documentation contract; no HTTP/environment/credential access.
- `tests/test_typhoon_protocol.py` and `tests/fixtures/typhoon/`: synthetic fixtures, never live receipts.
- `scripts/model_selection_market/provider_batch.py`: source-scoped linkage from the **existing** pinned FreeLLMAPI Typhoon reference to `offline_protocol_legal_hold`. It does not add a model claim, native transport or account admission. The other 53 unmapped service references remain gaps, not inferred integrations.
- The existing dashboard has a separate held-discovery link, outside quota-service/live-manager counts. The resource matrix links here; existing research provenance is preserved rather than rewritten with first-party claims.

The 72 static FreeLLMAPI references now have 16 existing chat families, one fixed public-research service, one custom placeholder, one held Typhoon protocol implementation and 53 still-unmapped leads. The **117 exact pinned model claims and 16 mapped chat-family counts are unchanged**. Active transport/catalog/quota registries, routes, PR #1441, Gemini free-path code and schedules are untouched. Passing fixtures establishes protocol code, not a usable free account or a successful inference.

## LongCat: do not integrate as free

The [official LongCat model pricing](https://longcat.chat/platform/docs/pricing/longcat-2.5) lists token-metered LongCat-2.5-Preview rates: $0.30/million uncached input tokens, $0.006/million cached input tokens and $1.20/million output tokens, described as limited-time pricing. [Pay-As-You-Go setup](https://longcat.chat/platform/docs/api-pay-as-you-go) explicitly requires a balance top-up and says requests are rejected when balance is zero or below. [Token packs](https://longcat.chat/platform/docs/token-pack) are purchased and expire after 30 days.

The [API platform terms](https://longcat.chat/platform/private/) allow discretionary free test credits/vouchers but do not promise a current or recurring free API quota. The PAYG page says account verification precedes top-up while the [FAQ](https://longcat.chat/platform/docs/faq) says real-name verification is unnecessary for recharge/use: that prerequisite remains contradictory. No numeric API free quota/reset is established. Monthly enterprise paid-consumption discount resets are not free allowance resets.

The [chat contract](https://longcat.chat/platform/docs/api/chat) is bearer-auth `POST https://api.longcat.chat/openai/v1/chat/completions` with `model` and `messages`; the [model-list contract](https://longcat.chat/platform/docs/api/models) specifies authenticated `/openai/v1/models`. These documented endpoints do not prove free entitlement or a live inventory. Its [API privacy policy](https://longcat.chat/platform/private/policy) covers account/payment and model/token/API-key usage data. **No LongCat adapter is enabled or claimed shipped**: the verified public setup is paid, and any usable $0 exception is unproven. No account, top-up, trial credit, API request or legal acceptance was attempted.
