# Cadence Provider Onboarding — one registry, every surface checked

Implements: QAC-005 (`docs/proposals/active/quota-aware-cadence-rfp/ITEMS.md`)

## Problem (verified on master, 2026-10-28)

Cadence did **not** auto-adjust for new providers. A provider only joined
the cadence system after hand-editing up to five independent surfaces, and
nothing verified the surfaces agreed:

| Surface | Home |
|---|---|
| Catalog endpoint | `scripts/provider_model_catalog.py` `ENDPOINTS`, or `provider_extension_catalogs.py`, or `provider_catalog_protocols.py` |
| Catalog secret (names only) | the same modules' `SECRETS` / `SECRET_ALIASES` |
| Availability wiring | `.github/workflows/provider-availability.yml` job env |
| Quota family | `ops/quota/provider-managers.json` |
| Review-bot maps | `.github/workflows/peer-review-orchestrator.yml` `providerLogins` / `providerCheckApps` |

Within a registered provider, cadence *timing* is already adaptive
(quota-dispatch-tree G1 re-derives its staleness threshold as 1.5× the
median gap of the last 5 availability runs, clamped 120–720 min; the
peer-review orchestrator applies per-SHA gating, bot-author exemptions,
reviewer-metrics JIT exemptions, and CodeRabbit cooldown parsing).
Discovery/onboarding was the manual part.

## Mechanism

- **Registry (SSOT):** `ops/cadence/provider-onboarding.json`
  (`cadence-provider-onboarding/v1`) — one entry per provider:
  `{provider, kind: llm|review, availability_extra_env?, exceptions?}`.
- **Check:** `scripts/cadence_provider_onboarding.py check` derives the
  actual surface matrix from the live modules/workflows and fails when a
  provider is on a surface without a registry entry, an expected surface
  is missing without a recorded exception, an exception is stale, or an
  availability secret name is claimed by no entry. Wired into the test
  suite (`tests/test_provider_onboarding.py`), so drift fails CI.
- **Render:** `scripts/cadence_provider_onboarding.py render` regenerates
  `docs/ops/generated/cadence-provider-onboarding.json` (the derived
  matrix; the check in tests keeps the registry honest, render keeps the
  published matrix current).
- **Scaffold:** `scripts/cadence_provider_onboarding.py scaffold <id>
  --kind llm --endpoint <url>` (or `--kind review --bot-login <login>`)
  prints the complete onboarding patch for every surface from one
  invocation. The registry entry it prints lands in the same PR as the
  surface edits — that is the whole onboarding procedure.

## Current state (2026-10-28, derived, not hand-counted)

33 providers fully onboarded: 27 `llm`, 6 `review`; 6 llm families carry
an `implemented_passive_adapter` quota manager (groq, huggingface,
ollama, openrouter, sambanova, siliconflow) — the other families are
documentation-only or unsupported in `provider-managers.json`, which the
generated matrix shows per provider. 7 exceptions are recorded, all
real asymmetries verified against the live surfaces:

- `typhoon` — quota-family record only (no catalog/secret/availability).
- `xfyun` — availability wired under vendor iFlytek env names
  (`XFYUN_API_KEY`, `IFLYTEK_SPARK_API_PASSWORD`); no catalog module entry.
- `zai` — secret-only: `ZAI_API_KEY` wired, no catalog endpoint registered.
- `xkiro` — public catalog; availability probe needs no secret env.

## Rules

- Secret **names only**, never values (fleet credential rule, issue #184).
- A public catalog listing never grants admission/routing by itself —
  unchanged from the catalog modules' existing contract.
- Adding an exception requires a reason that names the verified
  asymmetry; a stale exception fails the check, so exceptions retire
  themselves when the surface lands.
