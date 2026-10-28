# Provider audit — routed && wired (2026-10-28)

Owner order: audit that ALL providers are routed && wired.
Method: firsthand, on master `707d73c` (fresh clone) + live GitHub
API (PAT helper, names-only — no secret values anywhere in this
audit). Four legs per provider: **routed** (catalog endpoint +
orchestrator/router maps), **wired** (availability env + quota
family + quota-registry record), **provisioned** (the named secret
actually exists where the consumer runs), **guarded** (drift
automation green).

## Verdict

| Leg | Result |
|---|---|
| Routed + wired (code) | **PASS — 33/33** (27 llm + 6 review). `cadence_provider_onboarding.py check` = "33 providers fully onboarded, 7 recorded exceptions"; tests 8/8; rendered matrix on master is fresh (render = 0 diff) |
| Quota coverage | PASS — every llm provider carries a quota family + registry record(s); unmapped set = only the acknowledged `github` platform entry; g4f namespaced records (61) counted under the `g4f.vendors` aggregate by design |
| Review providers (6) | PASS — app/login surface (aikido, coderabbit, copilot, devin, qodo, sentry); no secrets involved |
| Guarded | PASS — `cadence-provider-onboarding.yml` last runs success (40750749123, 40708431982); `provider-availability.yml` success (40704824602) |
| **Provisioned (Actions)** | **FAIL for 8 llm providers** — finding F1 below |

## F1 — routed && wired in code, NOT provisioned in Actions

These providers' secret names are referenced by Actions workflows
(`provider-availability.yml`, `provider-batch.yml`; omni also by
`gemini-invoke.yml` / `gemini-after-peers.yml` /
`continuous-evaluation.yml`) but do **not** exist in the repo's
Actions secrets (58 names checked) nor in the sampled environment
secrets (`env_Termux-MonoRepo`, `Production`, `staging` = empty).
In Actions they receive empty credentials: availability reads
no-key and batch/invoke calls cannot run. If a key exists only
on-device, that is a device-only provider and the Actions legs
should say so explicitly; today they fail silently.

| Provider | Missing name(s) |
|---|---|
| cerebras | `CEREBRAS_API_KEY` |
| kilo | `KILO_API_KEY` |
| mistral | `MISTRAL_API_KEY` |
| modelscope | `MODELSCOPE_TOKEN` |
| omni | `OMNI_API_KEY` |
| ovhcloud | `OVHCLOUD_API_KEY` |
| requesty | `REQUESTY_API_KEY` |
| xfyun | `XFYUN_API_KEY`, `IFLYTEK_SPARK_API_PASSWORD` |

**Disposition:** owner provisioning item — provision the name in
repo Actions secrets, or record the provider as device-only in
`ops/cadence/provider-onboarding.json` so the Actions legs stop
pretending. Values are never handled in chat (names-only
discipline); this audit neither creates nor guesses any secret.

## Non-findings (checked, clean)

- huggingface: wired via provisioned alias `HUGGINGFACE_TOKEN`;
  the other alias names (`HF_TOKEN` etc.) being absent is fine —
  aliases are alternatives, not a set.
- typhoon: public/no-secret by recorded exception.
- cloudflare: both names provisioned (`CLOUDFLARE_API_TOKEN`,
  `CLOUDFLARE_ACCOUNT_ID` extra env).
- The other 17 llm providers: catalog secret provisioned under its
  canonical name.

## Tooling gap (recommendation)

The onboarding check derives surfaces from code only — it cannot
see provisioning, so F1-class drift is invisible to it. Extend
`cadence-provider-onboarding.yml` with a names-only cross-reference
of the derived secret names against the Actions secrets list
(readable in-workflow via the API with the workflow token), failing
loudly on a code-wired-but-unprovisioned name that carries no
device-only exception.
