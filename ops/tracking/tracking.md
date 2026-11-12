# Repo tracking — lane × project × state × last-merge × next

Generated: `2026-11-12T22:46:30Z` · schema `repo-tracking/v1` · single-writer: `repo-tracking-collect.yml` — **do not hand-edit** (contract: [REPO-TRACKING.md](../../docs/ops/REPO-TRACKING.md))

Sources: PR feed read_at=`2026-11-12T22:46:29Z` (merged 150 · open 200) · lane-events(Neon) status=`ok` count=`35204` read_at=`2026-11-12T22:46:29Z`

Rows: 22 · by_state: active=3 · closed=1 · in-flight=9 · landed=1 · unknown=8

| domain | lane | project | state | last-merge | next |
|---|---|---|---|---|---|
| challenges | `challenge-entries` | D0 Delphi Oracle | closed | NOT_ESTABLISHED | IN UPGRADE MAINTENANCE (owner correction 2026-11-03, D0 seat): the 4/4 close was the UPGRADE program's, ¬ the entry's maintenance life · production owner = Optimizations (Swarm seat) · PAIR CLOSED 2026-11-03: repo ✓ (2026-10-31) + per-entry AppID ✓ (App 5602904 · install 178358203, delphi-oracle ONLY; record PR #4659) · adoption (workflow mint steps in delphi-oracle) = follow-on PRs via Optimizations · winners capture leg #4547 unchanged |
| challenges | `challenge-entries-amd` | C11 AMD AI League / Academy | active | #4996 `ad5ee5bdc9bb` 2026-11-05T04:32:44Z | Routes after M3 or when builders idle · LANDING TARGET Nov 28 (league wall Dec 1 11:00 PT; M4 target Nov 9 stands). OWNER BUFFER RULE (2026-11-02): wall ≠ landing — desk dispatch planning consumes the LANDING TARGET; final stretch = buffer + submission mechanics only, ∅ build dispatch into it. |
| challenges | `challenge-entries-d1` | D1 StudySprint (Workshop to Ship) | in-flight | #5006 `2c4589646f44` 2026-11-05T06:42:09Z | SUBMITTED 2026-11-03 (confirmation_ref in submission) · open line to the wall: v1.0.0 cut on the richest green tree · article currency edit · frozen-state verification at the freeze · $5,000 AT_RISK (OC-003) resolves at event close |
| challenges | `challenge-entries-d2` | D2 Vultr Agent Rush | in-flight | NOT_ESTABLISHED | Queue leg CLOSED (WAF spec struck, owner direct 2026-11-01) · D2 production target DECIDED 2026-11-04 00:51 PT: B — Quarantine Browser Clerk (C1·B) · kickoff mechanics stand OUTSIDE batch @2026-11-03T15:00Z: {new repo ∧ new AppID via 7075f9c0 ∧ Vultr account + $200 gift code (gate D2-NOCARD) ∧ team} · kickoff mechanics FIRE on the decision (pick stage done → spec active) · ROUTE Δ (D2 seat, 2026-11-01): kickoff routing = DeepSeek + command-dispatch until recovery probe PASS; Jules-primary suspended ¬ deleted; ∅ silent reroute beyond this named pair · ARMS Δ (2026-11-01, manager/Swarm): DeepSeek tunnel DOWN (tunnel-unresolved skip ×2, agent ∅ invoked — runs 41301295882/41321691938) ⇒ live arms @kickoff 2026-11-03 = command-dispatch ALONE {Jules DOWN · Gemini OUT · DeepSeek DOWN}; restoration ⇒ desk flags D2 seat same-turn · LANDING TARGET Nov 7 (wall: submission ≤ Nov 8 15:00 PT). OWNER BUFFER RULE (2026-11-02): wall ≠ landing — desk dispatch planning consumes the LANDING TARGET; final stretch = buffer + submission mechanics only, ∅ build dispatch into it. |
| challenges | `challenge-entries-d3` | D3 ListingLens (Builder.io) | landed | #5251 `860582e0d0b5` 2026-11-12T15:23:47Z | Nov 1 checkpoint met build-side (landed 2026-10-30); submission deadline 2026-11-09 · ROUTE Δ (D3 seat, 2026-11-01): batch B1–B5 trigger route = DeepSeek + command-dispatch until recovery probe PASS (Jules DOWN (created 3/completed 0/errored 3, Swarm 2026-11-01; opportunistic OFF) ∧ Gemini-CLI build leg OUT); producer-naming req unchanged · LANDING TARGET Nov 8 (wall: submission Nov 9 23:59 PT). OWNER BUFFER RULE (2026-11-02): wall ≠ landing — desk dispatch planning consumes the LANDING TARGET; final stretch = buffer + submission mechanics only, ∅ build dispatch into it. |
| challenges | `challenge-entries-d4` | D4 Kiroween (skeleton-crew) | unknown | NOT_ESTABLISHED | BATCH QUEUED (owner batch order 2026-11-01, priority ↑) · dispatch AT build window >2026-11-08, ∅ fire before window · AppID owed at build start via AppID lane 7075f9c0 (owner rule 2026-11-01) — flagged for dispatch · gate D4-ACCOUNTS still open (Kiro ID, ≤2026-12-01T12:00PT) · submit 2026-12-04 14:00 PT · PROVIDER Δ (2026-11-01): Jules DOWN (created 3/completed 0/errored 3, Swarm 2026-11-01; opportunistic OFF) + Gemini build leg OUT (Swarm via manager) — at build window, route re-selects per manager rule {DeepSeek + command-dispatch} unless recovery probe PASS first · LANDING TARGET Dec 2 (wall: submit Dec 4 14:00 PT). OWNER BUFFER RULE (2026-11-02): wall ≠ landing — desk dispatch planning consumes the LANDING TARGET; final stretch = buffer + submission mechanics only, ∅ build dispatch into it. |
| challenges | `challenge-entries-d5` | D5 Aha! AI Builder Day | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| classifiers | `tier-1` | Tier-1 classifier engine | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| desk | `contribution-desk` | Contribution Desk + desk-feed | active | #5215 `25215ce21f8c` 2026-11-12T10:36:15Z | NOT_ESTABLISHED |
| desk | `ops` | Lane-events Neon ledger | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| doe | `doe` | DoE campaigns (lab-1 / pilot-1 / live waves) | in-flight | #5191 `ba12d157e732` 2026-11-12T04:42:17Z | land/close PR #5198 — docs(doe): establish governed free-inference endpoint tournament order |
| doe | `doe-nc1` | DoE nc-1 notation-compliance | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| marketing | `marketing` | FB Pages MVT + challenge promo | active | #5208 `9f75e4263357` 2026-11-12T13:17:02Z | NOT_ESTABLISHED |
| marketing | `marketing-social` | Social connectors (Meta Pages / WhatsApp) | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| opportunities | `challenge-entries` | Challenge OSINT + opportunity ledger | in-flight | #5110 `0ee3c56df289` 2026-11-10T12:41:41Z | land/close PR #2235 — chore(osint): refresh coverage + page snapshots |
| providers | `providers` | Provider registry / catalog / availability | in-flight | #5020 `a07d479c493f` 2026-11-06T01:54:38Z | land/close PR #3916 — chore(reviewer-metrics): regenerate provider x context map |
| providers | `providers-phrases` | Provider-phrases SSOT + JIT phrase layer | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| providers | `telemetry` | HindSight + Provenance telemetry ingest | in-flight | #5069 `a60dd2b068f5` 2026-11-07T19:30:33Z | land/close PR #3890 — chore(telemetry): refresh HindSight+Provenance ingest |
| quota | `quota` | Quota registry / allocations / dispatch-tree | in-flight | #5248 `f81db0c2cdf5` 2026-11-12T15:07:44Z | land/close PR #5258 — feat(ops): #5160 autoQuotaCadence — deterministic pool generation + cadence derivation |
| replay | `repo-replay` | Repo Replay | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| swarm | `swarm` | Swarm App + F1 token migration wave | in-flight | #5238 `1b573fde5351` 2026-11-12T14:41:48Z | land/close PR #5222 — docs(architecture): reconcile swarm routing control planes |
| webdev-viz | `web-design-viz` | Fleet landing + dashboard/viz surfaces | in-flight | #5130 `748b3ef6a18c` 2026-11-10T14:26:48Z | land/close PR #4069 — chore(dashboards): refresh surface feeds |

## Provider × DoE settings (join: DESIGN.json × treatment.instance)

Campaigns: 18 · joined: 2 · distinct instances: 11 · providers: Muse, cohere, openrouter, sealion

| campaign | provider | model@version | role | prompt (ref#sha12) | moniker | context | instance_key | plan | recorded | dispatched |
|---|---|---|---|---|---|---|---|---|---|---|
| apk-1-parallel-versioning | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| bf-1-backfill-methods | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| cb-1-chronomancer-emission | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| cmp-register | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| game-development-specialist-evolution | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| lab-1-prompt-x-model-x-role | openrouter | meta-llama/llama-3.1-8b-instruct:free | reviewer | experiments/doe/lab-1-prompt-x-model-x-role/prompts/prompt-a.md (+ role line: reviewer)#a8f522b64adf | doe-expert | lab-1-prompt-x-model-x-role | `7f5083a90dad…` | 8 | 0 | 0 |
| lab-1-prompt-x-model-x-role | openrouter | meta-llama/llama-3.1-8b-instruct:free | reviewer | experiments/doe/lab-1-prompt-x-model-x-role/prompts/prompt-b.md (+ role line: reviewer)#1a3c8af80ddd | doe-expert | lab-1-prompt-x-model-x-role | `e42a430c5555…` | 8 | 0 | 0 |
| lab-1-prompt-x-model-x-role | openrouter | meta-llama/llama-3.1-8b-instruct:free | triage | experiments/doe/lab-1-prompt-x-model-x-role/prompts/prompt-a.md (+ role line: triage)#6dbc83fe4a09 | doe-expert | lab-1-prompt-x-model-x-role | `2121b5f4c20f…` | 8 | 0 | 0 |
| lab-1-prompt-x-model-x-role | openrouter | meta-llama/llama-3.1-8b-instruct:free | triage | experiments/doe/lab-1-prompt-x-model-x-role/prompts/prompt-b.md (+ role line: triage)#63ee8aad657b | doe-expert | lab-1-prompt-x-model-x-role | `e2f6199c75a3…` | 8 | 0 | 0 |
| lab-1-prompt-x-model-x-role | openrouter | openai/gpt-4o-mini | reviewer | experiments/doe/lab-1-prompt-x-model-x-role/prompts/prompt-a.md (+ role line: reviewer)#a8f522b64adf | doe-expert | lab-1-prompt-x-model-x-role | `cb4a2e08ff87…` | 8 | 0 | 0 |
| lab-1-prompt-x-model-x-role | openrouter | openai/gpt-4o-mini | reviewer | experiments/doe/lab-1-prompt-x-model-x-role/prompts/prompt-b.md (+ role line: reviewer)#1a3c8af80ddd | doe-expert | lab-1-prompt-x-model-x-role | `cb4644f74a52…` | 8 | 0 | 0 |
| lab-1-prompt-x-model-x-role | openrouter | openai/gpt-4o-mini | triage | experiments/doe/lab-1-prompt-x-model-x-role/prompts/prompt-a.md (+ role line: triage)#6dbc83fe4a09 | doe-expert | lab-1-prompt-x-model-x-role | `2889490a8da8…` | 8 | 0 | 0 |
| lab-1-prompt-x-model-x-role | openrouter | openai/gpt-4o-mini | triage | experiments/doe/lab-1-prompt-x-model-x-role/prompts/prompt-b.md (+ role line: triage)#63ee8aad657b | doe-expert | lab-1-prompt-x-model-x-role | `990dfd2fd245…` | 8 | 0 | 0 |
| live-1-wave-framing | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| live-2-prlane-tuning | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| live-3-phrases-deepseek | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| live-4-dispatch-framing | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| nc-1-notation-compliance | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| phone-1-mcp-background-control | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| pilot-1-context-routing-x-compression | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| routed-dispatch | Muse | Muse Spark 1.3 | builder | docs/ops/SWARM-OPTIMIZATION-ASSURANCE.md#7d7481cc3c52 | optimizations-assurance | fan-out wiring completion set (build-class) | `1a60e8329fb6…` | 0 | 3 | 0 |
| routed-dispatch | cohere | c4ai-aya-expanse-32b | builder | scripts/certifications/run_unit.py#c34eb7290dfe | optimizations-assurance | certifications-unit l1-relational-databases-v9/061 | `7434577f5900…` | 0 | 1 | 0 |
| routed-dispatch | sealion | aisingapore/Llama-SEA-LION-v3-70B-IT | builder | scripts/certifications/run_unit.py#c34eb7290dfe | optimizations-assurance | FCC L1 M5 theory batch (cert-unit workflow dispatch) | `7e20822af41d…` | 0 | 3 | 0 |
| util-1-provider-rotation | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| ww-1-duckduckgo | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| ww-2-brave | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| ww-3-you-com | NOT_ESTABLISHED (design_only) | | | | | | | | | |

## Gaps (named, never synthesized)

- merged PRs unclassified by seed match rules: 120/150 (extend ops/tracking/projects.json match rules)
