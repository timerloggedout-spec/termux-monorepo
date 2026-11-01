# Quota routes RECON 🏅 — all service provider integrations (2026-10-31)

`[MUSEai]@{role:{quota-gaps}}` · Program: allocation verification (owner order via doe-expert → quota-specialist census, PRs #2846/#2851) · Completion of the route investigation assigned to this lane by the owner 2026-10-31.

**Question:** for every integrated provider family, does a working verification route exist — and if not, what exactly blocks it?

**Evidence (all firsthand, 2026-10-31):** census feed `ops/quota/allocation-verification.json` @master (51 rows: 5 established / 46 not-established) · repo Actions secret NAMES census via API (61 names; values never read) · cadence provider-onboarding cross-check (`ops/cadence/provider-onboarding.json`, 33 entries) · connector inventory on hand. Route classes per the census doc: **Actions-secret probe** (the OpenRouter pattern) · **connector read** · **signed-in browser read** · **no-route** (recorded, never invented).

## Verdicts — 51 families

| class | n | families |
|---|---|---|
| ✅ VERIFIED (census batch-1) | 5 | openrouter (layered) · github (free) · neon (free) · jules (free, limits API-dark) · felo (free-equivalent, owner-attested) |
| 🟢 READY — Actions-secret probe executable now | 20 | aion · cloudflare · cohere · fly · gemini · groq · huggingface · llm7 · nvidia · ollama · pinecone · routeway · sambanova · sealion · siliconflow · supabase · unorouter · vercel · xkiro · zai |
| 🔴 KEY-GAP — no credential on any fleet surface | 9 | cerebras · kilo · mistral · modelscope · omni · ovhcloud · requesty · typhoon · xfyun |
| 🟡 INFRA — browser-read or no-route | 15 | render · turso · upstash · aws · gcp · oracle · meta · azure · digitalocean · grafana · partners · koyeb · platform201 · deno · netlify |
| ⚪ SPECIAL | 2 | g4f (aggregator) · fleet (internal) |

## READY — credential evidence (secret names, repo Actions store)

aion `AION_API_KEY` · cloudflare `CLOUDFLARE_API_TOKEN`+`CLOUDFLARE_ACCOUNT_ID` · cohere `COHERE_API_KEY` · fly `FLY_IO_ORG_TOKEN` · gemini `GEMINI_API_KEY`+`GOOGLE_API_KEY` · groq `GROQ_API_KEY` · huggingface `HUGGINGFACE_TOKEN` · llm7 `LLM7_API_TOKEN` · nvidia `NVIDIA_API_KEY`+`NVIDIA_NIM_API_KEY` · ollama `OLLAMA_API_KEY` · pinecone `PINECONE_API_KEY` · routeway `ROUTEWAY_API_KEY` · sambanova `SAMBANOVA_API_KEY` · sealion `SEALION_API_KEY` · siliconflow `SILICONFLOW_API_KEY` · supabase `SUPABASE_KEY` (+`SUPABASE_URL` var) · unorouter `UNOROUTER_API_KEY` · vercel `VERCEL_TOKEN` (connector read also on hand — dual route) · xkiro `XKIRO_API_KEY` · zai `ZAI_API_KEY`. **felo verify** rides `FELO_AI_API` — the batch-1 `verify-claim-state` flag is executable now. Total executable verifications: **21** (20 probes + felo).

## KEY-GAP — findings

- cerebras · mistral · requesty were batch-2 headliners, but **no secret exists under any name** in the repo store (61-name census) — their census order assumed provisioning that never landed. Route blocked at provisioning, not at probe design.
- xfyun is doubly phantom: cadence onboarding names `XFYUN_API_KEY` + `IFLYTEK_SPARK_API_PASSWORD`; **both absent** from the repo store (matches the onboarding file's own recorded exception for xfyun).
- kilo · modelscope · omni · ovhcloud · typhoon: no key, no connector, no browser session on record ⇒ no-route until provisioned.

### Correction (2026-10-31, provisioning lane cross-check vs its record PR #1854 + rulings; spot-verified by this lane)

The KEY-GAP class above is a credential-store fact, not a work queue — per-item dispositions of record:

- **cerebras** ⛔ card-gated (terms Δ2026-07-16: $5 trial only after a payment method) ⇒ parked under the fleet card rule; ¬ gap-fillable.
- **mistral** ⛔ owner-ruled DO NOT PROVISION (PR #1805, merged — Mistral is a webWrapper, not an API key) ⇒ ruling, ¬ gap. ∅ re-attempt.
- **typhoon** ⛔ ¬ issuable (Together-hosted, deprecated 2025-12-31) ⇒ parked.
- **requesty · kilo** ◐ in-flight at the provisioning lane: accounts exist/creating; harvest gated solely on owner Google vault entry.
- **xfyun** ◐ in-flight at the provisioning lane (= iFlytek): gated on owner vault new-password entry; the pair mints together.
- **modelscope** ⛔ parked: ∅ Google route, registration is SMS-only; GitHub-OAuth route ⇒ owner ruling pending.
- **omni** ◐ ¬ a signup: instance decision at main (`OMNI_API_KEY`/`OMNIROUTE`/`BASE_URL`).
- **ovhcloud** ● the only actionable item: provisioning lane attempting the free account + Public Cloud route now; card ⇒ hard stop + park.

Net: of the 9, actionable-now = 1 (ovhcloud) · in-flight on owner vault entries = 3 (requesty, kilo, xfyun) · parked/ruled = 4 (cerebras, mistral, typhoon, modelscope) · decision at main = 1 (omni).

## INFRA — route notes

vercel-class connector reads exist only for vercel (READY above) and neon (verified). The 15 here have no key in the store; several are reachable in principle via signed-in fleet browser sessions (dashboards), none has a provisioned API route. aws account creation is **deferred by owner order** (code readiness + explicit approval) — route recorded as owner-gated, not missing. platform201 = the owner's own platform surface (internal accounting, rides fleet).

## SPECIAL

- **g4f**: aggregator over 60 upstreams; per-upstream quota already resolved at registry level (17 ESTABLISHED / 43 NOT ESTABLISHED, PR #2032). Route = upstream-by-upstream; no single g4f route exists or should be invented.
- **fleet**: internal surfaces (GitHub pool + Apps) — verified under the github row + AppID census (MAINT-02 owns the recurring per-app bucket readings).

## Work dispatched from this recon

- **quota-specialist (census owner):** batch-2a READY AI probes — groq, cohere, sambanova, siliconflow, zai, llm7, routeway, unorouter, aion, sealion, ollama, nvidia, gemini, huggingface, xkiro + felo verify (16) · batch-2b READY infra — cloudflare, vercel, supabase, pinecone, fly (5). Pattern = OpenRouter probe (production-directed reads, ∅ synthetic spend, ∅ card); each landed read flips its feed row to `api-verified` with the date.
- **provisioning lane:** KEY-GAP 9 — cerebras, mistral, requesty first (batch-2 assumed them), then kilo, modelscope, omni, ovhcloud, typhoon, xfyun. No-card routes only; any card gate ⇒ park + report.
- **doe-expert:** program state — routes ∀51 now definitive: 5 verified · 21 executable · 9 key-gated · 15 infra-browser/no-route · 2 special. UNCLAIMED allocations: still ∅ established anywhere (no read has yet evidenced an unclaimed credit).
- **INFRA 15:** no probe work dispatched — browser-read scheduling is a cadence decision; until then their rows stay honestly `not-established` with this route record.

## Standing rules (unchanged)

A row is `api-verified` only with a dated firsthand read. `unclaimed-allocation` flags only on evidence. Any card requirement ⇒ `parked-card`, reported, ∅ purchase. Documented limits are entitlements, never balances.
