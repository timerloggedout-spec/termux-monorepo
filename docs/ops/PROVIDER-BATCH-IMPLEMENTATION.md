# Provider batch: native adapters, not directory-based activation

The native production catalog and local `llm_api_hub` now support **Groq, Mistral, and Gemini** through official APIs. The checked-in research snapshot contains **21 individual model claims** for those providers: 3 Groq, 7 Mistral, and 11 Gemini. Model IDs are matched exactly, including qualified IDs such as `openai/gpt-oss-120b`. This is an implemented adapter batch, not a claim that 21 models have been invoked or that every provider account is free.

The existing OpenRouter, Felo, Omni, and Hugging Face catalog defaults stay unchanged. Adding adapters does not expand existing continuous-evaluation cohorts, change model-router weights, or run the upstream proxy code.

## Official contracts

| Provider | Catalog API | Native hub route | Credential name | Primary reference |
|---|---|---|---|---|
| Groq | `https://api.groq.com/openai/v1/models` | `groq/<exact-model>` | `GROQ_API_KEY` | [Groq models](https://console.groq.com/docs/models) |
| Mistral | `https://api.mistral.ai/v1/models` | `mistral/<exact-model>` | `MISTRAL_API_KEY` | [Mistral model API](https://docs.mistral.ai/api/endpoint/models) |
| Gemini | `https://generativelanguage.googleapis.com/v1beta/models` | `gemini/<exact-model>` | `GEMINI_API_KEY`, alias `GOOGLE_API_KEY` | [Models and pagination](https://ai.google.dev/api/models), [OpenAI compatibility](https://ai.google.dev/gemini-api/docs/openai) |

Catalog requests are GET-only. Gemini uses its key in a header, never a URL, and follows page tokens only on its fixed API path. Authenticated requests reject redirects. Catalog metadata records context/output limits and available capability fields; missing prices remain unknown. A model-list response does not establish invocation health, accepted terms, account entitlement, remaining quota, or license suitability.

## Explicit account admission

New native inference routes are **disabled by default**, even when a key exists. An operator may point `LLM_API_HUB_PROVIDER_POLICY` at an external JSON policy after independently verifying the account, terms, model, and use case. The schema is `research-provider-admission/v1`; each entry requires an exact `provider` and `model`, literal `free_account_verified: true`, literal `terms_accepted: true`, `data_class: public`, and a future UTC `expires_at` ending in `Z`. Explicit paid/trial account status is rejected. No enabled policy is shipped in this change.

These policy fields are an operator assertion, **not machine verification of provider billing**. Do not assert them solely because a directory calls a service free or because an API key is present. If the provider cannot constrain an account to no-cost requests, leave it disabled. There is no paid fallback, provider/account hopping, automatic retry, or automatic production routing-weight change. New routes accept text-only messages; the caller remains responsible for supplying only public data. The hub cannot classify confidential prose by inspecting a string.

Policy is revalidated on each request, so revocation or expiry takes effect without a process restart. A denied native route must not fall through to OpenRouter. Error text excludes upstream bodies and credentials. The existing hub streaming shape remains the API contract; it does not imply native upstream token streaming.

## Every research claim gets a disposition

`provider_batch.py` reconciles **all 160 existing research candidates**, not just the implemented batch. It reuses pinned-source validation and explicit provider identity mappings. Supported identities are OpenRouter, Hugging Face, Groq, Mistral and Gemini. Felo and Omni remain native catalog sources but were not identities in the harvested snapshot.

The report distinguishes `observed_in_catalog`, `not_observed_in_catalog`, `catalog_unavailable`, `not_an_individual_model`, and `adapter_not_implemented`. Aggregate labels and static provider-class references never become invocable model IDs. Unimplemented provider families remain visible rather than being silently dropped or relabeled complete. Every report row retains `runtime_eligible: false`, null remaining quota, source provenance, and blocking reasons. An injected documented model-page record is not counted as a live model-list match.

```bash
python3 scripts/provider_model_catalog.py \
  --providers openrouter,felo,omni,huggingface,groq,mistral,gemini \
  --output /tmp/provider-batch/catalog.json
python3 -m scripts.model_selection_market.provider_batch \
  --catalog /tmp/provider-batch/catalog.json \
  --output /tmp/provider-batch/coverage.json
python3 -m pytest -q tests/test_provider_model_catalog.py \
  tests/test_provider_batch.py tests/test_research_provider_hub.py \
  tests/test_llm_api_hub_server.py tests/test_review_evidence.py
```

## Production validation without accidental activation

[Provider batch production contracts](../../.github/workflows/provider-batch.yml) runs real production entry-point regressions on relevant PRs and master pushes. Tests mock outbound network I/O, not admission or HTTP routing. They cover exact harvested identities, legacy hub compatibility, malformed/expired admission, pricing uncertainty, catalog transport, reconciliation, and review attribution.

A manual dispatch from the default branch additionally checks out trusted default-branch code, reads the seven named catalog credentials from Actions secrets, and stores catalog, coverage, and matrix-review observations in a run-attempt artifact. There is **no new schedule**, no inference step, and no write authority. PR runs receive no provider credentials. The read-only GitHub job token is scoped to the separate review-evidence step, not provider requests. Missing credentials and failed catalogs remain explicit evidence; a successful workflow does not mean every provider passed.

Actions secret values cannot be read back through GitHub's secret API. The session's secret-name listing still returns HTTP 403; that is distinct from the anonymous commit-metadata error fixed by #1298. The workflow can test configured names in place without extracting values, granting permissions, or confusing GitHub PATs with inference credentials.

The fresh production [research run 39377722728](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39377722728) passed contracts, collection, and publication on master `2b559f48fa14ee466baf2242355ca9e1f1950a78`. Its downloaded artifact contains two pinned sources, 160 research candidates, and 185 aggregate records. This verifies #1298's metadata authentication recovery; it does not verify free inference or deploy a hub server.

Review artifacts identify PR-history counts, not current-head approvals. Each formal review retains its commit ID. The production collector records UTC collection start and a separate normalization time, verifies an unchanged head before/after pagination, and requires that head in the collected commit list. This detects head drift without pretending independently retrieved API pages are an atomic event snapshot.

## Completion slice: MSM-012 / MSM-013 / MSM-014

Native exact-model admission now also covers **Hugging Face, Cerebras and NVIDIA**, using fixed official chat URLs: `https://router.huggingface.co/v1/chat/completions`, `https://api.cerebras.ai/v1/chat/completions`, and `https://integrate.api.nvidia.com/v1/chat/completions`. Cerebras and NVIDIA have matching native `/v1/models` adapters. Credentials are `CEREBRAS_API_KEY` and `NVIDIA_API_KEY` (alias `NVIDIA_NIM_API_KEY`); HF retains its four existing aliases. None is enabled merely by possessing a key.

Official references: [HF inference providers](https://huggingface.co/docs/inference-providers/en/index), [HF current pricing](https://huggingface.co/docs/inference-providers/en/pricing), [Cerebras compatibility](https://inference-docs.cerebras.ai/resources/openai), [Cerebras models](https://inference-docs.cerebras.ai/models/overview), [NVIDIA hosted APIs](https://docs.api.nvidia.com/nim/reference/llm-apis), and [NVIDIA catalog](https://integrate.api.nvidia.com/v1/models). NVIDIA's hosted API is distinct from downloadable NIM containers. Documentation establishes transport contracts, not this project's account entitlement.

### How many are implemented?

The pinned snapshot contains **160 research records**, not 160 invocable models:

| Source | Records | Exact model claims | Static/aggregate references | Exact claims covered by chat transports |
|---|---:|---:|---:|---:|
| `mnfst/awesome-free-llm-apis` | 123 | 117 | 6 | 48: 32 explicitly gated native + 16 legacy OpenRouter |
| `tashfeenahmed/freellmapi` | 37 | 0 | 37 provider-class references | 0 exact claims extracted by this parser |

The 32 gated claims comprise 3 Groq, 7 Mistral, 11 Gemini, 5 HF and 6 NVIDIA. This adds 11 exact claims over the earlier batch. Cerebras is implemented but has no exact claim in the pinned snapshot, so does not inflate the count. Six of the directory's 16 provider families have transport coverage. The second source's 37 references do **not** describe its complete upstream model inventory; upstream headline endpoint counts are not the implementation denominator. All records retain dispositions and zero automatic runtime admissions. `summary.by_source` exposes these denominators and labels legacy OpenRouter separately.

### Credential discovery and remaining decisions

The manual default-branch workflow now attempts **names-only** inventory with existing issue-184-authorized administration credentials, isolated from catalogs and read-only review collection. The fixed GitHub metadata endpoint cannot retrieve secret values. Missing authorization, 403 and bounded-pagination failures remain explicit observations. PR runs receive no credentials; no new schedule, permission grant or routing activation is created. The earlier description of a wholly read-only observation job applies to catalog/review calls: the new inventory step uses an existing administrative credential strictly for a metadata GET.

Availability monitoring is separately repaired for HF alias parity and Gemini header authentication; its existing health lane is not admission evidence for new providers. See the [Delphi/RFP matrix](../proposals/active/free-llm-provider-prioritization/DEBATE.md) for proposed priorities and uncast ballots, and the [HITL checklist](PROVIDER-HITL.md) for signup contact/verification, exact-model entitlement and Origin-device access. `DeepAgent.py --doctor` reports local readiness; a local doctor or Administrator title does not prove a remotely running administrator.
