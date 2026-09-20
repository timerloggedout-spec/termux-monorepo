# Free quota windows (entitlements)

This file is **operational metadata**, not routing policy.
The live provider catalog (`scripts/provider_model_catalog.py`) remains authoritative for model IDs and observed pricing.
Public plan pages describe *entitlements*; they do **not** prove remaining account balance.

Last ops stamp: 2026-09-20 11:14 PDT (session on master `502583d2`).

## Cadence classes

| Cadence | Meaning | How agents must treat it |
|---------|---------|--------------------------|
| hourly | rolling or clock-hour cap | skip lane when live headers show remaining=0 or 429/402 |
| daily | calendar or rolling 24h credits | do not assume reset time; observe `retry-after` / credit headers |
| weekly | rolling 7d or week-boundary | same; never invent remaining |
| monthly | calendar month or 30d | same |
| trial | time-boxed $0 route | poll catalog until route leaves `free_zero_price` / `free_trial` |
| catalog | live `$0` / `:free` / `free_zero_price` listing | re-poll; listings change; never cache remaining |

FELO is one provider among peers. Every cadence class above is a first-class free route **when** live evidence classifies it as free/zero/trial/catalog.

## Documented public entitlements (revalidate before spend)

| Provider | Route / plan | Cadence | Public claim | Remaining-balance source |
|----------|--------------|---------|--------------|--------------------------|
| Felo | Search API Free Standard | daily | 200 daily free credits (public harness docs) | authenticated API / headers only |
| Felo | `ox-alpha` LLM | trial | documented free-trial model page | catalog + invocation outcome |
| OpenRouter | `:free` suffix models | catalog | $0 listed price | `/v1/models` pricing |
| OpenRouter | `stealth/ox-alpha` | trial | historically $0/M; watch deadline 2026-08-24 was **observe-until-change** | live catalog |
| Hugging Face | router free/zero models | catalog | only when poll classifies free | one of the configured Hugging Face secret names + router `/v1/models` |
| OmniRoute | catalog $0 | catalog | only when poll classifies free | `OMNI_API_KEY` + `/v1/models` |
| Gemini | soft budgets | hourly/daily | rotation YAML + quota-gate | `gemini-quota-gate` skip vs proceed |
| GitHub Actions | public repo minutes | monthly | platform entitlement | Actions usage API; not a model route |

Do **not** hardcode remaining credits. Do **not** substitute a paid model when a free lane is empty.

## Required telemetry (every poll / invoke)

- `observed_at` (UTC)
- provider + model id
- `pricing_classification` + `access_classification`
- cadence (`hourly`/`daily`/`weekly`/`monthly`/`trial`/`catalog`/`unknown`)
- safe response headers: `x-ratelimit-*`, `x-credit-*`, `x-quota-*`, `x-remaining-*`, `x-usage-*`, `retry-after`
- HTTP status + error class
- never persist credentials

## Router rule

Eligible automatic lanes = union of:

1. `pricing_classification == free_zero_price`
2. `id` ends with `:free`
3. `access_classification == free_trial`
4. documented cadence entitlement **and** live headers do not contradict

Paid / unknown requires an explicit experiment label.

See also: `docs/ops/PROVIDER-PROMOTION-WATCH.md`, `docs/ops/AGENT-TEAM-ORCHESTRATION.md`, issues #175 #337 #184.
