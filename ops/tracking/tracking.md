# Repo tracking — lane × project × state × last-merge × next

Generated: `2026-11-02T15:31:23Z` · schema `repo-tracking/v1` · single-writer: `repo-tracking-collect.yml` — **do not hand-edit** (contract: [REPO-TRACKING.md](../../docs/ops/REPO-TRACKING.md))

Sources: PR feed read_at=`2026-11-02T15:31:18Z` (merged 150 · open 181) · lane-events(Neon) status=`ok` count=`8983` read_at=`2026-11-02T15:31:18Z`

Rows: 22 · by_state: active=1 · closed=1 · in-flight=11 · landed=1 · unknown=8

| domain | lane | project | state | last-merge | next |
|---|---|---|---|---|---|
| challenges | `challenge-entries` | D0 Delphi Oracle | closed | NOT_ESTABLISHED | Closed as foundation for D1 (StudySprint builds on the D0 package). |
| challenges | `challenge-entries-amd` | C11 AMD AI League / Academy | in-flight | NOT_ESTABLISHED | Routes after M3 or when builders idle · LANDING TARGET Nov 28 (league wall Dec 1 11:00 PT; M4 target Nov 9 stands). OWNER BUFFER RULE (2026-11-02): wall ≠ landing — desk dispatch planning consumes the LANDING TARGET; final stretch = buffer + submission mechanics only, ∅ build dispatch into it. |
| challenges | `challenge-entries-d1` | D1 StudySprint (Workshop to Ship) | unknown | NOT_ESTABLISHED | Reader MERGED+synced · SR: system (balanced) · Notes pass: DeepSeek arm tunnel-DOWN ×2 skips ⇒ task submitted to system (issue #3215); tunnel escalated ⇒ Swarm · freeze-hold submission 2026-11-04 23:59 PT · TEMPLATE TRIGGER: build requirement filed to system as #3577 (form + issues[opened] consumer per owner directive); on landing desk re-files {notes #3215 · SR #3050} in the new form same-turn · RFPs FILED (owner order): #3695 RFP-D1-1 impact copy (pre-Nov 4) · #3696 RFP-D1-2 originality copy (pre-Nov 4) · #3697 RFP-D1-3 reading pipeline §1b (post-Nov 4) · #3698 RFP-D1-4 multi-course+countdown+.ics (post-Nov 4) — Delphi gate evaluation; outputs ⇒ D1 verification · BUFFER TARGET (owner via main, 2026-11-02): #3695/#3696 evaluations must return in time for copy landed + D1-verified by the **Nov 3 re-sync**; final ~24h pre-deadline = buffer only, ∅ deadline-day copy landings; desk tracks dispatch timing vs Nov 3 ¬ Nov 4 · LANDING TARGET Nov 3 (wall Nov 4 23:59 PT). OWNER BUFFER RULE (2026-11-02): wall ≠ landing — desk dispatch planning consumes the LANDING TARGET; final stretch = buffer + submission mechanics only, ∅ build dispatch into it. · EVALUATIONS RETURNED (Delphi, desk-verified on-issue): #3695 ∧ #3696 both effective 8.54/25, parked/Backlog, converged 1 round, recheck >2026-12-02 — parked = quota-surface vocabulary, ∅ gate on the copy PRs (evaluator read via D1 seat); EXECUTION proceeding: RFP-D1-1 + RFP-D1-2 copy folds ride the copy landing path alongside notes #3215; target = landed + D1-verified by Nov 3 re-sync |
| challenges | `challenge-entries-d2` | D2 Vultr Agent Rush | unknown | NOT_ESTABLISHED | Queue leg CLOSED (WAF spec struck, owner direct 2026-11-01) · D2 production target ∅ until owner pick · kickoff mechanics stand OUTSIDE batch @2026-11-03T15:00Z: {new repo ∧ new AppID via 7075f9c0 ∧ Vultr account + $200 gift code (gate D2-NOCARD) ∧ team} · ∅ fire pre-pick · ROUTE Δ (D2 seat, 2026-11-01): kickoff routing = DeepSeek + command-dispatch until recovery probe PASS; Jules-primary suspended ¬ deleted; ∅ silent reroute beyond this named pair · ARMS Δ (2026-11-01, manager/Swarm): DeepSeek tunnel DOWN (tunnel-unresolved skip ×2, agent ∅ invoked — runs 41301295882/41321691938) ⇒ live arms @kickoff 2026-11-03 = command-dispatch ALONE {Jules DOWN · Gemini OUT · DeepSeek DOWN}; restoration ⇒ desk flags D2 seat same-turn · LANDING TARGET Nov 7 (wall: submission ≤ Nov 8 15:00 PT). OWNER BUFFER RULE (2026-11-02): wall ≠ landing — desk dispatch planning consumes the LANDING TARGET; final stretch = buffer + submission mechanics only, ∅ build dispatch into it. |
| challenges | `challenge-entries-d3` | D3 ListingLens (Builder.io) | landed | NOT_ESTABLISHED | Nov 1 checkpoint met build-side (landed 2026-10-30); submission deadline 2026-11-09 · ROUTE Δ (D3 seat, 2026-11-01): batch B1–B5 trigger route = DeepSeek + command-dispatch until recovery probe PASS (Jules DOWN (created 3/completed 0/errored 3, Swarm 2026-11-01; opportunistic OFF) ∧ Gemini-CLI build leg OUT); producer-naming req unchanged · LANDING TARGET Nov 8 (wall: submission Nov 9 23:59 PT). OWNER BUFFER RULE (2026-11-02): wall ≠ landing — desk dispatch planning consumes the LANDING TARGET; final stretch = buffer + submission mechanics only, ∅ build dispatch into it. |
| challenges | `challenge-entries-d4` | D4 Kiroween (skeleton-crew) | unknown | NOT_ESTABLISHED | BATCH QUEUED (owner batch order 2026-11-01, priority ↑) · dispatch AT build window >2026-11-08, ∅ fire before window · AppID owed at build start via AppID lane 7075f9c0 (owner rule 2026-11-01) — flagged for dispatch · gate D4-ACCOUNTS still open (Kiro ID, ≤2026-12-01T12:00PT) · submit 2026-12-04 14:00 PT · PROVIDER Δ (2026-11-01): Jules DOWN (created 3/completed 0/errored 3, Swarm 2026-11-01; opportunistic OFF) + Gemini build leg OUT (Swarm via manager) — at build window, route re-selects per manager rule {DeepSeek + command-dispatch} unless recovery probe PASS first · LANDING TARGET Dec 2 (wall: submit Dec 4 14:00 PT). OWNER BUFFER RULE (2026-11-02): wall ≠ landing — desk dispatch planning consumes the LANDING TARGET; final stretch = buffer + submission mechanics only, ∅ build dispatch into it. |
| challenges | `challenge-entries-d5` | D5 Aha! AI Builder Day | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| classifiers | `tier-1` | Tier-1 classifier engine | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| desk | `contribution-desk` | Contribution Desk + desk-feed | in-flight | #3899 `0a223bddacb3` 2026-11-02T13:55:09Z | land/close PR #3063 — viz(desk): adopt desk-feed v1.3 (dispatch.provider_catalog) — fixture + schema pins |
| desk | `ops` | Lane-events Neon ledger | in-flight | NOT_ESTABLISHED | land/close PR #1614 — ops(actions): matrix continuation + plan scheduled lane-events aggregator for spam reduction |
| doe | `doe` | DoE campaigns (lab-1 / pilot-1 / live waves) | in-flight | #3865 `7b416c374c09` 2026-11-02T13:17:49Z | land/close PR #2966 — [apk-doe] A v0.2.1 |
| doe | `doe-nc1` | DoE nc-1 notation-compliance | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| marketing | `marketing` | FB Pages MVT + challenge promo | in-flight | NOT_ESTABLISHED | land/close PR #3032 — fix(crg): align promotion gate with canonical master |
| marketing | `marketing-social` | Social connectors (Meta Pages / WhatsApp) | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| opportunities | `challenge-entries` | Challenge OSINT + opportunity ledger | in-flight | NOT_ESTABLISHED | land/close PR #2907 — fix: scope free-tier opportunity cost to repo work |
| providers | `providers` | Provider registry / catalog / availability | in-flight | #2167 `6d24b733af85` 2026-11-02T13:52:46Z | land/close PR #3916 — chore(reviewer-metrics): regenerate provider x context map |
| providers | `providers-phrases` | Provider-phrases SSOT + JIT phrase layer | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| providers | `telemetry` | HindSight + Provenance telemetry ingest | in-flight | #3920 `a9841cfed69f` 2026-11-02T13:56:58Z | land/close PR #3890 — chore(telemetry): refresh HindSight+Provenance ingest |
| quota | `quota` | Quota registry / allocations / dispatch-tree | in-flight | #3928 `6635afbb8572` 2026-11-02T14:11:20Z | land/close PR #1441 — feat(triage): reconcile official quota before dispatch |
| replay | `repo-replay` | Repo Replay | active | #3896 `7b22048ce8ca` 2026-11-02T13:46:27Z | NOT_ESTABLISHED |
| swarm | `swarm` | Swarm App + F1 token migration wave | in-flight | NOT_ESTABLISHED | land/close PR #3437 — feat(dispatch): wire gemini-invoke to the stamp fan-out |
| webdev-viz | `web-design-viz` | Fleet landing + dashboard/viz surfaces | in-flight | #3937 `e7f0a4dfecbd` 2026-11-02T14:20:07Z | land/close PR #3939 — chore(dashboards): refresh surface feeds |

## Provider × DoE settings (join: DESIGN.json × treatment.instance)

Campaigns: 16 · joined: 2 · distinct instances: 11 · providers: Muse, cohere, openrouter, sealion

| campaign | provider | model@version | role | prompt (ref#sha12) | moniker | context | instance_key | plan | recorded | dispatched |
|---|---|---|---|---|---|---|---|---|---|---|
| apk-1-parallel-versioning | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| bf-1-backfill-methods | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| cb-1-chronomancer-emission | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| cmp-register | NOT_ESTABLISHED (design_only) | | | | | | | | | |
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
| pilot-1-context-routing-x-compression | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| routed-dispatch | Muse | Muse Spark 1.3 | builder | docs/ops/SWARM-OPTIMIZATION-ASSURANCE.md#7d7481cc3c52 | optimizations-assurance | fan-out wiring completion set (build-class) | `1a60e8329fb6…` | 0 | 3 | 0 |
| routed-dispatch | cohere | c4ai-aya-expanse-32b | builder | scripts/certifications/run_unit.py#c34eb7290dfe | optimizations-assurance | certifications-unit l1-relational-databases-v9/061 | `7434577f5900…` | 0 | 1 | 0 |
| routed-dispatch | sealion | aisingapore/Llama-SEA-LION-v3-70B-IT | builder | scripts/certifications/run_unit.py#c34eb7290dfe | optimizations-assurance | FCC L1 M5 theory batch (cert-unit workflow dispatch) | `7e20822af41d…` | 0 | 3 | 0 |
| util-1-provider-rotation | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| ww-1-duckduckgo | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| ww-2-brave | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| ww-3-you-com | NOT_ESTABLISHED (design_only) | | | | | | | | | |

## Gaps (named, never synthesized)

- merged PRs unclassified by seed match rules: 110/150 (extend ops/tracking/projects.json match rules)
