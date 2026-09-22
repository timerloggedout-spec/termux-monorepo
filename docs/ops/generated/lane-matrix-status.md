# Lane matrix status (2026-09-22T11:32:29Z)

- Master: `ca7fd7c88e65ed1d383ad800465b9ad0881f0cfd`
- Open PRs: **90**
- Oldest: #47 (47.82d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| EXTRACT | 8 |
| HOLD | 10 |
| OBSERVE | 59 |
| WAIT | 13 |

| Age bucket | Count |
|------------|------:|
| ancient | 12 |
| fresh | 50 |
| mid | 13 |
| stale | 15 |

## Tip lanes (non-OBSERVE first)

| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #48 | 47.79 | HOLD | wrong-base:master-staging | feat(llm-api-hub): OpenAI hub + standalone server  |
| #65 | 47.18 | EXTRACT | bot-observe, minesweeper-title | 🎨 Palette: Add pulsing heartbeat and color-blind a |
| #69 | 46.69 | HOLD | wrong-base:feature/proposal-vote-promote | docs(DEBATE): TOC-first debate dock + Linear TER-1 |
| #73 | 46.34 | HOLD | wrong-base:vibe/project-management-refresh-48caeb-staging | fix(connectors): resolve critical bugs in connecto |
| #258 | 34.27 | HOLD | wrong-base:master-staging | feat(eval): add repository development performance |
| #286 | 31.7 | HOLD | wrong-base:master-staging | feat(ops): evidence-gated autonomous staging progr |
| #350 | 28.5 | HOLD | draft | fix(ops): give ox-alpha canary DeepSeek target con |
| #354 | 28.32 | HOLD | wrong-base:feat/ox-alpha-deepseek-canary-context-v2 | fix(ops): bound all OX Alpha target context |
| #373 | 26.67 | HOLD | draft | fix(ops): contextualize OX Alpha DeepSeek canary o |
| #386 | 25.25 | HOLD | draft | feat(ops): DeepSeek/OX Alpha evidence-first canary |
| #432 | 17.46 | EXTRACT | ml-wholesale-no-go | feat(ml): observe-mode GitHub ML pipelines + Issue |
| #481 | 11.78 | EXTRACT | state:unknown, minesweeper-title | ops: make Jules PR handoffs observable |
| #549 | 6.22 | EXTRACT | ml-wholesale-no-go | feat(ml): rebase observe-mode GitHub ML pipelines  |
| #578 | 5.12 | HOLD | draft | feat(accounting): spreadsheet-first accounting/bid |
| #601 | 3.81 | EXTRACT | ml-wholesale-no-go | feat(ml): extract observe-mode GitHub ML pipelines |
| #630 | 3.15 | EXTRACT | bot-observe, minesweeper-title | fix(termux-multi-agent): add fallback rich UI clas |
| #672 | 2.42 | EXTRACT | state:unknown, minesweeper-title | feat(ops): evolve Help-Wanted Tribute dashboard |
| #682 | 1.76 | WAIT | ml-keep-alive-rebase-required | feat(ml): keep-alive pipeline DAG + operator skill |
| #711 | 0.68 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 12:16 PDT LANE-MATRIX pul |
| #712 | 0.64 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 13:13 PDT LANE-MATRIX pul |
| #722 | 0.48 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 17:01 PDT LANE-MATRIX pul |
| #723 | 0.43 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 18:05 PDT LANE-MATRIX pul |
| #726 | 0.42 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 18:26 PDT LANE-MATRIX pul |
| #727 | 0.39 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 19:15 PDT LANE-MATRIX pul |
| #728 | 0.35 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 20:08 PDT LANE-MATRIX pul |
| #729 | 0.31 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 21:09 PDT LANE-MATRIX pul |
| #730 | 0.27 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 22:01 PDT LANE-MATRIX pul |
| #731 | 0.21 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 23:29 PDT LANE-MATRIX pul |
| #733 | 0.2 | EXTRACT | state:unknown, minesweeper-title | feat(ops): upgrade Help-Wanted Tribute dashboard c |
| #737 | 0.02 | WAIT | session-record-dual-gate | ops(session): 2026-09-22 04:02 PDT LANE-MATRIX pul |
| #738 | 0.01 | WAIT | session-record-dual-gate | ops(session): 2026-09-22 04:12 PDT LANE-MATRIX pul |
| #47 | 47.82 | OBSERVE | ancient-no-auto-promote | feat(refTemplates): restore metadata-only skeleton |
| #67 | 46.73 | OBSERVE | ancient-no-auto-promote | docs(ops): PR scope discipline — why src/db.py is  |
| #81 | 45.57 | OBSERVE | ancient-no-auto-promote | ci: promote Gemini quota-gate + agent workflows to |
| #92 | 44.86 | OBSERVE | bot-observe | sec(workflows): harden permissions, pin SHAs, and  |
| #103 | 44.44 | OBSERVE | ancient-no-auto-promote | feat(comms): CAVEMAN-micro seed + success matrix + |
| #125 | 43.53 | OBSERVE | bot-observe | analyze agentic workflows and peer coordination ru |
| #140 | 43.17 | OBSERVE | bot-observe | 🎨 Palette: Stateful & Reactive PWA UX with Manual  |
| #143 | 42.84 | OBSERVE | bot-observe | Integrate MCP Agent Mail Coordination Layer in Git |
| #249 | 34.44 | OBSERVE | state:unknown | docs(teams): add roster, game-player, and context  |

Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote.
