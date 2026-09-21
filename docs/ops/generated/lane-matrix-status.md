# Lane matrix status (2026-09-21T21:57:08Z)

- Master: `abaad3da54c14e81e62aabe5f9491566ec226f1a`
- Open PRs: **70**
- Oldest: #47 (47.26d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

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
| #48 | 47.22 | HOLD | wrong-base:master-staging | feat(llm-api-hub): OpenAI hub + standalone server  |
| #65 | 46.62 | EXTRACT | bot-observe, minesweeper-title | 🎨 Palette: Add pulsing heartbeat and color-blind a |
| #69 | 46.13 | HOLD | wrong-base:feature/proposal-vote-promote | docs(DEBATE): TOC-first debate dock + Linear TER-1 |
| #73 | 45.78 | HOLD | wrong-base:vibe/project-management-refresh-48caeb-staging | fix(connectors): resolve critical bugs in connecto |
| #258 | 33.7 | HOLD | wrong-base:master-staging | feat(eval): add repository development performance |
| #286 | 31.13 | HOLD | wrong-base:master-staging | feat(ops): evidence-gated autonomous staging progr |
| #350 | 27.93 | HOLD | draft | fix(ops): give ox-alpha canary DeepSeek target con |
| #354 | 27.76 | HOLD | wrong-base:feat/ox-alpha-deepseek-canary-context-v2 | fix(ops): bound all OX Alpha target context |
| #373 | 26.1 | HOLD | draft | fix(ops): contextualize OX Alpha DeepSeek canary o |
| #386 | 24.68 | HOLD | draft | feat(ops): DeepSeek/OX Alpha evidence-first canary |
| #432 | 16.9 | EXTRACT | ml-wholesale-no-go | feat(ml): observe-mode GitHub ML pipelines + Issue |
| #481 | 11.21 | EXTRACT | state:unknown, minesweeper-title | ops: make Jules PR handoffs observable |
| #549 | 5.66 | EXTRACT | ml-wholesale-no-go | feat(ml): rebase observe-mode GitHub ML pipelines  |
| #578 | 4.56 | HOLD | draft | feat(accounting): spreadsheet-first accounting/bid |
| #601 | 3.24 | EXTRACT | ml-wholesale-no-go | feat(ml): extract observe-mode GitHub ML pipelines |
| #630 | 2.58 | EXTRACT | bot-observe, minesweeper-title | fix(termux-multi-agent): add fallback rich UI clas |
| #672 | 1.86 | EXTRACT | state:unknown, minesweeper-title | feat(ops): evolve Help-Wanted Tribute dashboard |
| #682 | 1.19 | WAIT | ml-keep-alive-rebase-required | feat(ml): keep-alive pipeline DAG + operator skill |
| #711 | 0.11 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 12:16 PDT LANE-MATRIX pul |
| #712 | 0.07 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 13:13 PDT LANE-MATRIX pul |
| #47 | 47.26 | OBSERVE | ancient-no-auto-promote | feat(refTemplates): restore metadata-only skeleton |
| #67 | 46.16 | OBSERVE | ancient-no-auto-promote | docs(ops): PR scope discipline — why src/db.py is  |
| #81 | 45.0 | OBSERVE | ancient-no-auto-promote | ci: promote Gemini quota-gate + agent workflows to |
| #92 | 44.3 | OBSERVE | bot-observe | sec(workflows): harden permissions, pin SHAs, and  |
| #103 | 43.87 | OBSERVE | ancient-no-auto-promote | feat(comms): CAVEMAN-micro seed + success matrix + |
| #125 | 42.97 | OBSERVE | bot-observe | analyze agentic workflows and peer coordination ru |
| #140 | 42.61 | OBSERVE | bot-observe | 🎨 Palette: Stateful & Reactive PWA UX with Manual  |
| #143 | 42.27 | OBSERVE | bot-observe | Integrate MCP Agent Mail Coordination Layer in Git |
| #249 | 33.87 | OBSERVE | state:unknown | docs(teams): add roster, game-player, and context  |
| #263 | 33.58 | OBSERVE | state:unknown | Manus/context relationship graph |
| #311 | 30.76 | OBSERVE | state:unknown | feat(sync): govern GitLab reconciliation instead o |
| #390 | 24.65 | OBSERVE | bot-observe | docs: formalize category-theoretic notation sets a |
| #402 | 23.6 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking vulnerability o |
| #404 | 23.07 | OBSERVE | state:unknown | sec(sentinel): skip chmod when cache/db/log path i |
| #407 | 22.58 | OBSERVE | bot-observe | ⚡ Bolt: optimize Bellman-Ford graph search in arbi |
| #418 | 20.9 | OBSERVE | bot-observe | 📖 Linguist: fast-path backtick guard in CedrLang d |
| #419 | 20.61 | OBSERVE | bot-observe | 🛡️ Sentinel: [MEDIUM] Enforce symlink safety and 0 |
| #429 | 17.6 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking in nexuscli exp |
| #453 | 13.89 | OBSERVE | state:unknown | feat(issues): canonical issue observatory + simila |
| #455 | 13.81 | OBSERVE | state:unknown | ci(docs): auto-render Mermaid diagrams with mmdc ( |

Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote.
