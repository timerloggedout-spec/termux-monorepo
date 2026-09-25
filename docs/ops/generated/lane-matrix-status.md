# Lane matrix status (2026-09-25T17:06:44Z)

- Master: `ea8e69f117238ef11509abf623882bb0fefef335`
- Open PRs: **91**
- Oldest: #47 (51.06d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| EXTRACT | 8 |
| HOLD | 16 |
| OBSERVE | 66 |
| WAIT | 1 |

| Age bucket | Count |
|------------|------:|
| ancient | 11 |
| fresh | 43 |
| mid | 20 |
| stale | 17 |

## Tip lanes (non-OBSERVE first)

| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #48 | 51.02 | HOLD | wrong-base:master-staging | feat(llm-api-hub): OpenAI hub + standalone server  |
| #65 | 50.42 | EXTRACT | bot-observe, minesweeper-title | 🎨 Palette: Add pulsing heartbeat and color-blind a |
| #73 | 49.58 | HOLD | wrong-base:vibe/project-management-refresh-48caeb-staging | fix(connectors): resolve critical bugs in connecto |
| #258 | 37.5 | HOLD | wrong-base:master-staging | feat(eval): add repository development performance |
| #286 | 34.93 | HOLD | wrong-base:master-staging | feat(ops): evidence-gated autonomous staging progr |
| #350 | 31.73 | HOLD | draft | fix(ops): give ox-alpha canary DeepSeek target con |
| #354 | 31.55 | HOLD | wrong-base:feat/ox-alpha-deepseek-canary-context-v2 | fix(ops): bound all OX Alpha target context |
| #373 | 29.9 | HOLD | draft | fix(ops): contextualize OX Alpha DeepSeek canary o |
| #386 | 28.48 | HOLD | draft | feat(ops): DeepSeek/OX Alpha evidence-first canary |
| #432 | 20.7 | EXTRACT | ml-wholesale-no-go | feat(ml): observe-mode GitHub ML pipelines + Issue |
| #481 | 15.01 | EXTRACT | state:unknown, minesweeper-title | ops: make Jules PR handoffs observable |
| #549 | 9.46 | EXTRACT | ml-wholesale-no-go | feat(ml): rebase observe-mode GitHub ML pipelines  |
| #578 | 8.36 | HOLD | draft | feat(accounting): spreadsheet-first accounting/bid |
| #601 | 7.04 | EXTRACT | ml-wholesale-no-go | feat(ml): extract observe-mode GitHub ML pipelines |
| #630 | 6.38 | EXTRACT | bot-observe, minesweeper-title | fix(termux-multi-agent): add fallback rich UI clas |
| #672 | 5.66 | EXTRACT | state:unknown, minesweeper-title | feat(ops): evolve Help-Wanted Tribute dashboard |
| #682 | 4.99 | WAIT | ml-keep-alive-rebase-required | feat(ml): keep-alive pipeline DAG + operator skill |
| #740 | 3.17 | HOLD | draft | feat: operationalize Laya runtime, CADENCE sweeps, |
| #750 | 2.79 | EXTRACT | bot-observe, minesweeper-title | fix(core, dashboard): add fallback imports for req |
| #752 | 2.78 | HOLD | draft | feat(ops): Termux MCP endpoint status workflow + P |
| #761 | 2.57 | HOLD | draft | lane: Desktop Commander fork + Android execution a |
| #762 | 2.56 | HOLD | draft | ops: map live plugin connector surface and parity  |
| #764 | 2.56 | HOLD | draft | lane: connect Termux hub over Tailscale + repeatab |
| #788 | 1.83 | HOLD | wrong-base:master-staging | test(archwiz): Linear client/sync coverage + Triag |
| #829 | 0.67 | HOLD | draft | feat(multi-ai-cli): DeepTerm integration with Ping |
| #47 | 51.06 | OBSERVE | ancient-no-auto-promote | feat(refTemplates): restore metadata-only skeleton |
| #67 | 49.96 | OBSERVE | ancient-no-auto-promote | docs(ops): PR scope discipline — why src/db.py is  |
| #81 | 48.8 | OBSERVE | ancient-no-auto-promote | ci: promote Gemini quota-gate + agent workflows to |
| #92 | 48.1 | OBSERVE | bot-observe | sec(workflows): harden permissions, pin SHAs, and  |
| #103 | 47.67 | OBSERVE | ancient-no-auto-promote | feat(comms): CAVEMAN-micro seed + success matrix + |
| #125 | 46.77 | OBSERVE | bot-observe | analyze agentic workflows and peer coordination ru |
| #140 | 46.41 | OBSERVE | bot-observe | 🎨 Palette: Stateful & Reactive PWA UX with Manual  |
| #143 | 46.07 | OBSERVE | bot-observe | Integrate MCP Agent Mail Coordination Layer in Git |
| #249 | 37.67 | OBSERVE | state:unknown | docs(teams): add roster, game-player, and context  |
| #263 | 37.38 | OBSERVE | state:unknown | Manus/context relationship graph |
| #311 | 34.55 | OBSERVE | state:unknown | feat(sync): govern GitLab reconciliation instead o |
| #390 | 28.45 | OBSERVE | bot-observe | docs: formalize category-theoretic notation sets a |
| #402 | 27.4 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking vulnerability o |
| #404 | 26.87 | OBSERVE | state:unknown | sec(sentinel): skip chmod when cache/db/log path i |
| #407 | 26.38 | OBSERVE | bot-observe | ⚡ Bolt: optimize Bellman-Ford graph search in arbi |

Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote.
