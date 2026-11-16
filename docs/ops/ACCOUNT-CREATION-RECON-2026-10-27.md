# Account-Creation Recon — Classifier/Provider Phantom Subset — 2026-10-27

**Lane:** [MUSEai]@{role:{account-creation}} — account creation + API-key harvest/provisioning,
split from the Tier 1 Classifiers steward lane on the owner's order (2026-10-27).
**Scope:** the classifier/provider subset of `docs/ops/PHANTOM-SECRET-REMEDIATION.md`.
**Method (all counts live-derived at recon time, 2026-10-27 ~15:00 PDT):**

- Live Actions secret store via the PAT helper: **41 names**. Names only — no secret
  value was read, recorded, or transmitted anywhere in this recon.
- Fleet Gmail evidence, two passes: `from:` searches per provider domain, plus the
  Google sign-in sharing notices ("You shared some Google Account data with …"),
  which are the strongest mailbox proof that a Google-route account/sign-in happened.
- Repo code at master `ed733b9`: `scripts/provider_model_catalog.py` (SECRETS map +
  SECRET_ALIASES), `scripts/provider_catalog_protocols.py`,
  `scripts/provider_extension_catalogs.py`, `.github/workflows/provider-batch.yml`,
  `.github/workflows/provision-secrets.yml`, `.github/workflows/remote-gamut-evaluation.yml`.
- Public signup / free-tier terms per provider (provider docs first, directories second;
  conflicts are flagged, never silently resolved).

## Corrections to the starting brief (firsthand, this recon)

1. **GROQ_API_KEY is DONE, not phantom.** It is present in the live 41-name store
   (harvested earlier on 2026-10-27; availability run 40512185380 verified).
   The assignment list and the current phantom doc (generated 2026-10-27T13:12Z,
   before the harvests) both still list it — the doc is stale on Groq and on
   HUGGINGFACE_TOKEN for the same reason. The live store wins.
2. **SambaNova and Cohere accounts EXIST — they were "never started" in the brief.**
   Google sign-in sharing notices, 2026-10-20 (the Oct 20–24 sweep):
   SambaNova 22:57 PDT, cohere.com 22:53 PDT, NVIDIA 22:53 PDT, Groq 22:53 PDT.
   Same failure shape as the earlier Groq correction: no provider-domain mail
   ≠ no account, because these accounts were created via Sign in with Google.
3. **Remaining never-started on current evidence: Cerebras, SiliconFlow, and
   OmniRoute-as-an-external-account** (no provider mail, no Google-share notice).
   OmniRoute resolves differently — see the Omni family row.

**Subset after correction:** the brief's 31 names + ZAI_API_KEY = 32 names;
minus GROQ_API_KEY (done) = **31 phantom names across ~24 provider families**
(several names are one family: NVIDIA×2, Typhoon×2, iFlytek×2, Omni×3,
OpenAI/Codex/Gamut-judge×3).

## Per-provider table

Account evidence key: **EXISTS** = mailbox-proven · **NOT ESTABLISHED** = some mail
trace but no API-account proof · **NONE** = no mailbox trace in 2026 on current evidence.
Card column is the fleet CARD RULE verdict: `card-gated` = hard stop, do not start.

### Batch H — account exists, harvest the key first (no new signup)

| Secret name(s) | Provider | Account evidence | Free / card state | Next action |
|---|---|---|---|---|
| `COHERE_API_KEY` | Cohere | **EXISTS** — Google sign-in 2026-10-20 22:53 | Trial key is auto-created at signup; 1,000 calls/mo, eval-only; no card | Sign in (Google route), copy the trial key, provision, verify |
| `SAMBANOVA_API_KEY` | SambaNova Cloud | **EXISTS** — Google sign-in 2026-10-20 22:57 (corrects the brief) | Free Tier applies *while no payment method is linked* (20 RPM / 20 req/day / 200K tok/day per model); no card | Sign in (Google route), create key, provision, verify. Do **not** link a payment method |
| `NVIDIA_API_KEY`, `NVIDIA_NIM_API_KEY` | NVIDIA (build.nvidia.com / NIM) | **EXISTS** — NVIDIA account created 2021-06-08 (account mail) + Google sign-in 2026-10-20 22:53 | Developer Program members get free NIM API access for prototyping; no card; phone verification reported on some flows | One NIM key from build.nvidia.com provisions **both** names (catalog alias pair). Pre-warn before any Google prompt |
| `OLLAMA_API_KEY` | Ollama Cloud | **EXISTS** — "Thank you for joining Ollama" 2026-10-22 + Google sign-in same day | Free tier for light usage; pay-as-you-go is optional, no subscription required | Sign in, create cloud key, provision, verify |
| `MISTRAL_API_KEY` | Mistral AI (La Plateforme) | **EXISTS** — consumer account in active use since mid-2026 (support/usage mail); a La Plateforme API key is NOT ESTABLISHED | La Plateforme "Free mode" is the default for new API accounts, no card; phone verification may be required | Open La Plateforme on the existing account, create workspace key, provision, verify. Phone step, if forced, is an owner-phone item |
| `GOOGLE_API_KEY` | Google AI Studio | **EXISTS** — fleet Google account; AI Studio mail Oct 2026; `GEMINI_API_KEY` already provisioned | AI Studio keys are free, no card | Two routes, do not conflate: (a) mint a separate AI Studio key under this name, or (b) owner-confirm the repoint to the provisioned Gemini key. Catalog code treats `GOOGLE_API_KEY` as the Gemini alias, but the earlier equivalence ruling was NOT VERIFIED — route (b) needs the owner's word |

### Batch C — no account on current evidence, creation is free / card-free

| Secret name(s) | Provider | Account evidence | Free / card state | Next action |
|---|---|---|---|---|
| `AION_API_KEY` | Aion Labs | NONE | Free tier by default on signup (daily allowance), no card | Create (email), mint key, provision, verify |
| `LLM7_API_TOKEN` | LLM7.io | NONE | Free email token (100K tokens/24h); endpoint also works anonymously at lower limits | Create token, provision, verify |
| `REQUESTY_API_KEY` | Requesty | NONE | Free account, free models 200 req/day, explicitly no credit card, no trial expiry | Create, mint key, provision, verify |
| `ROUTEWAY_API_KEY` | Routeway | NONE | Free API key offered at routeway.ai; catalog is public/anonymous for discovery | Create, mint key, provision, verify |
| `UNOROUTER_API_KEY` | UnoRouter | NONE | Free tier on a usage-based gateway | Create, mint key, provision, verify |
| `SEALION_API_KEY` | SEA-LION (AI Singapore) | NONE | Sign in with Google, no card, no region wall (per the provider reference the catalog ecosystem uses) | Create via Google route — **pre-warning to main chat before any prompt**, then mint key |
| `KILO_API_KEY` | Kilo (Kilo Code gateway) | NONE | Free models exist; the gateway even allows unauthenticated access to some — a key raises limits | Create, mint key, provision, verify |
| `ZAI_API_KEY` | Z.ai (Zhipu) | NONE (code-referenced only; outside the workflow audit's scope) | GLM Flash models (4.5/4.6V/4.7) are $0-priced; no card | Create, mint key, provision, verify |
| `MODELSCOPE_TOKEN` | ModelScope (Alibaba) | NONE | API-Inference free for registered users (~2,000 req/day claimed); signup may force phone verification | Create; if a phone/real-name gate is forced, stop and record it as gated |
| `SILICONFLOW_API_KEY` | SiliconFlow | NONE — never started on current evidence | International platform: $1 signup credit, no card. The .cn platform's $0 models require mainland real-name authentication + phone signup | Create on the international platform only; do **not** attempt the .cn real-name route |
| `XFYUN_API_KEY`, `IFLYTEK_SPARK_API_PASSWORD` | iFlytek (XFYun / Spark) | NONE | Global platform: email signup + verification code, 90-day free trial per capability; Spark Lite is permanently free. Credentials are per-application: APPID / APIKey / APISecret, plus the Spark **API Password** | Create one account + one application; harvest both names from it, provision, verify |
| `XKIRO_API_KEY` | xKiro | NONE | Hosted gateway (api.xkiro.com); catalog code marks some models `access_tier == free`. **Not** the same surface as Kiro IDE (kiro.dev) — no relation is established | Create, mint key, provision, verify. Do not touch the owner-gated Kiro identity for this |

### Batch S — not an external signup at all

| Secret name(s) | Provider | Finding | Next action |
|---|---|---|---|
| `OMNI_API_KEY`, `OMNIROUTE_API_KEY`, `OMNI_BASE_URL` | OmniRoute | OmniRoute is a self-hostable open-source gateway; the catalog endpoint is a hosted instance (`cloud.omniroute.online`). An OmniRoute API key is *generated by an instance's dashboard* (Endpoints page), and `OMNI_BASE_URL` is itself phantom — no fleet instance is configured anywhere the workflows can read | No account exists to "create" until an instance decision exists: use the hosted cloud instance (account = that service's signup, terms not yet reconned) **or** deploy a fleet instance and generate the key locally. Escalated to main chat as a decision item, not a signup |

### Batch G — gated: do not create / do not activate

| Secret name(s) | Provider | Account evidence | Gate |
|---|---|---|---|
| `CEREBRAS_API_KEY` | Cerebras | NONE | **CARD-GATED.** Terms changed 2026-07-16: no permanent free tier; the $5 trial credit is granted only *after adding a verified payment method*, and Playground/API stay inactive without one (Cerebras's own changelog/FAQ). Older directories still saying "no card" are stale. Recorded card-gated; not created |
| `ANTHROPIC_API_KEY` | Anthropic | NOT ESTABLISHED — Claude-consumer mail exists (data export Aug 2026, policy mail); a Console (API) org is not established | **PAY-FIRST.** Current Anthropic help position in secondary sources: credits are purchased before API use; no recurring free tier is established. Key creation is free but a zero-balance key is not a usable free route. Owner ruling needed before any purchase |
| `OPENAI_API_KEY` | OpenAI | NOT ESTABLISHED — ChatGPT-consumer mail exists; a platform (API) account is not separately established | **PAY-FIRST.** No free credit for new API accounts in current sources; Tier 1 requires a $5 prepay (payment instrument). Owner ruling needed |
| `CODEX_API_KEY` | OpenAI (Codex) | Same account family as OpenAI | Catalogued in provision-secrets.yml as its own name with `OPENAI_API_KEY` as fallback. Rides on the OpenAI ruling above; do not provision separately |
| `GAMUT_JUDGE_API_KEY` | GAMUT evaluation judge | Mail trace exists (Team Gamut marketing Sep–Oct 2026) but no API account is established — and none is needed: `remote-gamut-evaluation.yml` maps this secret into the `OPENAI_API_KEY` env var for a judge model | This is an **OpenAI key under a second name**, not a Gamut product key. It provisions if/when the OpenAI ruling lands, as a dedicated judge key on that account |
| `TYPHOON_API_KEY`, `OPENTYPHOON_API_KEY` | SCB10X Typhoon | NONE | **NOT CURRENTLY ISSUABLE on public evidence.** Typhoon API Pro was hosted on Together AI and deprecated 2025-12-31; the announced AWS-native Typhoon API ("launching in 2026") has no established live signup. Both names are one family. Defer; recheck when the new API launches |
| `OVHCLOUD_API_KEY` | OVHcloud AI Endpoints | NONE | **LOW PRIORITY / PART-GATED.** The endpoints work *keyless* at anonymous rate limits (the catalog already polls them publicly), so no key is needed for catalog evidence. A key requires an OVHcloud account + a Public Cloud project; whether project creation forces a payment-method validation is NOT ESTABLISHED. Do not start until that is answered from OVH's own flow |

## You.com — recon answer to the brief's open question

You.com **exists** (created 2026-10-22; "You've created your API key!" 2026-10-23 —
the email holds no key value) but it has **no secret name, no workflow reference,
and no registry row** in the phantom subset or the catalog SECRETS maps read for
this recon. It does not belong to this burn-down. If a lane wants it wired, that
starts with a catalog/workflow change, not with provisioning.

## Work order (this lane, from here)

1. **Batch H harvests** (Cohere → SambaNova → NVIDIA → Ollama → Mistral →
   Google decision), each: sign in → mint/copy key → provision via the sealed-box
   Actions-secrets API through the PAT helper → dispatch provider-availability /
   phantom-secrets audit → confirm `credential_present` / name flipped.
2. **Batch C creations** in table order, free/card-free routes only; any flow that
   surfaces a card field, a forced real-name check, or a phone gate that cannot
   be completed stops at that provider and is recorded as gated.
3. **Batch S/G stay parked** pending the owner/main decisions named above.
4. After each batch: phantom-secrets audit dispatch (workflow_dispatch is the
   reliable trigger) and a burn-down delta report to main chat, signed
   [MUSEai]@{role:{account-creation}}.

*Names only. No secret values appear in this document, and none were read during
this recon. Signup terms are as published at recon time (2026-10-27) and are
re-checked at each provider's own flow before any account is created.*
