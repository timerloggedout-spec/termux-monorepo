# Lane matrix status (2026-09-21T12:42:23Z)

- Master: `b25f2e91c6f1304f1ba965b637a5e8492a46aea2`
- Open PRs: **70**
- Oldest: #47 (46.87d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| EXTRACT | 7 |
| HOLD | 10 |
| OBSERVE | 50 |
| WAIT | 3 |

| Age bucket | Count |
|------------|------:|
| ancient | 12 |
| fresh | 32 |
| mid | 11 |
| stale | 15 |

## Tip lanes (non-OBSERVE first)

| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #48 | 46.84 | HOLD | wrong-base:master-staging | feat(llm-api-hub): OpenAI hub + standalone server  |
| #65 | 46.23 | EXTRACT | bot-observe, minesweeper-title | 🎨 Palette: Add pulsing heartbeat and color-blind a |
| #69 | 45.74 | HOLD | wrong-base:feature/proposal-vote-promote | docs(DEBATE): TOC-first debate dock + Linear TER-1 |
| #73 | 45.39 | HOLD | wrong-base:vibe/project-management-refresh-48caeb-staging | fix(connectors): resolve critical bugs in connecto |
| #258 | 33.31 | HOLD | wrong-base:master-staging | feat(eval): add repository development performance |
| #286 | 30.75 | HOLD | wrong-base:master-staging | feat(ops): evidence-gated autonomous staging progr |
| #350 | 27.55 | HOLD | draft | fix(ops): give ox-alpha canary DeepSeek target con |
| #354 | 27.37 | HOLD | wrong-base:feat/ox-alpha-deepseek-canary-context-v2 | fix(ops): bound all OX Alpha target context |
| #373 | 25.71 | HOLD | draft | fix(ops): contextualize OX Alpha DeepSeek canary o |
| #386 | 24.3 | HOLD | draft | feat(ops): DeepSeek/OX Alpha evidence-first canary |
| #432 | 16.51 | EXTRACT | ml-wholesale-no-go | feat(ml): observe-mode GitHub ML pipelines + Issue |
| #481 | 10.83 | EXTRACT | state:unknown, minesweeper-title | ops: make Jules PR handoffs observable |
| #549 | 5.27 | EXTRACT | ml-wholesale-no-go | feat(ml): rebase observe-mode GitHub ML pipelines  |
| #578 | 4.17 | HOLD | draft | feat(accounting): spreadsheet-first accounting/bid |
| #601 | 2.85 | EXTRACT | ml-wholesale-no-go | feat(ml): extract observe-mode GitHub ML pipelines |
| #630 | 2.2 | EXTRACT | bot-observe, minesweeper-title | fix(termux-multi-agent): add fallback rich UI clas |
| #672 | 1.47 | EXTRACT | state:unknown, minesweeper-title | feat(ops): evolve Help-Wanted Tribute dashboard |
| #682 | 0.81 | WAIT | ml-keep-alive-rebase-required | feat(ml): keep-alive pipeline DAG + operator skill |
| #705 | 0.31 | WAIT | session-record-dual-gate | ops(session): 2026-09-20 22:19 PDT LANE-MATRIX aft |
| #706 | 0.27 | WAIT | session-record-dual-gate | ops(session): 2026-09-20 23:09 PDT LANE-MATRIX aft |
| #47 | 46.87 | OBSERVE | ancient-no-auto-promote | feat(refTemplates): restore metadata-only skeleton |
| #67 | 45.78 | OBSERVE | ancient-no-auto-promote | docs(ops): PR scope discipline — why src/db.py is  |
| #81 | 44.62 | OBSERVE | ancient-no-auto-promote | ci: promote Gemini quota-gate + agent workflows to |
| #92 | 43.91 | OBSERVE | bot-observe | sec(workflows): harden permissions, pin SHAs, and  |
| #103 | 43.49 | OBSERVE | ancient-no-auto-promote | feat(comms): CAVEMAN-micro seed + success matrix + |
| #125 | 42.58 | OBSERVE | bot-observe | analyze agentic workflows and peer coordination ru |
| #140 | 42.22 | OBSERVE | bot-observe | 🎨 Palette: Stateful & Reactive PWA UX with Manual  |
| #143 | 41.89 | OBSERVE | bot-observe | Integrate MCP Agent Mail Coordination Layer in Git |
| #249 | 33.48 | OBSERVE | state:unknown | docs(teams): add roster, game-player, and context  |
| #263 | 33.2 | OBSERVE | state:unknown | Manus/context relationship graph |
| #311 | 30.37 | OBSERVE | state:unknown | feat(sync): govern GitLab reconciliation instead o |
| #390 | 24.27 | OBSERVE | bot-observe | docs: formalize category-theoretic notation sets a |
| #402 | 23.21 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking vulnerability o |
| #404 | 22.69 | OBSERVE | state:unknown | sec(sentinel): skip chmod when cache/db/log path i |
| #407 | 22.19 | OBSERVE | bot-observe | ⚡ Bolt: optimize Bellman-Ford graph search in arbi |
| #418 | 20.51 | OBSERVE | bot-observe | 📖 Linguist: fast-path backtick guard in CedrLang d |
| #419 | 20.22 | OBSERVE | bot-observe | 🛡️ Sentinel: [MEDIUM] Enforce symlink safety and 0 |
| #429 | 17.21 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking in nexuscli exp |
| #453 | 13.51 | OBSERVE | state:unknown | feat(issues): canonical issue observatory + simila |
| #455 | 13.42 | OBSERVE | state:unknown | ci(docs): auto-render Mermaid diagrams with mmdc ( |

Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote.
