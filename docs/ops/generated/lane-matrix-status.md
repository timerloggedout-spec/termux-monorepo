# Lane matrix status (2026-09-21T01:15:59Z)

- Master: `0643c21d7e13f340285659f3143aaed2079bca37`
- Open PRs: **76**
- Oldest: #47 (46.4d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| EXTRACT | 7 |
| HOLD | 10 |
| OBSERVE | 51 |
| WAIT | 8 |

| Age bucket | Count |
|------------|------:|
| ancient | 12 |
| fresh | 37 |
| mid | 13 |
| stale | 14 |

## Tip lanes (non-OBSERVE first)

| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #48 | 46.36 | HOLD | wrong-base:master-staging | feat(llm-api-hub): OpenAI hub + standalone server  |
| #65 | 45.75 | EXTRACT | bot-observe, minesweeper-title | 🎨 Palette: Add pulsing heartbeat and color-blind a |
| #69 | 45.27 | HOLD | wrong-base:feature/proposal-vote-promote | docs(DEBATE): TOC-first debate dock + Linear TER-1 |
| #73 | 44.91 | HOLD | wrong-base:vibe/project-management-refresh-48caeb-staging | fix(connectors): resolve critical bugs in connecto |
| #258 | 32.84 | HOLD | wrong-base:master-staging | feat(eval): add repository development performance |
| #286 | 30.27 | HOLD | wrong-base:master-staging | feat(ops): evidence-gated autonomous staging progr |
| #350 | 27.07 | HOLD | draft | fix(ops): give ox-alpha canary DeepSeek target con |
| #354 | 26.89 | HOLD | wrong-base:feat/ox-alpha-deepseek-canary-context-v2 | fix(ops): bound all OX Alpha target context |
| #373 | 25.24 | HOLD | draft | fix(ops): contextualize OX Alpha DeepSeek canary o |
| #386 | 23.82 | HOLD | draft | feat(ops): DeepSeek/OX Alpha evidence-first canary |
| #432 | 16.03 | EXTRACT | ml-wholesale-no-go | feat(ml): observe-mode GitHub ML pipelines + Issue |
| #481 | 10.35 | EXTRACT | state:unknown, minesweeper-title | ops: make Jules PR handoffs observable |
| #549 | 4.8 | EXTRACT | ml-wholesale-no-go | feat(ml): rebase observe-mode GitHub ML pipelines  |
| #578 | 3.7 | HOLD | draft | feat(accounting): spreadsheet-first accounting/bid |
| #601 | 2.38 | EXTRACT | ml-wholesale-no-go | feat(ml): extract observe-mode GitHub ML pipelines |
| #619 | 2.08 | WAIT | session-record-dual-gate | ops(skills): record live master fb382c48 + #617 WA |
| #630 | 1.72 | EXTRACT | bot-observe, minesweeper-title | fix(termux-multi-agent): add fallback rich UI clas |
| #641 | 1.17 | WAIT | session-record-dual-gate | ops(skills): record #638+#640 land + live master 1 |
| #647 | 1.13 | WAIT | session-record-dual-gate | ops(skills): session record 2026-09-19 15:04 PDT ( |
| #648 | 1.13 | WAIT | session-record-dual-gate | ops(skills): github-issue-pr-graph + fold/delete A |
| #672 | 1.0 | EXTRACT | state:unknown, minesweeper-title | feat(ops): evolve Help-Wanted Tribute dashboard |
| #673 | 0.99 | WAIT | session-record-dual-gate | ops(skills): session record 2026-09-19 18:23 PDT ( |
| #682 | 0.33 | WAIT | ml-keep-alive-rebase-required | feat(ml): keep-alive pipeline DAG + operator skill |
| #696 | 0.01 | WAIT | session-record-dual-gate | ops(skills): session 2026-09-20 18:00 PDT BIUDL —  |
| #697 | 0.01 | WAIT | session-record-dual-gate | ops(skills): session record 2026-09-20 ~18:00 PDT  |
| #47 | 46.4 | OBSERVE | ancient-no-auto-promote | feat(refTemplates): restore metadata-only skeleton |
| #67 | 45.3 | OBSERVE | ancient-no-auto-promote | docs(ops): PR scope discipline — why src/db.py is  |
| #81 | 44.14 | OBSERVE | ancient-no-auto-promote | ci: promote Gemini quota-gate + agent workflows to |
| #92 | 43.44 | OBSERVE | bot-observe | sec(workflows): harden permissions, pin SHAs, and  |
| #103 | 43.01 | OBSERVE | ancient-no-auto-promote | feat(comms): CAVEMAN-micro seed + success matrix + |
| #125 | 42.11 | OBSERVE | bot-observe | analyze agentic workflows and peer coordination ru |
| #140 | 41.75 | OBSERVE | bot-observe | 🎨 Palette: Stateful & Reactive PWA UX with Manual  |
| #143 | 41.41 | OBSERVE | bot-observe | Integrate MCP Agent Mail Coordination Layer in Git |
| #249 | 33.01 | OBSERVE | state:unknown | docs(teams): add roster, game-player, and context  |
| #263 | 32.72 | OBSERVE | state:unknown | Manus/context relationship graph |
| #311 | 29.89 | OBSERVE | state:unknown | feat(sync): govern GitLab reconciliation instead o |
| #390 | 23.79 | OBSERVE | bot-observe | docs: formalize category-theoretic notation sets a |
| #402 | 22.74 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking vulnerability o |
| #404 | 22.21 | OBSERVE | state:unknown | sec(sentinel): skip chmod when cache/db/log path i |
| #407 | 21.72 | OBSERVE | bot-observe | ⚡ Bolt: optimize Bellman-Ford graph search in arbi |

Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote.
