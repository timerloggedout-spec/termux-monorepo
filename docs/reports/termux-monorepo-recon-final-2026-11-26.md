# RECON 🏅 — Provider, quota, pool-count, and dispatch audit

⌖scope → ▶Reconcile pinned refs, registries, provider catalogs, pool-count claims, and dispatch evidence → ⊗read-only; preserve all 172 quota records and the owner’s worktree → ⤵evidence, status, and next gates → ~complete

## Executive findings

1. ⌖pool counts → ▶separate units → ⊗registry/pair/endpoint counts ≠ people → ⤵172 = service IDs; 9,588 = provider/model universe; 7,341 = historical verified-endpoint floor; 5k+ = RPS claim; participant identities remain unproven → ~count meanings disambiguated
2. ⌖quota universe → ▶use pinned prepool registry → ⊗selected checkout is a distinct snapshot → ⤵172 unique service IDs at `5c6c0082cd836f502df26bc6ed9a5aef9ed2df10`; 26 rows at selected HEAD `f8ff2c7f3b220bb7b64f834d70f3dd975f6f2d04` → ~retain 172 as the minimum owner-mandated universe
3. ⌖provider status → ▶join all 33 canonical quota families → ⊗catalog sighting ≠ quota balance ≠ inference success → ⤵169/172 status rows are `unknown`, two `ok`, one `watch`; all 98 model-lane rows are `unknown`; each family has `inference_ok=false` in the dated snapshots → ~current $0-qualified access remains unproven
4. ⌖G4F → ▶retain 60 `REFERENCE_ONLY` source candidates plus umbrella record → ⊗`REFERENCE_ONLY` means refTemplate/source to harvest and activate, not exclusion → ⤵54 candidates map to 5,693 historical provider/model pairs; six have no historical pair rows → ~source eligibility stays separate from runtime evidence
5. ⌖runtime → ▶trace Observatory, fleet-swarm, QUE/QDesk, Mesh, Tribute, and inference receipts → ⊗workflow labels/tokens ≠ end-to-end inference evidence → ⤵zero verified `fleet-swarm → QUE/QDesk → provider/model inference → result/telemetry` receipts; no dedicated multi-endpoint stress harness or hard deployment maximum found → ~live tournament, enrollment, and stress remain gated
6. ⌖actions → ▶preserve user state → ⊗no live provider calls or deployment → ⤵112 offline tests passed; Swarms dry-run planned two agents/one loop with `model=null`; worktree unchanged → ~read-only recon

## 1. Pool-count claims and established components

| Claim | Verified unit and evidence |
|---|---|
| `172` | Unique quota service IDs in `ops/quota/registry.json` at pinned prepool ref `5c6c0082cd836f502df26bc6ed9a5aef9ed2df10`. The cohort adapter accepts externally supplied gate decisions; it does not generate a people/participant pool. |
| `9,588` | `docs/ops/G4F-WORKING-PROVISIONING.md` and `docs/ops/PROVIDER-CATALOG-POPULATION.md` define a G4F provider/model universe of 9,588 pairs across 160 providers: 5,347 upstream-only + 1,156 fork-only + 3,085 overlap. Two historical CSVs also each contain 9,588 unique `(provider, model)` pairs, but their extracted view has 67 populated provider labels and 5,068 model strings. The equal cardinality is verified; exact dataset identity/provider normalization is not. CSVs: `endpoint-mappings.csv` at `8b1854b04a5e30851bd3d2e5d9b59c12bb88664d`; `endpoints-db.csv` at `c0d0f05087958a89681717a6fe0432208b1ee6a1`. These are provider/model rows, not people. |
| `5k+` | Located text describes 5k requests per second (RPS), including the Bifrost recon claim; it is not a participant count. |
| `7k+` | PR #5759’s pool compiler carries a historical **7,341 verified-endpoint floor** from its desk-feed census. This is an endpoint-floor claim, not a participant count. The compiler does not calculate it; its matching test value is a synthetic fixture. The raw desk-feed blob/run receipt was unavailable, so the underlying count remains unverified. No participant identities, denominator, dedupe key, or generation receipt were found. |
| `676 / 455` | Repository inventories for two different owners, not participants. |

⌖pipeline → ▶trace source → transform → output → receipt → ⊗do not promote endpoint/provider-model rows to people → ⤵`scripts/prepool_cohort_adapter.py` is a pass-through adapter: it preserves records and consumes externally supplied gate decisions; it does not instantiate routes, dispatch inference, or generate participant identities → ~adapter role bounded

⌖established generator → ▶inspect PR #5759 local head `26227bd7…` → ⊗candidate compiler ≠ participant generator or runtime admission → ⤵`scripts/provider_catalog_population.py` reconciles desk feed + 172-record quota registry + dispatch model-lane bench + G4F working catalog + G4F endpoint universe + optional incumbent-v5 snapshot; merges candidate provenance; writes `population-v1.json` and a source-hash manifest; sets runtime-eligible and inference-admitted counts to zero → ~pool compiler found; absent from selected HEAD `f8ff2c7…` and pinned prepool `5c6c008…`

⌖next pipeline stage → ▶follow the design note → ⊗projection does not establish inference → ⤵`docs/ops/PROVIDER-CATALOG-POPULATION.md` documents `scripts.provider_catalog_competition` creating Incumbent and VultrInspired projections → ~candidate competition, not deployment

⌖7,341 provenance → ▶compare compiler, design note, and test → ⊗test fixture ≠ run receipt → ⤵the compiler carries the historical verified-endpoint floor from the desk feed; test `7,341` is synthetic; raw desk-feed object was unavailable in this shallow, blob-filtered checkout → ~underlying census remains unverified

⌖historical CSV quality → ▶inspect row-level probe fields → ⊗CSV rows ≠ execution receipts → ⤵`endpoints-db.csv` has 160 `probe_ok=True` flags without timestamp/request/response receipts, and 47 rows with blank endpoint URLs; `endpoint-mappings.csv` has blank `probe` fields throughout → ~mapping data, not verified inference

⌖9,588-byte hypothesis → ▶compare index metadata with CSV/docs → ⊗historical object scan has promisor-object gaps → ⤵the G4F docs and CSVs independently show 9,588 provider/model pairs; the index scan also found a 9,588-byte artifact match, but the exact-size scan was incomplete → ~byte-size match is a separate coincidence, not the pool count

## 2. Quota registry and polling semantics

⌖registry snapshots → ▶keep each ref distinct → ⊗do not merge branch counts → ⤵pinned prepool `5c6c0082...` = 172 rows; selected checkout HEAD `f8ff2c7f3b220bb7b64f834d70f3dd975f6f2d04` = 26 rows → ~branch copy is drift from the 172-row owner-mandated floor

⌖172-row public reading → ▶join by service ID → ⊗public projection withholds account-specific values → ⤵`apps/tribute-dashboard/data/quota.json` (`quota.readings.v2`, generated `2026-11-18T17:06:56.121328+00:00`) has 169 `unknown`, 2 `ok`, 1 `watch`; every `used` and `reset` is null → ~status projection, not current balance

The three non-unknown rows are:
- `github.actions.cache` → `ok`
- `github.api.github_token` → `watch`
- `vercel.deployments` → `ok`

The 98 model-lane rows are all `unknown`.

⌖historical polling → ▶separate registry status polls from provider catalogs → ⊗timestamps/catalog results do not prove a quota read or inference → ⤵quota promotion run `44354887888`, commit `6ce4eaa68a733730aae489b12fa3fd1ad4f7871d`; three dated catalog runs below; zero dated inference receipts → ~poll history exists, with different evidence classes

` scripts/quota_poll.py` direct readers include GitHub API/core, GitHub Actions cache, Vercel deployments, OpenRouter free-model requests, Hugging Face Hub API, and the OpenRouter key; Render and Neon use multi-readers. Hugging Face’s reader calls Hub `whoami-v2` and reads a Hub `RateLimit` header; it is not Hugging Face Inference Providers quota and sends no inference. OpenRouter key observations are status-only, with private values withheld. Public conversion writes `used:null` and `reset:null`, and uses `unknown` for withheld values or absent observations. Promotion workflow: `.github/workflows/quota-readings-promote.yml`.

Owner’s free-tier qualification semantics include refill credits, dollar allotments, and cycle windows. This audit preserves those criteria; a public `unknown` status does not mean a zero allowance or a confirmed free inference route.

## 3. All 33 canonical provider/quota families

Codes: `K` = dated catalog succeeded with credential present; `P` = public catalog succeeded without credential; `U` = Gemini catalog succeeded, free-account status explicitly unverified; `n` = row present without catalog success, generally missing credentials; `—` = no row in that snapshot. Every family has `quota_status=unknown` and `inference_ok=false` in every dated snapshot.

| Provider family | Quota ID(s) | Manager | Oct 23 | Nov 1 | Nov 2 |
|---|---|---|---|---|---|
| agentrouter | `agentrouter.models` | Unsupported | — | — | — |
| aion | `aion.free_tokens` | Unsupported | n | K | K |
| baseten | `baseten.api` | Docs only | — | — | n |
| cerebras | `cerebras.free_tokens` | Docs only | n | n | n |
| cloudflare | `cloudflare.workers_ai` | Docs only | K | K | K |
| cohere | `cohere.trial_calls` | Docs only | n | K | K |
| deepinfra | `deepinfra.api` | Docs only | — | — | n |
| deepseek | `deepseek.api` | Docs only | — | — | — |
| felo | `felo.api_credits` | Unsupported | K | K | K |
| friendli | `friendli.api` | Docs only | — | — | n |
| gemini | `gemini.api_free` | Docs only | U | U | U |
| groq | `groq.free_tier` | Passive adapter | n | K | K |
| huggingface | `huggingface.inference_providers` | Passive adapter | n | K | K |
| kilo | `kilo.free_models` | Docs only | n | n | n |
| llm7 | `llm7.free_token` | Docs only | P | K | K |
| mistral | `mistral.free_mode` | Docs only | n | n | K |
| modelscope | `modelscope.api_inference` | Docs only | P | P | P |
| novita | `novita.api` | Docs only | — | — | n |
| nvidia | `nvidia.api_catalog` | Docs only | n | K | K |
| ollama | `ollama.balance` | Passive; private opt-in | n | K | K |
| omni | `omni.gateway` | Unsupported | n | n | n |
| openrouter | `openrouter.free_models`, `openrouter.key` | Passive; private opt-in | K | K | K |
| ovhcloud | `ovhcloud.ai_endpoints` | Docs only | P | P | P |
| requesty | `requesty.free_models` | Docs only | P | P | P |
| routeway | `routeway.free_models` | Docs only | P | K | K |
| sambanova | `sambanova.free_tier` | Passive adapter | n | K | K |
| sealion | `sealion.api` | Docs only | n | K | K |
| siliconflow | `siliconflow.free_models` | Passive adapter | n | K | K |
| typhoon | `typhoon.api` | Docs only | — | — | — |
| unorouter | `unorouter.free_models` | Docs only | n | K | K |
| xfyun | `xfyun.spark` | Docs only | — | — | — |
| xkiro | `xkiro.free_models` | Docs only | P | P | P |
| zai | `zai.free_models` | Docs only | — | — | — |

Catalog-run counts:
- Oct 23 `39991236049` → 24 rows / 10 catalog successes / 4 credentials / 0 inference successes
- Nov 1 `41308757523` → 24 / 20 / 16 / 0
- Nov 2 `41456184549` → 28 / 21 / 17 / 0

Historical catalog batches list 578/645/702 entries, with 22/26/30 exact matches and zero automatic admissions. A historical OpenRouter no-cost attempt returned HTTP 429. These events show dated catalog activity, not current account-specific inference access or quota balance.

## 4. G4F `REFERENCE_ONLY` source candidates and activation path

⌖G4F roster → ▶harvest and activate all reference sources → ⊗`REFERENCE_ONLY` is a source/template role, not an exclusion or runtime ban → ⤵60 individual candidate records plus umbrella `g4f.vendors` = 61 G4F-associated records → ~retain all 60 candidates for harvesting

Historical crosswalk of candidate suffixes to provider/model CSV pairs: 54 candidates map to 5,693 pairs; six have zero historical model rows. Candidate totals below are historical source-corpus pair counts, not live inference counts.

| Candidate | Pairs | Candidate | Pairs | Candidate | Pairs |
|---|---:|---|---:|---|---:|
| `agenttools` | 1 | `airforce` | 793 | `antigravity` | 28 |
| `arena` | 153 | `bingcreateimages` | 1 | `blackforestlabs_flux1dev` | 3 |
| `blackforestlabs_flux1kontextdev` | 1 | `blackboxpro` | 380 | `bravesearch` | 2 |
| `cerebras` | 7 | `chatgpt` | 16 | `claude` | 2 |
| `cloudflare` | 108 | `cohereforai_c4ai_command` | 9 | `copilot` | 10 |
| `copilotapp` | 13 | `deepinfra` | 25 | `deepseek` | 3 |
| `elevenlabs` | 1 | `g4fspace` | 196 | `glm` | 6 |
| `gemini` | 21 | `geminipro` | 64 | `googleaimode` | 1 |
| `googlesearch` | 1 | `grok` | 20 | `groq` | 17 |
| `hailuoai` | 1 | `huggingchat` | 139 | `huggingface` | 138 |
| `huggingfacemedia` | 556 | `huggingspace` | 15 | `kilocode` | 403 |
| `llm7` | 1 | `metaai` | 1 | `metaaiaccount` | 1 |
| `microsoftdesigner` | 4 | `nvidia` | 86 | `ollama` | 27 |
| `omniroute` | 1 | `openaifm` | 18 | `openrouterfree` | 387 |
| `operaaria` | 2 | `perplexity` | 49 | `pi` | 1 |
| `pollinations` | 206 | `pollinationsaudio` | 38 | `pollinationsimage` | 33 |
| `puter` | 1,242 | `qwen` | 24 | `relayrouter` | 434 |
| `stabilityai_sd35large` | 2 | `teachanything` | 1 | `yqcloud` | 1 |

Six source-only candidates have no historical provider/model rows: `g4f.cachedsearch`, `g4f.geminicli`, `g4f.githubcopilot`, `g4f.markitdown`, `g4f.whiterabbitneo`, and `g4f.you`. Their source links reside in their registry rows at the pinned prepool ref.

Source-field totals for the 5,693 pairs: 3,085 `both`, 1,452 `upstream-g4f`, 1,156 `fork-catalog`. Crosswalk evidence: 5,315 exact `quota_record` ID matches; 5,654 rows with endpoint URL; 114 `probe_ok=True` flags without timestamp/request/response receipts. The 114 flags prove a historical field value, not current callable/free inference.

⌖activation route → ▶registry ID/source → historical provider/model corpus → catalog classification → evidence-linked gate decision → cohort adapter → ⊗adapter passes through candidate records and does not dispatch providers → ⤵activation requires current entitlement/quota/inference evidence and dispatch receipts → ~no candidate cleared for a live $0 tournament in this audit

`g4f.vendors` is an umbrella row. Keep it separate from the 60 individual source candidates. Preserve the owner’s refTemplate harvesting and activation mandate; keep source eligibility distinct from evidence status.

## 5. Observatory, fleet-swarm, QUE/QDesk, Mesh, Tribute, and regressions

⌖runtime chain → ▶trace `fleet-swarm → QUE/QDesk → exact provider/model → inference result → telemetry` → ⊗workflow definitions, dispatch names, and bot tokens ≠ successful inference receipts → ⤵zero complete end-to-end receipts or inference-regression artifacts verified in inspected refs → ~runtime outcome remains unproven

- Observatory/QUE/QDesk mechanics are present as static workflow/dispatch paths; complete provider/model inference receipts are absent from the inspected evidence.
- Mesh runner-hop history exists. The expected `docs/ops/flywheel-comms/REGISTRY.json` is absent at selected HEAD.
- Tribute execution is live-capable and can claim/fork/commit/open PRs/dispatch. This audit made no such claim or dispatch.
- `.github/workflows/team-mvt.yml` runs 5 lanes × 3 trials; it is live-capable and can call Felo/OpenRouter/Omni/Hugging Face. `promotion_ready=false` by default. It is not an offline test.
- Synthetic DSPy DoE stub, static selector, deterministic Swarms SDK fixture, and loopback Rust hub fixture are offline-capable test paths; none ran in this audit.
- No dedicated multi-endpoint stress harness or repo-wide hard deployment maximum was found in inspected paths. Production Vercel workflow consumes caller-supplied project list (default two); dashboard treats Vercel quota errors as optional and says to avoid retry loops.
- Keep queues, quota observations, telemetry, CSV evidence, and wallet ledgers separate; this audit found no wallet reconciliation proving parity.

## 6. BRR, skills, commits, and validation

⌖BRR → ▶use as read-only reconciliation/reporting over existing CRG output → ⊗BRR does not authorize promotion/deletion/closure/merge → ⤵docs/implementation at commit `a70a6e8b04d6039ca8bfd8b91cd8360800479e2f` on another reachable branch; files/report absent at selected HEAD → ~no BRR report generated

Relevant skills found: `.agents/skills/evidence-led-monorepo-ops/SKILL.md`, `.github/skills/forensic-recovery/SKILL.md`, `.github/skills/evidence-provenance/SKILL.md`, `.github/skills/production-reconciliation/SKILL.md`. No local SuperPowers/Superpowers skill was found.

Relevant history:
- Quota cadence/catalog `89ed1ced…`; registry/poller/weights `4fe260e…`; provider research `b64792e…`.
- MVT/DoE `e4185dc5…`, `38c4df83…`, `d27cc815…`, `6a24a19…`.
- Mesh `37dbe3eb…`, `bba0c76d…`, `d4445b5f…`.
- Tribute `eb808e2c…`, `214aa168…`, `10f7b4b…`, `223cd247…`.
- QUE/QDesk `c5d9f2f8…`, `4084d6fb…`.

The branch `cue/swarms-synthesis-20261021` is at `f8ff2c7f3b220bb7b64f834d70f3dd975f6f2d04`; the pinned prepool registry ref is `5c6c0082...`. Their histories diverge substantially. An earlier six-file, +22,558/−67 selected-to-prepool comparison lacked endpoint refs and does not represent the whole-tree diff. A Git lazy retrieval occurred during one historical lookup; the read stopped, and local object-store gaps leave exhaustive whole-history claims open.

⌖offline validation → ▶run focused suites and Swarms dry-run → ⊗no provider/model/hub call → ⤵112 tests passed in 1.65 s; dry-run status `dry_run`, 2 planned agents, 1 loop, `model=null` → ~offline checks only

## 7. Worktree and gated next phase

⌖worktree → ▶preserve all pre-existing changes → ⊗no task edits → ⤵modified `docs/ops/PROVIDER-HITL.md`, `docs/proposals/active/termux-agentic-hub/ITEMS.md`; untracked `.serena/`, `docs/ops/PROVIDER-SIGNUP-HITL.md`, `docs/ops/TERMUX-SSH-ROUTES.md` → ~checkout unchanged

⌖$0 qualification → ▶apply provider entitlement + refill/credit/allotment/cycle rules to the owner’s account and exact model → ⊗catalog presence, historical CSV rows, and unknown public status do not prove current free access → ⤵collect current source-backed entitlement, remaining quota, endpoint/inference, retry/cooldown, and telemetry evidence per candidate → ~all 98 model lanes stay `unknown`; no live candidate cleared

⌖safe order → ▶1) harvest all eligible refTemplates; 2) classify source candidates and map registry rows; 3) add current account/model qualification evidence; 4) run offline fixtures; 5) dispatch only verified $0-eligible routes; 6) stress-test within measured quota and platform ceilings; 7) reconcile resulting registry/telemetry receipts → ⊗preserve all 172 rows and current worktree → ⤵gated execution sequence → ~no live call or spend performed


⌖FLY-014 → ▶Marked mandatory; one Muse opening entry, no Hark reply. The 9,588/67/160 census is frozen (Nov 24–25 generations match; probe dated Nov 1), so it is not current eligibility.
⌖FLY-010 → ▶Separate Muse↔Hark relay; the request was sent and Manus replied, but no Muse/Hark response or FLY-010/014 response record exists. End-to-end SSH login remains unproven.
⌖runtime gate → ▶No exact provider×model $0/quota receipt or successful runtime inference receipt is available; no probes or calls were run.
⌖regression → ▶#5630 is BRR-only. #5459 has an unmerged quota-cadence admission/data-integrity lead, not a demonstrated provider/model runtime failure; exact regression remains unresolved.
⊗This omits raw DMs, device addresses, and SSH mechanics.
