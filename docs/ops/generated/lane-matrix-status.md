# Lane matrix status (2026-09-25T04:52:34Z)

- Master: `98a13dcf9fac091585a11316985485f101c21d8d`
- Open PRs: **93**
- Oldest: #47 (50.55d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| EXTRACT | 8 |
| HOLD | 16 |
| OBSERVE | 68 |
| WAIT | 1 |

| Age bucket | Count |
|------------|------:|
| ancient | 11 |
| fresh | 48 |
| mid | 17 |
| stale | 17 |

## Tip lanes (non-OBSERVE first)

| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #48 | 50.51 | HOLD | wrong-base:master-staging | feat(llm-api-hub): OpenAI hub + standalone server  |
| #65 | 49.91 | EXTRACT | bot-observe, minesweeper-title | 🎨 Palette: Add pulsing heartbeat and color-blind a |
| #73 | 49.07 | HOLD | wrong-base:vibe/project-management-refresh-48caeb-staging | fix(connectors): resolve critical bugs in connecto |
| #258 | 36.99 | HOLD | wrong-base:master-staging | feat(eval): add repository development performance |
| #286 | 34.42 | HOLD | wrong-base:master-staging | feat(ops): evidence-gated autonomous staging progr |
| #350 | 31.22 | HOLD | draft | fix(ops): give ox-alpha canary DeepSeek target con |
| #354 | 31.04 | HOLD | wrong-base:feat/ox-alpha-deepseek-canary-context-v2 | fix(ops): bound all OX Alpha target context |
| #373 | 29.39 | HOLD | draft | fix(ops): contextualize OX Alpha DeepSeek canary o |
| #386 | 27.97 | HOLD | draft | feat(ops): DeepSeek/OX Alpha evidence-first canary |
| #432 | 20.19 | EXTRACT | ml-wholesale-no-go | feat(ml): observe-mode GitHub ML pipelines + Issue |
| #481 | 14.5 | EXTRACT | state:unknown, minesweeper-title | ops: make Jules PR handoffs observable |
| #549 | 8.95 | EXTRACT | ml-wholesale-no-go | feat(ml): rebase observe-mode GitHub ML pipelines  |
| #578 | 7.85 | HOLD | draft | feat(accounting): spreadsheet-first accounting/bid |
| #601 | 6.53 | EXTRACT | ml-wholesale-no-go | feat(ml): extract observe-mode GitHub ML pipelines |
| #630 | 5.87 | EXTRACT | bot-observe, minesweeper-title | fix(termux-multi-agent): add fallback rich UI clas |
| #672 | 5.15 | EXTRACT | state:unknown, minesweeper-title | feat(ops): evolve Help-Wanted Tribute dashboard |
| #682 | 4.48 | WAIT | ml-keep-alive-rebase-required | feat(ml): keep-alive pipeline DAG + operator skill |
| #740 | 2.66 | HOLD | draft | feat: operationalize Laya runtime, CADENCE sweeps, |
| #750 | 2.28 | EXTRACT | bot-observe, minesweeper-title | fix(core, dashboard): add fallback imports for req |
| #752 | 2.27 | HOLD | draft | feat(ops): Termux MCP endpoint status workflow + P |
| #761 | 2.06 | HOLD | draft | lane: Desktop Commander fork + Android execution a |
| #762 | 2.05 | HOLD | draft | ops: map live plugin connector surface and parity  |
| #764 | 2.05 | HOLD | draft | lane: connect Termux hub over Tailscale + repeatab |
| #788 | 1.32 | HOLD | wrong-base:master-staging | test(archwiz): Linear client/sync coverage + Triag |
| #829 | 0.16 | HOLD | draft | feat(multi-ai-cli): DeepTerm integration with Ping |
| #47 | 50.55 | OBSERVE | ancient-no-auto-promote | feat(refTemplates): restore metadata-only skeleton |
| #67 | 49.45 | OBSERVE | ancient-no-auto-promote | docs(ops): PR scope discipline — why src/db.py is  |
| #81 | 48.29 | OBSERVE | ancient-no-auto-promote | ci: promote Gemini quota-gate + agent workflows to |
| #92 | 47.59 | OBSERVE | bot-observe | sec(workflows): harden permissions, pin SHAs, and  |
| #103 | 47.16 | OBSERVE | ancient-no-auto-promote | feat(comms): CAVEMAN-micro seed + success matrix + |
| #125 | 46.26 | OBSERVE | bot-observe | analyze agentic workflows and peer coordination ru |
| #140 | 45.9 | OBSERVE | bot-observe | 🎨 Palette: Stateful & Reactive PWA UX with Manual  |
| #143 | 45.56 | OBSERVE | bot-observe | Integrate MCP Agent Mail Coordination Layer in Git |
| #249 | 37.16 | OBSERVE | state:unknown | docs(teams): add roster, game-player, and context  |
| #263 | 36.87 | OBSERVE | state:unknown | Manus/context relationship graph |
| #311 | 34.04 | OBSERVE | state:unknown | feat(sync): govern GitLab reconciliation instead o |
| #390 | 27.94 | OBSERVE | bot-observe | docs: formalize category-theoretic notation sets a |
| #402 | 26.89 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking vulnerability o |
| #404 | 26.36 | OBSERVE | state:unknown | sec(sentinel): skip chmod when cache/db/log path i |
| #407 | 25.87 | OBSERVE | bot-observe | ⚡ Bolt: optimize Bellman-Ford graph search in arbi |

Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote.
