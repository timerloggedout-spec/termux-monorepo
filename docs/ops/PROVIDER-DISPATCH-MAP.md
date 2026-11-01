# Provider dispatch map — complete catalog

**Owner order 2026-11-01 (fix seat `5f3a3217`): Desk dispatch resolution = COMPLETE catalog.**
Machine-readable source of record: `ops/challenge/desk-feed.json` → `dispatch.provider_catalog`
(schema `desk-feed/v1.3`). This doc is the human mirror; the feed wins on any drift.

## Why

Desk dispatch was a 4-lane funnel {Jules, Gemini, DeepSeek, command-dispatch} against a bench of
164 registry services (91 model records / 89 distinct model providers / 110 distinct providers
across all lanes, `ops/quota/registry.json` blob `0f892261` @master `ff76abef`, census
2026-11-01T11:22Z) and 18 provider workflows in-repo. Already-triggered surfaces (DeepAgent
bridge, provider-batch, CodeRabbit, Devin, Qodo, …) completed work the funnel never routed to.
The funnel is retired: every dispatch-capable surface is a named lane below, honestly classed.

## Classes

- **proven** — triggered ∧ completed, evidence cited per lane (run id / PR / session).
- **wired-unproven** — wired in-repo, no successful run yet. Gets bounded, DoE-stamped proof
  dispatches instead of permanent exile; a first success promotes it at the next feed refresh.
- **triggerable** — a live trigger exists (workflow_dispatch / schedule / event) but the surface
  is support-class or has never fired.
- **inference-only** — registry model records with no build-dispatch wiring of their own.
  Reachable for inference/eval tasks via a named arm (`provider-batch`, `provider-availability`,
  `openrouter-free-counter-batch-probe`); promotion path = `cadence-provider-onboarding` + one
  stamped proof dispatch. The full 91 record ids + 89 distinct providers are enumerated in the
  feed's `dispatch.provider_catalog.inference_only` — nothing is silently dropped from the bench.

## Proven lanes (census 2026-11-01T11:22Z, PAT API firsthand)

| Lane | Task classes | Surface | Evidence |
|---|---|---|---|
| Jules | build, fix | `agent-jules-on-issues.yml` + handoff + review-auto | sessions 17326020844735872479 (PR #2635) + 7007935780300107338 (PR #2731); last success 41296280415 |
| Gemini dispatch | build, feature, invoke | `gemini-dispatch.yml` | D1 SR run 41301369671 ✓ (issue #3050, event = issues); last success 41301486059. Trigger = issues / issue_comment / PR events (@gemini-cli) — ∅ workflow_dispatch (#2734 open) |
| Gemini after-peers | review (2nd pass) | `gemini-after-peers.yml` | 1,269 runs; last success 41299982052 |
| DeepSeek termux-agent | fix, build | `deepseek-termux-agent.yml` | D1 fix-pass run 41301295882 ✓ |
| DeepSeek CI | invoke, review | `deepseek-ci.yml` | last success 41301485914 |
| DeepAgent bridge | device, task | `deepcli-agent-bridge.yml` | 158 runs; last success 39989289180 (2026-10-23). Device leg NOT_ESTABLISHED (2026-11-01 split: device steps skipped, reachable=false) — workflow-level dispatch proven, device execution unverified; verify at PR level |
| DeepAgent task | task, build | `deepagent-task.yml` | first success 41301564332 in the widening window (was 0 runs; workflow-level — device steps skipped, device execution NOT_ESTABLISHED; stamp #2735) |
| provider-batch | inference, batch, eval | `provider-batch.yml` | 250 runs; last success 40710434190 (2026-10-28); latest-100 mixed ⇒ verify per dispatch. **DISPATCH HELD per issue #2672 until contracts job green** (arm proven, dispatch suspended) |
| provider-availability | probe, catalog | `provider-availability.yml` | 93 runs; last success 40704824602 |
| provider-command-dispatch | fix, review | `provider-command-dispatch.yml` + command library | 1 run ✓ 39170909023 (2026-10-18, n=1 stale — re-proof on next use) |
| CodeRabbit | review, fix | command library + peer-review-orchestrator | default required reviewer; triggered today (Swarm census) |
| Qodo | review | command library + peer-review-orchestrator | opt-in; triggered today (Swarm census) |
| Devin | review, fix, wiki | `reconcile-devin-wiki-access.yml` + command library | wiki 778 runs, last success 41301566618; review-trigger today NOT_ESTABLISHED (Swarm census) |
| CellCog | review | `cellcog-review.yml` | 30,220 runs; last success 41301485944 |
| Peer-review orchestrator | review routing | `peer-review-orchestrator.yml` | last success 41301622846 |
| ECC Tools | review, audit ops | `agent-ecc-tools-ops.yml` | last success 41301536037 |
| Scout / Delphi | build, verify | owner-named lane route | D0 of record (PR #1702; delphi-oracle @393e1f4b) |

## Registry bench classes (Quota capability map, firsthand @master 2026-11-01)

89 distinct model-lane providers = **proven 2 + wired-unproven 22 + triggerable 2 + inference-only 63**:

- **Proven (2):** `google` (Gemini router/after-peers, key-live) · `openrouter` (production invoke
  legs; free layer active, paid balance $0.00).
- **Wired-unproven (22)** via provider-batch (surface: 249 runs / 138 successes; per-provider
  invoke NOT_ESTABLISHED): key-live {cohere, huggingface, llm7, routeway, sambanova, siliconflow,
  unorouter, zai} · no-credential {cerebras, kilo, mistral, modelscope, ovhcloud, requesty,
  typhoon, xfyun} · egress-blocked {groq, xkiro} · route-dead {aion, sealion} · flags {cloudflare
  verify-scope, nvidia auth-unproven}. Promotion = one named single-provider batch dispatch each
  (after flag resolution; batch currently HELD per #2672). Gate-state (Quota amendment, Swarm
  firsthand): the 7 key-live members {cohere, sambanova, zai, llm7, routeway, unorouter,
  siliconflow} are `blocked-by-#2672` — observation jobs gate on the red `contracts` job
  (run 41301473553 job split), so the batch yields ∅ operational evidence regardless of
  provider health. Blocker = the gate, ¬ the providers. Reverse gap: batch member `ollama`
  has ∅ registry model row.
- **Triggerable (2):** `felo`, `omni` — catalog endpoints exist, ∅ batch admission/wiring.
- **Inference-only (63):** `github` (GitHub Models), `meta` (llama_api RETIRED, do-not-route),
  gpt4free family, + 60 `g4f/*` upstreams (duplicates route via native entries; media/search
  upstreams need a media/search batch variant, ¬ chat batch).

DeepSeek note: ∅ distinct model-lane provider row (only `g4f/DeepSeek`); its lanes are the
ci-lane dispatch records.

## Wired-unproven

| Lane | Surface | State |
|---|---|---|
| gemini-invoke | `gemini-invoke.yml` | `workflow_call` via gemini-dispatch; invoke job SUCCESS in run 41302651335 (2026-11-01, production issue #3077) — PROVEN |
| gemini-triage | `gemini-triage.yml` | `workflow_call` via gemini-dispatch; triage job SUCCESS in runs 41301369671 + 41302644454 (2026-11-01) — PROVEN |
| gemini-review | `gemini-review.yml` | `workflow_call` via gemini-dispatch; review job SUCCESS in run 41303090873 (2026-11-01, PR #3080) — PROVEN (standalone history: 26 runs, 0 successes to 2026-08-20) |

## Triggerable (support / never fired)

`gemini-interactions-smoke` (dispatch, 0 runs) · `openrouter-free-counter-batch-probe`
(dispatch, 0 runs) · `cadence-provider-onboarding` (dispatch+schedule, 8 runs, last success
2026-10-30 — the promotion arm) · `provider-recon-compound` (57 runs, last success 2026-10-27) ·
`quota-dispatch-tree` (51 runs, last success 2026-11-01 — routing support, not a build lane).

## App layer (identity, not inference)

- Record: `ops/github-apps/PROCESS.json` (blob efbc50c26ecd; bundle record PR #2479) +
  `docs/ops/GITHUB-APP-PROCESS.md`.
- Code wired into the Desk: `scripts/github/github_app_telemetry.py` +
  `scripts/github/publish_github_app_telemetry.py` (+ tests), runner
  `.github/workflows/github-app-telemetry.yml`, doc `docs/ops/GITHUB-APP-FLEET-TELEMETRY.md`;
  output `ops/github-apps/observations/**` (2026-10-30 -> 2026-11-01) feeding desk-feed.
- Telemetry identity: **Termux Fleet Collector — App 5535733** (mints via vars
  TERMUX_FLEET_COLLECTOR_APP_ID / secret TERMUX_FLEET_COLLECTOR_PRIVATE_KEY, SEC-03).
- Slate: Collector 5535733 · Publisher 5537873 · Reviewer 5539430 · Gate 5539499 ·
  Lifecycle 5539639 · Swarm 5560920 · CrossReference 5564430 · RepoStory 5565297 (repo-story only).
- Fleet APK is NOT a 9th app (two recons, 2026-11-01: no bare-Fleet GitHub App ever existed;
  its keystore was never provisioned — v0.1.0 shipped ephemeral-debug).

## Batch outcomes — BATCH ALL TRIGGERABLE (owner order 2026-11-01)

All 5 triggerable + 3 wired-unproven lanes fired at production work; classes updated on evidence:

- **Proven by the batch:** `openrouter-free-counter-batch-probe` (run 41302260322 success) ·
  `quota-dispatch-tree` (dispatch run 41302083313 success) · `cadence-provider-onboarding`
  (first fire 41302262147 FAILED on meta-unmapped drift; meta acknowledged in 44ad26f9; run
  41302538342 success) · `gemini-triage` (triage job success, dispatch runs 41301369671 +
  41302644454) · `gemini-invoke` (invoke job success, dispatch run 41302651335; production
  spec = issue #3077).
- **Fired, failed + diagnosis (class unchanged):** `gemini-interactions-smoke` — runs
  41302258314 + 41302303592 FAILURE; log-verified: Interactions API probe HTTP 404 with
  GEMINI_API_KEY configured (route/model not found, ¬ credential failure) ·
  `provider-recon-compound` — batch runs FAILED (403 layer) but RESTORED: run 41304907142
  FULL SUCCESS {contracts+collect+publish} 2026-11-01T12:06Z. Root causes: (1) parser grammar
  vs upstream KeylessDecisionProvider registrations (fix #3085); (2) transient egress/rate
  403 during the batch window (error-surfacing #3096 -> #3094; token pin #3110) => PROVEN.
- **Review leg:** `gemini-review` — first attempt on PR #3079 (comment 6557428651) produced
  no dispatch run (PR merged mid-storm 11:39:39Z); re-fired on PR #3080 (comment 6557463507)
  ⇒ dispatch run 41303090873, review job SUCCESS ⇒ PROVEN.

## Inference wiring — re-based (owner class correction 2026-11-01)

The inference bench IS the batch universe. Wiring classes are computed on **wired INVOKE
routes for inference providers only**; review/command surfaces (Qodo, Devin, CodeRabbit,
peer-review lanes, gemini review/triage legs) are excluded from this batch — a triggerable
workflow lane is not a wired provider. Structural form: every lane now carries
  `batch_scope` {inference-bench 9 · excluded-review-command 10 · build-or-support 6} and
  batch accounting reads `inference_wiring` only (Desk NOTE stamp = PR #3111). #2672 gate:
  contracts run 41303413675 FAILED 2026-11-01T11:47Z — batch observation still gated.

- **Wired-invoke: 17 / 89** — invoke endpoint present in code: provider-batch
  `research_providers` ENDPOINTS (14: aion, cerebras, gemini→google, groq, huggingface, kilo,
  llm7, mistral, modelscope, nvidia, ovhcloud, sambanova, siliconflow, zai) ∪ catalog
  ENDPOINTS (16, adds felo, omni, openrouter). Blockers still apply per provider (groq =
  Actions egress; 5 of the batch set carry gate-state blocked-by-#2672; cerebras/kilo/
  mistral/modelscope/ovhcloud = no credential; aion = route-dead claim; nvidia = auth
  unproven; openrouter = free layer only).
- **Not wired: 72 / 89** — no invoke endpoint in code (registry/roster presence, hub route
  claims, or batch membership without an endpoint key). Each carries a blocker of record in
  `dispatch.provider_catalog.inference_wiring.not_wired`. Wiring target (owner escalation,
  Swarm owns): an invoke route per provider, or the blocker stands as the record.
- The lane table above keeps its own classes for *dispatch lanes*; it no longer says
  anything about inference-provider wiring.

## Rotation rule (bench-wide)

No provider takes 2 consecutive dispatches for the same entry, across **all** catalog lanes
(supersedes the 2026-10-31 rule, which capped repeats inside the 4-lane funnel only).
Selection = task-fit across the full catalog: proven lanes carry production work;
wired-unproven / triggerable surfaces get bounded proof dispatches; inference-only providers
are selectable via their named arm. Every dispatch stamps provider + surface + selection
reason + session/run id — no stamp ⇒ no dispatch (telemetry gate, 2026-10-30).

**D1 re-selection (2026-11-01):** DeepSeek fix-pass (run 41301295882 ✓) ∧ Gemini SR
(issue #3050, run 41301369671 ✓) stand — distinct providers, rotation-valid, already fired.
Next D1 dispatch ⇒ a proven lane outside {DeepSeek, Gemini} for its task class, reason stamped.

## Inference availability mapping — the crux (owner emphasis 2026-11-01)

Lane names are not the resolution; **invocability** is. Per-record map for all 91 model-lane
registry records lives in the feed at `dispatch.provider_catalog.inference_availability.records`
(fields: id, provider, class, availability_probe, batch, inference_route, registry_live_field).

- **Availability surface** = `provider-availability.yml` → `scripts/provider_availability_probe.py`
  → `scripts/provider_model_catalog.py` (ENDPOINTS 16: aion, cerebras, felo, gemini, groq,
  huggingface, kilo, llm7, mistral, modelscope, nvidia, omni, openrouter, ovhcloud, sambanova,
  siliconflow; SECRETS 17 adds zai = secret-mapped, ∅ catalog endpoint).
- **Semantics (the surface's own schema):** it proves `credential_present` + `catalog_ok` only —
  `inference_ok` is false for scheduled probes. Bounded inference legs exist for exactly 2:
  openrouter (real inference call on credential+catalog ok) ∧ gemini (models list +
  generateContent-capability check). Coverage ≠ inference proof for the other 14.
- **Batch surface** = `llm_api_hub/server/research_providers.py` ENDPOINTS (14 provider keys:
  aion, cerebras, gemini, groq, huggingface, kilo, llm7, mistral, modelscope, nvidia, ovhcloud,
  sambanova, siliconflow, zai) — the invoke route for the wired-unproven class; currently
  HELD per #2672.
- **Summary over 91 records:** by class {'wired-unproven': 22, 'triggerable': 2, 'inference-only': 65, 'proven': 2}; availability-covered
  16 records (+1 secret-only,
  74 not covered); batch endpoint-wired 14.
  The remaining records (g4f family etc.) have **no wired invocable route** — inference-only
  until the promotion wiring lands; they are named per-record in the feed, not rounded up.

## Refresh

Cross-ref: Swarm widened rotation of record = SWARM doc §15 (PR #3056). Batch invoke keys live today: cohere / sambanova / zai / llm7 / routeway / unorouter / siliconflow (groq excluded, Actions egress).

Desk single-writer refresh pattern (feed PR). Re-census registry + workflow runs at each
refresh; a lane's class changes only on cited run/PR evidence, never on wiring alone.
