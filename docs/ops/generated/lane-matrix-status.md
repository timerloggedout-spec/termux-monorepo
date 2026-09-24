# Lane matrix status (2026-09-24T20:33:40Z)

- Master: `8aeb902d0aa0d55671a6710399402e37e22268be`
- Open PRs: **89**
- Oldest: #47 (50.2d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| EXTRACT | 8 |
| HOLD | 15 |
| OBSERVE | 64 |
| SUPERSEDE | 1 |
| WAIT | 1 |

| Age bucket | Count |
|------------|------:|
| ancient | 11 |
| fresh | 46 |
| mid | 16 |
| stale | 16 |

## Tip lanes (non-OBSERVE first)

| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #48 | 50.16 | HOLD | wrong-base:master-staging | feat(llm-api-hub): OpenAI hub + standalone server  |
| #65 | 49.56 | EXTRACT | bot-observe, minesweeper-title | 🎨 Palette: Add pulsing heartbeat and color-blind a |
| #73 | 48.72 | HOLD | wrong-base:vibe/project-management-refresh-48caeb-staging | fix(connectors): resolve critical bugs in connecto |
| #258 | 36.64 | HOLD | wrong-base:master-staging | feat(eval): add repository development performance |
| #286 | 34.07 | HOLD | wrong-base:master-staging | feat(ops): evidence-gated autonomous staging progr |
| #350 | 30.88 | HOLD | draft | fix(ops): give ox-alpha canary DeepSeek target con |
| #354 | 30.7 | HOLD | wrong-base:feat/ox-alpha-deepseek-canary-context-v2 | fix(ops): bound all OX Alpha target context |
| #373 | 29.04 | HOLD | draft | fix(ops): contextualize OX Alpha DeepSeek canary o |
| #386 | 27.62 | HOLD | draft | feat(ops): DeepSeek/OX Alpha evidence-first canary |
| #432 | 19.84 | EXTRACT | ml-wholesale-no-go | feat(ml): observe-mode GitHub ML pipelines + Issue |
| #481 | 14.16 | EXTRACT | state:unknown, minesweeper-title | ops: make Jules PR handoffs observable |
| #549 | 8.6 | EXTRACT | ml-wholesale-no-go | feat(ml): rebase observe-mode GitHub ML pipelines  |
| #578 | 7.5 | HOLD | draft | feat(accounting): spreadsheet-first accounting/bid |
| #601 | 6.18 | EXTRACT | ml-wholesale-no-go | feat(ml): extract observe-mode GitHub ML pipelines |
| #630 | 5.52 | EXTRACT | bot-observe, minesweeper-title | fix(termux-multi-agent): add fallback rich UI clas |
| #672 | 4.8 | EXTRACT | state:unknown, minesweeper-title | feat(ops): evolve Help-Wanted Tribute dashboard |
| #682 | 4.13 | WAIT | ml-keep-alive-rebase-required | feat(ml): keep-alive pipeline DAG + operator skill |
| #740 | 2.31 | HOLD | draft | feat: operationalize Laya runtime, CADENCE sweeps, |
| #750 | 1.93 | EXTRACT | bot-observe, minesweeper-title | fix(core, dashboard): add fallback imports for req |
| #752 | 1.92 | HOLD | draft | feat(ops): Termux MCP endpoint status workflow + P |
| #761 | 1.72 | HOLD | draft | lane: Desktop Commander fork + Android execution a |
| #762 | 1.71 | HOLD | draft | ops: map live plugin connector surface and parity  |
| #764 | 1.7 | HOLD | draft | lane: connect Termux hub over Tailscale + repeatab |
| #788 | 0.97 | HOLD | wrong-base:master-staging | test(archwiz): Linear client/sync coverage + Triag |
| #815 | 0.0 | SUPERSEDE | session-record-not-a-promote-object | feat(ops): open LANE-MATRIX as a live URL (board,  |
| #47 | 50.2 | OBSERVE | ancient-no-auto-promote | feat(refTemplates): restore metadata-only skeleton |
| #67 | 49.11 | OBSERVE | ancient-no-auto-promote | docs(ops): PR scope discipline — why src/db.py is  |
| #81 | 47.95 | OBSERVE | ancient-no-auto-promote | ci: promote Gemini quota-gate + agent workflows to |
| #92 | 47.24 | OBSERVE | bot-observe | sec(workflows): harden permissions, pin SHAs, and  |
| #103 | 46.81 | OBSERVE | ancient-no-auto-promote | feat(comms): CAVEMAN-micro seed + success matrix + |
| #125 | 45.91 | OBSERVE | bot-observe | analyze agentic workflows and peer coordination ru |
| #140 | 45.55 | OBSERVE | bot-observe | 🎨 Palette: Stateful & Reactive PWA UX with Manual  |
| #143 | 45.21 | OBSERVE | bot-observe | Integrate MCP Agent Mail Coordination Layer in Git |
| #249 | 36.81 | OBSERVE | state:unknown | docs(teams): add roster, game-player, and context  |
| #263 | 36.53 | OBSERVE | state:unknown | Manus/context relationship graph |
| #311 | 33.7 | OBSERVE | state:unknown | feat(sync): govern GitLab reconciliation instead o |
| #390 | 27.59 | OBSERVE | bot-observe | docs: formalize category-theoretic notation sets a |
| #402 | 26.54 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking vulnerability o |
| #404 | 26.01 | OBSERVE | state:unknown | sec(sentinel): skip chmod when cache/db/log path i |
| #407 | 25.52 | OBSERVE | bot-observe | ⚡ Bolt: optimize Bellman-Ford graph search in arbi |

Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote.
