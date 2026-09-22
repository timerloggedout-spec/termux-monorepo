# Lane matrix status (2026-09-22T04:49:34Z)

- Master: `d40a2b2ec7b43a5ef37fa8e44a478af6c4c2b2ce`
- Open PRs: **81**
- Oldest: #47 (47.55d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| EXTRACT | 7 |
| HOLD | 10 |
| OBSERVE | 55 |
| WAIT | 9 |

| Age bucket | Count |
|------------|------:|
| ancient | 12 |
| fresh | 42 |
| mid | 12 |
| stale | 15 |

## Tip lanes (non-OBSERVE first)

| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #48 | 47.51 | HOLD | wrong-base:master-staging | feat(llm-api-hub): OpenAI hub + standalone server  |
| #65 | 46.9 | EXTRACT | bot-observe, minesweeper-title | 🎨 Palette: Add pulsing heartbeat and color-blind a |
| #69 | 46.41 | HOLD | wrong-base:feature/proposal-vote-promote | docs(DEBATE): TOC-first debate dock + Linear TER-1 |
| #73 | 46.06 | HOLD | wrong-base:vibe/project-management-refresh-48caeb-staging | fix(connectors): resolve critical bugs in connecto |
| #258 | 33.99 | HOLD | wrong-base:master-staging | feat(eval): add repository development performance |
| #286 | 31.42 | HOLD | wrong-base:master-staging | feat(ops): evidence-gated autonomous staging progr |
| #350 | 28.22 | HOLD | draft | fix(ops): give ox-alpha canary DeepSeek target con |
| #354 | 28.04 | HOLD | wrong-base:feat/ox-alpha-deepseek-canary-context-v2 | fix(ops): bound all OX Alpha target context |
| #373 | 26.39 | HOLD | draft | fix(ops): contextualize OX Alpha DeepSeek canary o |
| #386 | 24.97 | HOLD | draft | feat(ops): DeepSeek/OX Alpha evidence-first canary |
| #432 | 17.18 | EXTRACT | ml-wholesale-no-go | feat(ml): observe-mode GitHub ML pipelines + Issue |
| #481 | 11.5 | EXTRACT | state:unknown, minesweeper-title | ops: make Jules PR handoffs observable |
| #549 | 5.94 | EXTRACT | ml-wholesale-no-go | feat(ml): rebase observe-mode GitHub ML pipelines  |
| #578 | 4.84 | HOLD | draft | feat(accounting): spreadsheet-first accounting/bid |
| #601 | 3.53 | EXTRACT | ml-wholesale-no-go | feat(ml): extract observe-mode GitHub ML pipelines |
| #630 | 2.87 | EXTRACT | bot-observe, minesweeper-title | fix(termux-multi-agent): add fallback rich UI clas |
| #672 | 2.14 | EXTRACT | state:unknown, minesweeper-title | feat(ops): evolve Help-Wanted Tribute dashboard |
| #682 | 1.48 | WAIT | ml-keep-alive-rebase-required | feat(ml): keep-alive pipeline DAG + operator skill |
| #711 | 0.4 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 12:16 PDT LANE-MATRIX pul |
| #712 | 0.36 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 13:13 PDT LANE-MATRIX pul |
| #722 | 0.2 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 17:01 PDT LANE-MATRIX pul |
| #723 | 0.16 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 18:05 PDT LANE-MATRIX pul |
| #726 | 0.14 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 18:26 PDT LANE-MATRIX pul |
| #727 | 0.11 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 19:15 PDT LANE-MATRIX pul |
| #728 | 0.07 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 20:08 PDT LANE-MATRIX pul |
| #729 | 0.03 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 21:09 PDT LANE-MATRIX pul |
| #47 | 47.55 | OBSERVE | ancient-no-auto-promote | feat(refTemplates): restore metadata-only skeleton |
| #67 | 46.45 | OBSERVE | ancient-no-auto-promote | docs(ops): PR scope discipline — why src/db.py is  |
| #81 | 45.29 | OBSERVE | ancient-no-auto-promote | ci: promote Gemini quota-gate + agent workflows to |
| #92 | 44.58 | OBSERVE | bot-observe | sec(workflows): harden permissions, pin SHAs, and  |
| #103 | 44.16 | OBSERVE | ancient-no-auto-promote | feat(comms): CAVEMAN-micro seed + success matrix + |
| #125 | 43.25 | OBSERVE | bot-observe | analyze agentic workflows and peer coordination ru |
| #140 | 42.89 | OBSERVE | bot-observe | 🎨 Palette: Stateful & Reactive PWA UX with Manual  |
| #143 | 42.56 | OBSERVE | bot-observe | Integrate MCP Agent Mail Coordination Layer in Git |
| #249 | 34.16 | OBSERVE | state:unknown | docs(teams): add roster, game-player, and context  |
| #263 | 33.87 | OBSERVE | state:unknown | Manus/context relationship graph |
| #311 | 31.04 | OBSERVE | state:unknown | feat(sync): govern GitLab reconciliation instead o |
| #390 | 24.94 | OBSERVE | bot-observe | docs: formalize category-theoretic notation sets a |
| #402 | 23.89 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking vulnerability o |
| #404 | 23.36 | OBSERVE | state:unknown | sec(sentinel): skip chmod when cache/db/log path i |

Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote.
