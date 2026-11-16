# Provider Dispatch Capability — the 89-provider bench vs the dispatch funnel

Owner order 2026-11-01 (provider utilization FIX — "USE THEM ALL"): desk
dispatch ran through a 4-lane funnel {Jules, Gemini, DeepSeek,
command-dispatch} while the registry carries **89 distinct model-lane
providers** (91 records; firsthand count @master 2026-11-01). This doc is
the capability map of record for widening: every registry model provider
classified by dispatch state, from registry + workflows @master, with
run evidence read firsthand via the Actions API (Collector App token).
Classes: **(a)** dispatch-wired and proven · **(b)** wired, per-provider
invoke unproven · **(c)** triggerable via existing surfaces, no dedicated
wiring · **(d)** inference-only, with the wiring that would promote it.

## Dispatch surfaces of record

| Surface | Trigger | Roster | Run evidence @2026-11-01 |
|---|---|---|---|
| `agent-jules-on-issues.yml` | issue label | Jules (build arm; registry `jules.build_sessions`, lane ci) | 405 successful runs, last 2026-11-01 |
| `gemini-dispatch.yml` (+ `gemini-after-peers.yml`) | issues / issue_comment | google (Gemini) | dispatch successes 2026-11-01; after-peers 1,158 successes. Standalone `gemini-invoke/triage/review` = 0 successful runs — the router is the proven entry, the legs are not independently proven |
| `deepseek-ci.yml` + `deepseek-termux-agent.yml` | events + dispatch | DeepSeek (registry `deepseek.build_dispatch`, lane ci) | successes 2026-11-01; termux-agent 22 successes |
| `provider-batch.yml` | dispatch | 24-provider inference roster (below) | 249 runs, 138 successful at first census. **Gate state: GREEN — #2672 RESOLVED + CLOSED 2026-11-01 (fix chain PRs #3126/#3128/#3130/#3138); proof run 41308987754 (workflow_dispatch, head 87453e9c) SUCCESS: contracts ✓, operational_providers ✓ — the first operational evidence leg executed; the earlier blocked-by-#2672 state (observation jobs gated on the red `contracts` job) is historical** |
| `provider-command-dispatch.yml` | dispatch / repository_dispatch | coderabbit, qodo, devin (review-arm class; not registry model providers) | 1 run, success 2026-10-18 |
| `ai-studio-delphi-trigger.yml` | dispatch | google (AI Studio) | 1 run, success 2026-10-30 |
| `provider-availability.yml` | schedule | probe roster | 93 runs, recent 30/30 success, last 2026-10-28 — probes availability, does not dispatch work |
| llm_api_hub + MSM catalog | API / selection | catalog roster (16, below) | selection layer; admission-gated (`research-provider-admission/v1` policy) |

The batch roster = `llm_api_hub/server/research_providers.py` ENDPOINTS
(14 native) + `provider_protocols` {cloudflare, cohere, ollama} +
`provider_extensions` {requesty, routeway, sealion, typhoon, unorouter,
xfyun, xkiro} = **24**. The MSM catalog roster
(`scripts/provider_model_catalog.py` ENDPOINTS) = 16 {aion, cerebras,
felo, gemini, groq, huggingface, kilo, llm7, mistral, modelscope,
nvidia, omni, openrouter, ovhcloud, sambanova, siliconflow}.

## (a) Dispatch-wired and proven — 2 of 89

| Provider | Wiring | Proof |
|---|---|---|
| google | gemini-dispatch router + after-peers + ai-studio trigger + batch `gemini` leg | workflow successes 2026-11-01 (above); census key-live |
| openrouter | production invoke legs (swarm/DoE workflows) + `openrouter-free-catalog-sync` | catalog-sync 33 successes, last 2026-10-31; free-counter evidence (allocation census: 50/day :free layer live). Paid layer parked at $0.00 balance; :free roster rotates — same-day roster check before pinning an id |

## (b) Wired, per-provider invoke unproven — 22 of 89

The provider-batch surface is proven (138 successful runs) but
per-provider invoke success is not audited per provider in batch
artifacts; treat each as wired-unproven until a batch result names it.
Flags from the allocation census (batch-2, 2026-10-31) where they exist:

aion (flag route-dead: hub endpoint 404 + site DNS dead) · cerebras
(flag no-credential) · cloudflare (flag verify-scope: account-scoped
token) · cohere (key-live 200; **gate-state: GREEN since 2026-11-01 (#2672 closed; run 41308987754)**) · groq (flag route-blocked: Cloudflare
1010 from Actions egress; invocable from non-Actions egress) ·
huggingface (key-live; free, isPro=false) · kilo (flag no-credential) ·
llm7 (key-live; **gate-state: GREEN since 2026-11-01 (#2672 closed; run 41308987754)**) · mistral (flag no-credential) · modelscope (flag
no-credential) · nvidia (api-read only; auth not proven) · ovhcloud
(flag no-credential) · requesty (flag no-credential) · routeway
(key-live; **gate-state: GREEN since 2026-11-01 (#2672 closed; run 41308987754)**) · sambanova (key-live; **gate-state: GREEN since 2026-11-01 (#2672 closed; run 41308987754)**) · sealion (flag route-dead: DNS) ·
siliconflow (key-live 200 post-errata, `.com/v1/models`; **gate-state: GREEN since 2026-11-01 (#2672 closed; run 41308987754)**) · typhoon
(flag no-credential) · unorouter (key-live; :free ids visible; **gate-state: GREEN since 2026-11-01 (#2672 closed; run 41308987754)**) · xfyun
(flag no-credential, doubly phantom) · xkiro (flag route-blocked:
1010 from Actions egress) · zai (key-live; **gate-state: GREEN since 2026-11-01 (#2672 closed; run 41308987754)**).

The seven members formerly gate-blocked — cohere, sambanova, zai,
llm7, routeway, unorouter, siliconflow — are exactly the census
key-live set: the contracts gate went GREEN 2026-11-01 (#2672
closed, run 41308987754 with operational_providers ✓), so their
operational evidence leg now executes; per-provider (b) → (a)
promotion follows Swarm's invoke-phase results as they land.

DeepAgent arm (adjacent, rides the DeepSeek/device route): workflow-
level dispatch proven today (Swarm firsthand, run 41301564332); the
device leg is NOT_ESTABLISHED (reachable=false) — a green workflow run
is not device execution evidence.

Reverse gap: batch roster member **ollama** has no registry model
provider row (its registry record sits under a different provider
string) — wiring exists without a registry row; registry lane's call.

## (c) Triggerable via existing surfaces — 2 of 89

| Provider | Surface | Note |
|---|---|---|
| felo | MSM catalog endpoint; owner-attested free-equivalent | Not in the batch roster (no research_providers endpoint); triggerable once an admission-policy entry exists. Claim-state flag verify-claim-state; Actions egress 1010-blocked, use non-Actions route |
| omni | MSM catalog endpoint | Catalog-only; same admission step as felo promotes it to (b) |

Every (b) provider is additionally triggerable directly through the
llm_api_hub API (admission policy permitting) without the batch
workflow — the hub is the generic surface; the batch is its scheduled
exercise.

## (d) Inference-only — 63 of 89, and what promotes them

- **g4f upstreams (60 `g4f/*` providers + `gpt4free/CLIProxyAPI/Chapito/ai-manus`):**
  reachable today only through g4f tester/library scripts (usage-log
  inference class in the registry; no dispatch workflow names g4f).
  Promotion, in order of leverage: (1) where a native API exists behind
  the upstream (e.g. `g4f/Groq`, `g4f/Cerebras`, `g4f/CohereForAI_*`),
  the native arm in (b) already carries the capability — route there,
  no new wiring; (2) for session/web-only upstreams (ChatGPT, Copilot,
  Perplexity, Grok, MetaAI, …), a g4f adapter leg in provider-batch
  (one ENDPOINTS-style entry + admission) makes them batch-triggerable;
  (3) image/audio/search upstreams (Pollinations*, StabilityAI,
  BraveSearch, …) promote via a media/search batch variant, not the
  chat batch.
- **meta** (3 records): pooled by PR #2952; draw starts on
  MODEL_API_KEY / META_API_KEY provisioning (provisioning lane), then a
  catalog + research_providers endpoint admission promotes to (b).
  `meta.llama_api` is excluded as RETIRED / DO-NOT-ROUTE.
- **github** (GitHub Models record): no invoke workflow exists.
  Promotion = one invoke step (models-scoped token) in provider-batch
  or a dedicated models leg; token scope is NOT ESTABLISHED today.

## Funnel arithmetic

Proven dispatch today reaches 2/89 registry model providers directly
(plus the Jules/DeepSeek build arms, which live outside the model
lane). The batch surface nominally covers 24 more, of which 9 carry a
no-credential or route-dead/blocked flag — the cheapest widening is
therefore: provision the 8 no-credential batch members (cerebras,
mistral, kilo, modelscope, ovhcloud, requesty, typhoon, xfyun),
route groq/xkiro/felo off Actions egress, admit felo + omni,
and audit batch artifacts per provider to move (b) → (a) honestly.
