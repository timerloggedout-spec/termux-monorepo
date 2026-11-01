# Repo tracking — lane × project × state × last-merge × next

Generated: `2026-11-01T04:28:22Z` · schema `repo-tracking/v1` · single-writer: `repo-tracking-collect.yml` — **do not hand-edit** (contract: [REPO-TRACKING.md](../../docs/ops/REPO-TRACKING.md))

Sources: PR feed read_at=`2026-11-01T04:28:22Z` (merged 150 · open 156) · lane-events(Neon) status=`ok` count=`3005` read_at=`2026-11-01T04:28:22Z`

Rows: 22 · by_state: active=2 · closed=1 · in-flight=9 · landed=1 · unknown=9

| domain | lane | project | state | last-merge | next |
|---|---|---|---|---|---|
| challenges | `challenge-entries` | D0 Delphi Oracle | closed | NOT_ESTABLISHED | Closed as foundation for D1 (StudySprint builds on the D0 package). |
| challenges | `challenge-entries-amd` | C11 AMD AI League / Academy | in-flight | NOT_ESTABLISHED | Routes after M3 or when builders idle |
| challenges | `challenge-entries-d1` | D1 StudySprint (Workshop to Ship) | unknown | NOT_ESTABLISHED | Nov 3 re-sync test (parity tool now in-repo: resync_parity.py); submission Nov 4 (owner ruling: submit on due day) |
| challenges | `challenge-entries-d2` | D2 Vultr Agent Rush | unknown | NOT_ESTABLISHED | Kickoff 2026-11-03T15:00Z; gate D2-NOCARD open (Vultr account before the gift-code step) |
| challenges | `challenge-entries-d3` | D3 ListingLens (Builder.io) | landed | NOT_ESTABLISHED | Nov 1 checkpoint met build-side (landed 2026-10-30); submission deadline 2026-11-09 |
| challenges | `challenge-entries-d4` | D4 Kiroween (skeleton-crew) | unknown | NOT_ESTABLISHED | deadline 2026-12-04T14:00:00-08:00 |
| challenges | `challenge-entries-d5` | D5 Aha! AI Builder Day | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| classifiers | `tier-1` | Tier-1 classifier engine | active | #2796 `7529170d5558` 2026-11-01T01:01:49Z | NOT_ESTABLISHED |
| desk | `contribution-desk` | Contribution Desk + desk-feed | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| desk | `ops` | Lane-events Neon ledger | in-flight | NOT_ESTABLISHED | land/close PR #1614 — ops(actions): matrix continuation + plan scheduled lane-events aggregator for spam reduction |
| doe | `doe` | DoE campaigns (lab-1 / pilot-1 / live waves) | in-flight | #2948 `971ff8a10299` 2026-11-01T04:27:47Z | land/close PR #2856 — doe(live-3): ci_mode — stamped dispatch comment as prompt (ruling (i-a), owners' review) |
| doe | `doe-nc1` | DoE nc-1 notation-compliance | active | #2908 `47b7aba1c339` 2026-11-01T02:41:18Z | NOT_ESTABLISHED |
| marketing | `marketing` | FB Pages MVT + challenge promo | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| marketing | `marketing-social` | Social connectors (Meta Pages / WhatsApp) | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| opportunities | `challenge-entries` | Challenge OSINT + opportunity ledger | in-flight | NOT_ESTABLISHED | land/close PR #2907 — fix: scope free-tier opportunity cost to repo work |
| providers | `providers` | Provider registry / catalog / availability | in-flight | #2924 `eda09a84bd56` 2026-11-01T03:54:43Z | land/close PR #2167 — chore(reviewer-metrics): regenerate provider x context map |
| providers | `providers-phrases` | Provider-phrases SSOT + JIT phrase layer | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| providers | `telemetry` | HindSight + Provenance telemetry ingest | in-flight | #2891 `fbd8cb72b23f` 2026-11-01T02:22:05Z | land/close PR #2914 — chore(telemetry): refresh HindSight+Provenance ingest |
| quota | `quota` | Quota registry / allocations / dispatch-tree | in-flight | #2939 `aa27eedebc65` 2026-11-01T04:17:13Z | land/close PR #2757 — feat(ci): add merged branch review audit and quota engine |
| replay | `repo-replay` | Repo Replay | unknown | NOT_ESTABLISHED | NOT_ESTABLISHED |
| swarm | `swarm` | Swarm App + F1 token migration wave | in-flight | #2937 `ecd08b5069a1` 2026-11-01T04:15:02Z | land/close PR #1470 — feat(swarms): publish Kye parity adapters, research lanes, and remote validation |
| webdev-viz | `web-design-viz` | Fleet landing + dashboard/viz surfaces | in-flight | #2941 `4b94e5304fec` 2026-11-01T04:26:14Z | land/close PR #2168 — chore(dashboards): refresh surface feeds |

## Provider × DoE settings (join: DESIGN.json × treatment.instance)

Campaigns: 10 · joined: 1 · distinct instances: 8 · providers: openrouter

| campaign | provider | model@version | role | prompt (ref#sha12) | moniker | context | instance_key | plan | recorded | dispatched |
|---|---|---|---|---|---|---|---|---|---|---|
| cb-1-chronomancer-emission | NOT_ESTABLISHED (design_only) | | | | | | | | | |
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

- merged PRs unclassified by seed match rules: 66/150 (extend ops/tracking/projects.json match rules)
