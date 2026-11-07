# ACCOUNT-CREATION RECORD — 2026-11-01

`[MUSEai]@{role:{account-creation}}` · names+status only (∅ values, ∀ surfaces) · store census: **66** (2026-11-01, PAT live) · supersedes-in-part ACCOUNT-CREATION-RECON-2026-10-27

## PROVISIONED ∧ store-verified (this lane)
| name | verify | state |
|---|---|---|
| COHERE_API_KEY | run 40599868866 | 17 models |
| SAMBANOVA_API_KEY | run 40600278153 | 6 models · `fleet` exp ~2027-01-25 |
| NVIDIA_API_KEY ∧ NVIDIA_NIM_API_KEY | run 40605450460 | 1 key · 85 models · exp 2027-10-27 |
| OLLAMA_API_KEY | run 40606324374 | 23 models |
| GOOGLE_API_KEY | direct 200 | AI Studio proj gen-lang-client-0865483516 · free tier |
| LLM7_API_TOKEN | run 40608056036 | **exp 2026-11-27** (nearest rotation) · name = _TOKEN, _KEY absent |
| AION_API_KEY | run 40608378822 | Tier 0 prepaid · $0 |
| SEALION_API_KEY | direct 200 | — |
| ROUTEWAY_API_KEY | direct 200 | completion 402 (funded-out) |
| PINECONE_API_KEY | direct 200 | org "LoggedOut's Org" · idx swaying-dogwood |
| UNOROUTER_API_KEY | run 40704824602 | catalog 324 (Swarm) · completions consent-gated ⇒ HITL list |
| ZAI_API_KEY | direct 200 | completion 429 insufficient-balance |
| XKIRO_API_KEY | direct 200 | — |
| SILICONFLOW_API_KEY | direct 200 ∧ re-probe 41264932179 | 81 models · dead-flag RETRACTED (PR #2896) · completion 402 |
| HUGGINGFACE_TOKEN | replaced 2026-11-01 | `fleet` fine-grained (repo.read + inference.serverless.write + endpoints.infer.write) · 403⇒402 |
| DEEPINFRA_API_KEY | Swarm check 2026-11-01 | catalog 173 · invoke 402 · PR #3208 |
| NOVITA_API_KEY | Swarm check 2026-11-01 | catalog 98 · invoke 403 · PR #3214 |
| FRIENDLI_API_KEY | Swarm check 2026-11-01 | catalog 5 · Tier 0 · PR #3224 |
| BASETEN_API_KEY | Swarm check 2026-11-01 | catalog 20 · **invoke ✓ 200** · $1+$2 real credits · PR #3235 |
| GEMINI_API_KEY ↦ repo:repo-story | live 200 + read-back 2026-11-01 | Actions track = 0865483516 key · ≠ vault track MUSE_GEMINI_COMMS (LLM-cnxns) |

## Pre-existing in store (∅ this lane)
GROQ_API_KEY (catalog 14 = 6 prod + 8 preview, VM-vantage read 2026-11-01; Actions egress 403) · AION count 6 (api.aionlabs.ai/v1/models, endpoint-verified) ⇒ counts ↦ Swarm/fix-seat, fold pending.

## Endpoint floor (Swarm, PRs)
7,046 (#3189) → +173 deepinfra (#3208) → +98 novita (#3214) → +5 friendli (#3224) → +20 baseten (#3235) = **7,342** · target 7,500+

## Tiers (rule: KEY-LIVE names its tier)
catalog-live ≠ completion-live. Completion-live ✓: baseten (credits) ∧ pre-wave set per Swarm invoke #3141. Funded-out @completion: {zai 429 · llm7 402 · routeway 402 · siliconflow 402 · HF 402 · deepinfra 402 · novita 403 · friendli 403 · aion Tier-0}.

## ∅ CC — owner fact (2026-11-01 13:04 PT) ⇒ card-gated = CLOSED class
∅ key: nebius (acct exists, mandatory card) · together (acct, ≥$15) · cerebras (card pre-trial) · anthropic/openai/codex/gamut (pay-first) · WhatsApp WABA (payment method).
Funded-out permanent (keys above): HF credits/PRO · deepinfra · novita · friendli promo · zai/llm7/routeway/siliconflow balances.
Re-open ⇔ owner states a card exists. "Top-up item" framing RETIRED (Swarm PR #3243 concurs).

## HITL/auth living list (browser|PW|auth only; update on Δ)
- requesty — Google vault entry ⇒ SSO + key (acct exists 2026-10-27)
- ovhcloud — vault PW entry ⇒ signup completes (post-acct card check unobserved)
- xfyun ∧ IFLYTEK_SPARK_API_PASSWORD — vault login (card in Accounts lane chat) ⇒ `fleet` app + Spark Lite
- IG pluckyonyx78 — vault PW (card in this lane chat) ⇒ submit + email-code [AUTO] + Professional
- hyperbolic — Google vault entry ⇒ signup + key
- unorouter consents — vault login ⇒ per-provider consents ⇒ 324-catalog completions unlock
- ai21 — vault login ⇒ acct + key
- kilo — owner tab takeover (Cloudflare ∀ agent attempts; Accounts lane route)
- upstage — acct + `fleet2` key exist; value clipboard-only UI ⇒ human copy (Tier 0/$0, low value)
- modelscope — GitHub-OAuth [ruling] ∨ SMS
- meta app "Termux Fleet Pages" — SMS number [ruling] (developer verify step)
AUTO patterns proven: Gmail code fetch (nebius ✓) · Cloudflare env-replace pre-signin (nebius ✓) · live-session SSO (deepinfra/novita/friendli/baseten ✓ ∅ HITL)

## Rulings ∧ parked
mistral = DO-NOT-PROVISION (PR #1805) · typhoon×2 ¬ issuable (Together-hosted, deprecated 2025-12-31) · omni family = instance decision @main · X = parked fleet-wide (dev acct @LoggedoutT44951, $0) · tiktok = connector-blocked.

## Monikers (registry v3, config/registration_monikers.json)
cohere HappyCanyon42 · requesty UrbanCanyon15 · kilo RapidHarbor74 · zai JollyVale52 · model-scope LivelyWillow16 · silicon-flow AmberFalcon96 · iflytek PluckyOasis73 · xkiro OpalOnyx77 · pinecone GentleWalnut50 · IG PluckyOnyx78 · Threads JollyJuniper25 · TikTok UrbanOnyx67 · WhatsApp OpalVale19

## HF quota change (verified 2026-11-01)
free $0.10/mo ⇒ **None** (hub-docs PR #2865, merged 2026-10-07) · PRO $9/mo ⇒ $2/mo · acct invoices Jun $0.01 + Jul $0.02 = old-regime traces · usage Sep–Nov = "No usage".
