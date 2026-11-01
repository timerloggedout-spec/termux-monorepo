# Repo tracking — lane × project × state × last-merge × next

Generated: `2026-11-01T11:13:10Z` · schema `repo-tracking/v1` · single-writer: `repo-tracking-collect.yml` — **do not hand-edit** (contract: [REPO-TRACKING.md](../../docs/ops/REPO-TRACKING.md))

Sources: PR feed read_at=`2026-11-01T11:13:10Z` (merged 150 · open 165) · lane-events(Neon) status=`ok` count=`4146` read_at=`2026-11-01T11:13:10Z`

Rows: 22 · by_state: active=4 · closed=1 · in-flight=10 · landed=1 · unknown=6

| domain | lane | project | state | last-merge | next |
|---|---|---|---|---|---|
| challenges | `challenge-entries` | D0 Delphi Oracle | closed | NOT_ESTABLISHED | Closed as foundation for D1 (StudySprint builds on the D0 package). |
| challenges | `challenge-entries-amd` | C11 AMD AI League / Academy | in-flight | #3044 `f44b59e32388` 2026-11-01T10:56:32Z | Routes after M3 or when builders idle |
| challenges | `challenge-entries-d1` | D1 StudySprint (Workshop to Ship) | unknown | NOT_ESTABLISHED | Nov 3 re-sync test (parity tool now in-repo: resync_parity.py); submission Nov 4 (owner ruling: submit on due day) |
| challenges | `challenge-entries-d2` | D2 Vultr Agent Rush | unknown | NOT_ESTABLISHED | Kickoff 2026-11-03T15:00Z; gate D2-NOCARD open (Vultr account before the gift-code step) |
| challenges | `challenge-entries-d3` | D3 ListingLens (Builder.io) | landed | NOT_ESTABLISHED | Nov 1 checkpoint met build-side (landed 2026-10-30); submission deadline 2026-11-09 |
| challenges | `challenge-entries-d4` | D4 Kiroween (skeleton-crew) | active | #3013 `503124a1c35f` 2026-11-01T09:34:45Z | deadline 2026-12-04T14:00:00-08:00 |
| challenges | `challenge-entries-d5` | D5 Aha! AI Builder Day | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| classifiers | `tier-1` | Tier-1 classifier engine | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| desk | `contribution-desk` | Contribution Desk + desk-feed | active | #3042 `f5c7478736be` 2026-11-01T10:36:53Z | NOT_ESTABLISHED |
| desk | `ops` | Lane-events Neon ledger | in-flight | NOT_ESTABLISHED | land/close PR #1614 — ops(actions): matrix continuation + plan scheduled lane-events aggregator for spam reduction |
| doe | `doe` | DoE campaigns (lab-1 / pilot-1 / live waves) | in-flight | #3046 `d4bbf5474a57` 2026-11-01T11:12:48Z | land/close PR #2966 — [apk-doe] A v0.2.1 |
| doe | `doe-nc1` | DoE nc-1 notation-compliance | active | #2908 `47b7aba1c339` 2026-11-01T02:41:18Z | NOT_ESTABLISHED |
| marketing | `marketing` | FB Pages MVT + challenge promo | in-flight | #2995 `6b48cb3897c5` 2026-11-01T09:12:09Z | land/close PR #3032 — fix(crg): align promotion gate with canonical master |
| marketing | `marketing-social` | Social connectors (Meta Pages / WhatsApp) | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| opportunities | `challenge-entries` | Challenge OSINT + opportunity ledger | in-flight | NOT_ESTABLISHED | land/close PR #2907 — fix: scope free-tier opportunity cost to repo work |
| providers | `providers` | Provider registry / catalog / availability | in-flight | #2924 `eda09a84bd56` 2026-11-01T03:54:43Z | land/close PR #2167 — chore(reviewer-metrics): regenerate provider x context map |
| providers | `providers-phrases` | Provider-phrases SSOT + JIT phrase layer | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| providers | `telemetry` | HindSight + Provenance telemetry ingest | in-flight | #2891 `fbd8cb72b23f` 2026-11-01T02:22:05Z | land/close PR #2914 — chore(telemetry): refresh HindSight+Provenance ingest |
| quota | `quota` | Quota registry / allocations / dispatch-tree | in-flight | #2992 `bf65498ef010` 2026-11-01T09:07:05Z | land/close PR #2757 — feat(ci): add merged branch review audit and quota engine |
| replay | `repo-replay` | Repo Replay | active | #2985 `d1de34243abf` 2026-11-01T07:34:10Z | NOT_ESTABLISHED |
| swarm | `swarm` | Swarm App + F1 token migration wave | in-flight | #3017 `102e17b3ad2c` 2026-11-01T09:49:37Z | land/close PR #1470 — feat(swarms): publish Kye parity adapters, research lanes, and remote validation |
| webdev-viz | `web-design-viz` | Fleet landing + dashboard/viz surfaces | in-flight | #3012 `93237772cac5` 2026-11-01T09:24:56Z | land/close PR #2168 — chore(dashboards): refresh surface feeds |

## Provider × DoE settings (join: DESIGN.json × treatment.instance)

Campaigns: 12 · joined: 1 · distinct instances: 8 · providers: openrouter

| campaign | provider | model@version | role | prompt (ref#sha12) | moniker | context | instance_key | plan | recorded | dispatched |
|---|---|---|---|---|---|---|---|---|---|---|
| apk-1-parallel-versioning | NOT_ESTABLISHED (design_only) | | | | | | | | | |
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
| ww-1-duckduckgo | NOT_ESTABLISHED (design_only) | | | | | | | | | |
| ww-2-brave | NOT_ESTABLISHED (design_only) | | | | | | | | | |

## Gaps (named, never synthesized)

- merged PRs unclassified by seed match rules: 86/150 (extend ops/tracking/projects.json match rules)
