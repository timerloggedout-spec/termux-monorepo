# Allocation Verification — per-provider free-tier ∧ credit census

`[MUSEai]@{role:{quota-specialist}}` · Program (owner order via doe-expert, 2026-10-31): verify by API read, ∀ integrated providers — production-directed reads only (∅ synthetic spend, ∅ card anything):

1. **Explicitly-labeled free tier** — exists? are we actually receiving it (enrolled/active)? limits?
2. **Credit allocations** — signup/program/referral/grant credits: are we GETTING them (claimed + credited) or leaving them unclaimed? Balance + consumption state.
3. **Replenishment gates** — what refills, what expires, what gates resupply.

Owner semantics: credits available with no spend from us = **free-equivalent** while they last; when credits run out behind replenishment gates, the explicitly-free tier is STILL available underneath — both layers reported per provider, never collapsed.

Row shape (feed: `ops/quota/allocation-verification.json`, schema `quota.allocation-verification/v1`):

```json
{"provider": "...", "evidence": "api-verified | doc | owner-attested | not-established",
 "free_tier": {"state": "active | available-not-enrolled | none | not-established", "limits": "..."},
 "credits": {"available": "...", "claimed": "yes | no | not-established", "balance": "...", "source": "..."},
 "replenishment": {"mechanism": "...", "gate": "..."},
 "verdict": "free | free-equivalent | layered | parked-card | not-established",
 "flags": ["unclaimed-allocation | card-required | verify-claim-state"]}
```

## Batch 1 (2026-10-31, firsthand API reads)

### openrouter — `api-verified` (PR #2828, run 41261080142 + bracket series PR #2842)
- free_tier: **active** — key `is_free_tier = true`; free-model allowance 50/day (`free_model_daily_requests` {used 3, limit 50} at first read; production free traffic demonstrably moves it).
- credits: purchased balance **$0.00** (`total_credits 0`, never purchased); `total_usage 0.206466965` consumed at account level (allowance-class consumption, key-level counters 0).
- replenishment: free allowance refills daily; paid credit resupply gates on a purchase (card) ⇒ **parked-card** for the paid layer; free layer continues underneath.
- verdict: **layered** (free active; paid layer parked-card). Flag: `card-required` (paid layer only).
- **Free-roster rotation hazard (verified 2026-11-01, catalog API read):** the 50/day allowance is variant-generic, but the :free ROSTER rotates — catalog = 452 models, DeepSeek 18 (ALL PAID, :free = ∅), `deepseek/deepseek-r1:free` DELISTED, total :free variants = 14. Any design pinned to a specific :free id is exposed: the repo's free-catalog snapshot (`scripts/openrouter_free_catalog.py` data) still lists r1:free = STALE, and the DeepSeek invoke/review reroute pins that id — route owners notified via the census relay. Flag: `free-roster-rotation`.

### github — `api-verified` (plan + buckets) / billing `not-established`
- free_tier: **active** — account plan = `free` (API). API buckets per principal, all live-verified: PAT 5000/h core, per-App 5000/h per installation, `GITHUB_TOKEN` 1000/h/repo. Actions minutes on public repos = free entitlement (doc); user billing endpoints return 404 to the PAT (scope) ⇒ minutes balance **not-established**.
- credits: no grant/credit program read on this surface — `not-established`.
- replenishment: buckets refill hourly (phase-aligned; see allocation plan smooth-flow); minutes monthly.
- verdict: **free**.

### neon — `api-verified`
- free_tier: **active** — account `plan = free` (API, `/users/me`); 2 projects live under the org (lane-events store receiving writes — we ARE receiving the tier).
- credits: no credit/grant balance exposed on the read surface — `not-established`.
- replenishment: free-plan monthly allowances (doc class); upgrade gates on billing (card) — not taken.
- verdict: **free**.

### jules — surface-enumerated
- free_tier: available via the Google account (sessions run in production — D1/D2 builds); the Jules API surface (sessions + activities) exposes **no quota/balance object** ⇒ limits + consumption `not-established` by construction of the API.
- credits: `not-established` (no credits surface in API).
- verdict: **free (receiving)**; limits row stays `not-established` until Google exposes them.

### felo — `owner-attested` (exemplar)
- Owner-named exemplar of the semantics: credits available ⇒ **free-equivalent** while they last.
- API verification route from this lane: `not-established` (no connector/key on hand) ⇒ flag `verify-claim-state` (claimed/balance unconfirmed firsthand — NOT ruled unclaimed).

## Remaining families (state `not-established`, route named)

g4f (61 records — aggregator; per-upstream verification rides the g4f resolution: 17 ESTABLISHED / 43 NOT), cloudflare, render, supabase, pinecone, turso, upstash, aws, gcp, oracle, meta, vercel (connector on hand — batch 2), azure, digitalocean, huggingface (saved login — batch 2), gemini (AI Studio route live — batch 2), ollama, grafana, partners, fly, koyeb, platform201, deno, netlify, aion, cerebras, cohere, groq, kilo, llm7, mistral, modelscope, nvidia, omni, ovhcloud, requesty, routeway, sambanova, sealion, siliconflow, typhoon, unorouter, xfyun, xkiro, zai, fleet.

Routes by class: Actions-secret probe (where a repo secret exists — the OpenRouter pattern) · connector read · signed-in browser read (fleet sessions) · no-route (recorded, never invented). Batch order follows recoverable-value likelihood: credit-bearing AI providers first (groq, cerebras, cohere, mistral, sambanova, siliconflow, zai, kilo, llm7, requesty, routeway, unorouter, felo-verify), then infra (cloudflare, vercel, supabase, turso, upstash, pinecone, render, fly, koyeb, netlify, deno).

## Standing rules

- A row is `api-verified` only with a dated firsthand read on record; everything else carries its evidence class or `not-established`.
- `unclaimed-allocation` flags ONLY on evidence an allocation exists ∧ is not credited — recoverable value, reported same-day.
- Any card requirement ⇒ `parked-card`, reported, ∅ purchase (owner rule).
