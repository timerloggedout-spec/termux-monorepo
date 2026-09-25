# Lane matrix status (2026-09-25T11:46:05Z)

- Master: `9d4daa2a2f263407635bc71414312effba617a17`
- Open PRs: **95**
- Oldest: #47 (50.83d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| EXTRACT | 8 |
| HOLD | 16 |
| OBSERVE | 70 |
| WAIT | 1 |

| Age bucket | Count |
|------------|------:|
| ancient | 11 |
| fresh | 48 |
| mid | 19 |
| stale | 17 |

## Tip lanes (non-OBSERVE first)

| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #48 | 50.8 | HOLD | wrong-base:master-staging | feat(llm-api-hub): OpenAI hub + standalone server  |
| #65 | 50.19 | EXTRACT | bot-observe, minesweeper-title | 🎨 Palette: Add pulsing heartbeat and color-blind a |
| #73 | 49.35 | HOLD | wrong-base:vibe/project-management-refresh-48caeb-staging | fix(connectors): resolve critical bugs in connecto |
| #258 | 37.28 | HOLD | wrong-base:master-staging | feat(eval): add repository development performance |
| #286 | 34.71 | HOLD | wrong-base:master-staging | feat(ops): evidence-gated autonomous staging progr |
| #350 | 31.51 | HOLD | draft | fix(ops): give ox-alpha canary DeepSeek target con |
| #354 | 31.33 | HOLD | wrong-base:feat/ox-alpha-deepseek-canary-context-v2 | fix(ops): bound all OX Alpha target context |
| #373 | 29.68 | HOLD | draft | fix(ops): contextualize OX Alpha DeepSeek canary o |
| #386 | 28.26 | HOLD | draft | feat(ops): DeepSeek/OX Alpha evidence-first canary |
| #432 | 20.47 | EXTRACT | ml-wholesale-no-go | feat(ml): observe-mode GitHub ML pipelines + Issue |
| #481 | 14.79 | EXTRACT | state:unknown, minesweeper-title | ops: make Jules PR handoffs observable |
| #549 | 9.23 | EXTRACT | ml-wholesale-no-go | feat(ml): rebase observe-mode GitHub ML pipelines  |
| #578 | 8.13 | HOLD | draft | feat(accounting): spreadsheet-first accounting/bid |
| #601 | 6.82 | EXTRACT | ml-wholesale-no-go | feat(ml): extract observe-mode GitHub ML pipelines |
| #630 | 6.16 | EXTRACT | bot-observe, minesweeper-title | fix(termux-multi-agent): add fallback rich UI clas |
| #672 | 5.43 | EXTRACT | state:unknown, minesweeper-title | feat(ops): evolve Help-Wanted Tribute dashboard |
| #682 | 4.77 | WAIT | ml-keep-alive-rebase-required | feat(ml): keep-alive pipeline DAG + operator skill |
| #740 | 2.95 | HOLD | draft | feat: operationalize Laya runtime, CADENCE sweeps, |
| #750 | 2.57 | EXTRACT | bot-observe, minesweeper-title | fix(core, dashboard): add fallback imports for req |
| #752 | 2.56 | HOLD | draft | feat(ops): Termux MCP endpoint status workflow + P |
| #761 | 2.35 | HOLD | draft | lane: Desktop Commander fork + Android execution a |
| #762 | 2.34 | HOLD | draft | ops: map live plugin connector surface and parity  |
| #764 | 2.34 | HOLD | draft | lane: connect Termux hub over Tailscale + repeatab |
| #788 | 1.6 | HOLD | wrong-base:master-staging | test(archwiz): Linear client/sync coverage + Triag |
| #829 | 0.44 | HOLD | draft | feat(multi-ai-cli): DeepTerm integration with Ping |
| #47 | 50.83 | OBSERVE | ancient-no-auto-promote | feat(refTemplates): restore metadata-only skeleton |
| #67 | 49.74 | OBSERVE | ancient-no-auto-promote | docs(ops): PR scope discipline — why src/db.py is  |
| #81 | 48.58 | OBSERVE | ancient-no-auto-promote | ci: promote Gemini quota-gate + agent workflows to |
| #92 | 47.87 | OBSERVE | bot-observe | sec(workflows): harden permissions, pin SHAs, and  |
| #103 | 47.45 | OBSERVE | ancient-no-auto-promote | feat(comms): CAVEMAN-micro seed + success matrix + |
| #125 | 46.54 | OBSERVE | bot-observe | analyze agentic workflows and peer coordination ru |
| #140 | 46.18 | OBSERVE | bot-observe | 🎨 Palette: Stateful & Reactive PWA UX with Manual  |
| #143 | 45.85 | OBSERVE | bot-observe | Integrate MCP Agent Mail Coordination Layer in Git |
| #249 | 37.45 | OBSERVE | state:unknown | docs(teams): add roster, game-player, and context  |
| #263 | 37.16 | OBSERVE | state:unknown | Manus/context relationship graph |
| #311 | 34.33 | OBSERVE | state:unknown | feat(sync): govern GitLab reconciliation instead o |
| #390 | 28.23 | OBSERVE | bot-observe | docs: formalize category-theoretic notation sets a |
| #402 | 27.17 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking vulnerability o |
| #404 | 26.65 | OBSERVE | state:unknown | sec(sentinel): skip chmod when cache/db/log path i |
| #407 | 26.15 | OBSERVE | bot-observe | ⚡ Bolt: optimize Bellman-Ford graph search in arbi |

Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote.
