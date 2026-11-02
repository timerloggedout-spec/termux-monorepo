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


## Batch 2 (2026-10-31, probe run 41263537880, PR #2862; routes per gaps recon PR #2859)

One read-only GET per provider from Actions with the verified secret name. Grades: `api-verified` = real account object or key-gated surface answered 200; `api-read` = public surface answered (auth not proven); failures recorded verbatim.

- **Key live (200, key-gated) — free layer receiving, limits not exposed by the surface:** cohere (models), sambanova (models), zai (models), llm7 (models), routeway (models), unorouter (models; roster visibly carries `:free` ids, AI-Horde class), gemini (models list is key-gated ⇒ key live; AI Studio free-quota class, no balance object).
- **huggingface — api-verified account:** user `timerloggedout-hf`, `isPro = false`, no orgs ⇒ free account, receiving; no PRO credits layer.
- **vercel — api-verified account:** user `timerloggedout-5184` answered; plan not present in the user object ⇒ plan `not-established`, account live.
- **supabase — api-verified management surface:** the stored key answers the Management API projects read: 1 project (`termux-monorepo-lane-state`) ⇒ account surface readable; tier not in the project object ⇒ `not-established`.
- **pinecone — api-verified:** 2 indexes Ready (`swaying-dogwood`, `termux-knowledge`) ⇒ receiving.
- **fly — api-verified:** org `personal` (PERSONAL) via GraphQL viewer read ⇒ account live.
- **ollama, nvidia — api-read only:** public model surfaces answered 200; auth NOT proven by these endpoints.
- **siliconflow — ERRATA (corrected 2026-10-31):** batch-2's `credential-dead` verdict is RETRACTED. The probe hit `api.siliconflow.cn` (the separate CN platform) — its 401 was a platform mismatch, not key death. Canonical surface = `api.siliconflow.com`: key reads 200 (models; provisioning reads 2026-10-28 + 2026-10-31, 81 models; this lane's re-probe run 41264932179 = 200). The .com account endpoint `/v1/user/info` is DEPRECATED (410, code 20092, run 41264677968) ⇒ balance state `not-established`; key LIVE, free layer receiving. Lesson recorded: a rejection verdict requires the CANONICAL surface for the credential's platform (same discipline as the cloudflare verify-scope caveat).
- **cloudflare — rejected at user-scope verify:** 401 code 1000 on `/user/tokens/verify`; an account-scoped token is NOT excluded (different verify path) ⇒ `verify-scope` caveat, not ruled dead.
- **Edge-blocked, NO verdict (Cloudflare 1010 from the Actions egress):** groq, xkiro, **felo** — felo claim-state therefore STILL `verify-claim-state` (owner-attested stands); route forward = non-Actions egress.
- **Route-dead:** aion (404 `no Route matched` — base/path wrong, no key verdict), sealion (DNS does not resolve — phantom-route candidate).
- **Not executable (no credential under any name — provisioning lane, per gaps recon):** cerebras, mistral, requesty, xfyun (doubly phantom), kilo, modelscope, omni, ovhcloud, typhoon.

Batch-2 totals: unclaimed allocations established = ∅; new card flags = ∅; credential-dead = 0 (siliconflow entry corrected by errata above).

## Remaining families (state `not-established`, route named)

g4f (61 records — aggregator; per-upstream verification rides the g4f resolution: 17 ESTABLISHED / 43 NOT), cloudflare, render, supabase, pinecone, turso, upstash, aws, gcp, oracle, meta, vercel (connector on hand — batch 2), azure, digitalocean, huggingface (saved login — batch 2), gemini (AI Studio route live — batch 2), ollama, grafana, partners, fly, koyeb, platform201, deno, netlify, aion, cerebras, cohere, groq, kilo, llm7, mistral, modelscope, nvidia, omni, ovhcloud, requesty, routeway, sambanova, sealion, siliconflow, typhoon, unorouter, xfyun, xkiro, zai, fleet.

Routes by class: Actions-secret probe (where a repo secret exists — the OpenRouter pattern) · connector read · signed-in browser read (fleet sessions) · no-route (recorded, never invented). Batch order follows recoverable-value likelihood: credit-bearing AI providers first (groq, cerebras, cohere, mistral, sambanova, siliconflow, zai, kilo, llm7, requesty, routeway, unorouter, felo-verify), then infra (cloudflare, vercel, supabase, turso, upstash, pinecone, render, fly, koyeb, netlify, deno).

## Standing rules

- A row is `api-verified` only with a dated firsthand read on record; everything else carries its evidence class or `not-established`.
- `unclaimed-allocation` flags ONLY on evidence an allocation exists ∧ is not credited — recoverable value, reported same-day.
- Any card requirement ⇒ `parked-card`, reported, ∅ purchase (owner rule).
- **Mirror duty (viz PR #2910):** the 🚦 live index (quota.html) fetches this feed from master with `apps/tribute-dashboard/data/allocation-verification.json` as fallback mirror — every census refresh PR MUST update the mirror byte-identical to `ops/quota/allocation-verification.json` (guard-tested viz-side).
