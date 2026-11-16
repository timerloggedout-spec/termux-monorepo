# Typhoon: callable text API adapter

Typhoon is registered in the native hub transport registry. The former offline-only development disposition is superseded by MSM-024. Development is not blocked by this document; account enrollment, key creation and new external acceptance are separate actions and were not performed.

## Implemented interface

The [official API reference](https://docs.opentyphoon.ai/en/api-reference/) specifies bearer-authenticated `POST https://api.opentyphoon.ai/v1/chat/completions`. `llm_api_hub/server/provider_extensions.py` fixes that destination, resolving `OPENTYPHOON_API_KEY` or `TYPHOON_API_KEY` without per-request endpoint overrides. The hub model IDs are `typhoon/typhoon-v2.5-30b-a3b-instruct` and `typhoon/typhoon-v2.1-12b-instruct` when exactly admitted.

`research_providers.complete()` authorizes the exact model, then uses the pure `typhoon_protocol.build_chat_request()` and strict response normalizer over the bounded HTTP transport. Only nonstreaming text is forwarded upstream. The hub can render its existing buffered SSE envelope; that is not provider-native streaming. Tool calls, images, unknown fields and the optional upstream `user` identifier are rejected. Redirects are refused; failures are sanitized and never retried through another or paid provider.

No `/models` API is invented. Model discovery uses the existing pinned service reference and exact runtime admission, not fabricated catalog rows. Context-window pages disagree, so the adapter does not advertise a verified context/output cap based on a convenient interpretation.

## Runtime readiness

The existing native-provider policy must name the exact model, verify a free account and applicable authorization, specify `data_class: public`, and remain unexpired. A configured key alone neither grants admission nor proves remaining quota. This batch does not generate or modify production admission files.

```bash
python3 scripts/ops/provider_operational_check.py
python3 -m pytest -q tests/test_typhoon_protocol.py tests/test_provider_extensions.py tests/test_typhoon_discovery.py
```

The readiness command sends no inference. Its optional `--catalogs` mode reads only verified model catalogs; Typhoon has none documented and is not contacted by that mode. The master-only manual `provider-batch.yml` readiness job can resolve existing Actions keys without exposing their values.

## Public data and no-cost boundary

The [official overview](https://docs.opentyphoon.ai/en/) and [FAQ](https://docs.opentyphoon.ai/en/faq/) describe free light research usage. This is separate from paid Typhoon Pro via Together.ai, which is not a fallback. The [terms](https://opentyphoon.ai/tac) prohibit personal/sensitive-data input and permit provider use of inputs. Do not send personal, private, user or repository content in verification; no such content or inference request was sent by this batch. No account, signup, key creation or new terms acceptance was attempted.

The [published rate limits](https://docs.opentyphoon.ai/en/rate-limits/) are request ceilings, not a remaining account balance or a guaranteed reset. No quota-service manager or new inference schedule is added. Passing fixtures establishes working transport code, not a successful live completion or usable account.
