# Lane matrix status (2026-09-22T21:15:23Z)

- Master: `4ae5bb294b3f632c533126c3e1062ce96b2d51bd`
- Open PRs: **94**
- Oldest: #47 (48.23d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| EXTRACT | 7 |
| HOLD | 11 |
| OBSERVE | 59 |
| WAIT | 17 |

| Age bucket | Count |
|------------|------:|
| ancient | 12 |
| fresh | 53 |
| mid | 14 |
| stale | 15 |

## Tip lanes (non-OBSERVE first)

| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #48 | 48.19 | HOLD | wrong-base:master-staging | feat(llm-api-hub): OpenAI hub + standalone server  |
| #65 | 47.59 | EXTRACT | bot-observe, minesweeper-title | 🎨 Palette: Add pulsing heartbeat and color-blind a |
| #69 | 47.1 | HOLD | wrong-base:feature/proposal-vote-promote | docs(DEBATE): TOC-first debate dock + Linear TER-1 |
| #73 | 46.75 | HOLD | wrong-base:vibe/project-management-refresh-48caeb-staging | fix(connectors): resolve critical bugs in connecto |
| #258 | 34.67 | HOLD | wrong-base:master-staging | feat(eval): add repository development performance |
| #286 | 32.1 | HOLD | wrong-base:master-staging | feat(ops): evidence-gated autonomous staging progr |
| #350 | 28.91 | HOLD | draft | fix(ops): give ox-alpha canary DeepSeek target con |
| #354 | 28.73 | HOLD | wrong-base:feat/ox-alpha-deepseek-canary-context-v2 | fix(ops): bound all OX Alpha target context |
| #373 | 27.07 | HOLD | draft | fix(ops): contextualize OX Alpha DeepSeek canary o |
| #386 | 25.65 | HOLD | draft | feat(ops): DeepSeek/OX Alpha evidence-first canary |
| #432 | 17.87 | EXTRACT | ml-wholesale-no-go | feat(ml): observe-mode GitHub ML pipelines + Issue |
| #481 | 12.18 | EXTRACT | state:unknown, minesweeper-title | ops: make Jules PR handoffs observable |
| #549 | 6.63 | EXTRACT | ml-wholesale-no-go | feat(ml): rebase observe-mode GitHub ML pipelines  |
| #578 | 5.53 | HOLD | draft | feat(accounting): spreadsheet-first accounting/bid |
| #601 | 4.21 | EXTRACT | ml-wholesale-no-go | feat(ml): extract observe-mode GitHub ML pipelines |
| #630 | 3.55 | EXTRACT | bot-observe, minesweeper-title | fix(termux-multi-agent): add fallback rich UI clas |
| #672 | 2.83 | EXTRACT | state:unknown, minesweeper-title | feat(ops): evolve Help-Wanted Tribute dashboard |
| #682 | 2.16 | WAIT | ml-keep-alive-rebase-required | feat(ml): keep-alive pipeline DAG + operator skill |
| #711 | 1.08 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 12:16 PDT LANE-MATRIX pul |
| #712 | 1.04 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 13:13 PDT LANE-MATRIX pul |
| #722 | 0.88 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 17:01 PDT LANE-MATRIX pul |
| #723 | 0.84 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 18:05 PDT LANE-MATRIX pul |
| #726 | 0.82 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 18:26 PDT LANE-MATRIX pul |
| #727 | 0.79 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 19:15 PDT LANE-MATRIX pul |
| #728 | 0.75 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 20:08 PDT LANE-MATRIX pul |
| #729 | 0.71 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 21:09 PDT LANE-MATRIX pul |
| #730 | 0.68 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 22:01 PDT LANE-MATRIX pul |
| #731 | 0.61 | WAIT | session-record-dual-gate | ops(session): 2026-09-21 23:29 PDT LANE-MATRIX pul |
| #737 | 0.43 | WAIT | session-record-dual-gate | ops(session): 2026-09-22 04:02 PDT LANE-MATRIX pul |
| #738 | 0.42 | WAIT | session-record-dual-gate | ops(session): 2026-09-22 04:12 PDT LANE-MATRIX pul |
| #740 | 0.34 | HOLD | draft | feat: operationalize Laya runtime, CADENCE sweeps, |
| #744 | 0.13 | WAIT | session-record-dual-gate | ops(session): 2026-09-22 11:18 PDT LANE-MATRIX pul |
| #745 | 0.09 | WAIT | session-record-dual-gate | ops(session): 2026-09-22 12:10 PDT LANE-MATRIX pul |
| #747 | 0.05 | WAIT | session-record-dual-gate | ops(session): 2026-09-22 13:03 PDT LANE-MATRIX — H |
| #749 | 0.01 | WAIT | session-record-dual-gate | ops(session): 2026-09-22 14:04 PDT LANE-MATRIX — t |
| #47 | 48.23 | OBSERVE | ancient-no-auto-promote | feat(refTemplates): restore metadata-only skeleton |
| #67 | 47.13 | OBSERVE | ancient-no-auto-promote | docs(ops): PR scope discipline — why src/db.py is  |
| #81 | 45.97 | OBSERVE | ancient-no-auto-promote | ci: promote Gemini quota-gate + agent workflows to |
| #92 | 45.27 | OBSERVE | bot-observe | sec(workflows): harden permissions, pin SHAs, and  |
| #103 | 44.84 | OBSERVE | ancient-no-auto-promote | feat(comms): CAVEMAN-micro seed + success matrix + |

Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote.
