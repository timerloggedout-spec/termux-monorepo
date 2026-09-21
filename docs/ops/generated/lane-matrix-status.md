# Lane matrix status (2026-09-21T01:23:52Z)

- Master: `c447216baaa1ecff7e41ea5e37ec51ec5617e228`
- Open PRs: **67**
- Oldest: #47 (46.4d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| EXTRACT | 7 |
| HOLD | 10 |
| OBSERVE | 49 |
| WAIT | 1 |

| Age bucket | Count |
|------------|------:|
| ancient | 12 |
| fresh | 29 |
| mid | 12 |
| stale | 14 |

## Tip lanes (non-OBSERVE first)

| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #48 | 46.36 | HOLD | wrong-base:master-staging | feat(llm-api-hub): OpenAI hub + standalone server  |
| #65 | 45.76 | EXTRACT | bot-observe, minesweeper-title | 🎨 Palette: Add pulsing heartbeat and color-blind a |
| #69 | 45.27 | HOLD | wrong-base:feature/proposal-vote-promote | docs(DEBATE): TOC-first debate dock + Linear TER-1 |
| #73 | 44.92 | HOLD | wrong-base:vibe/project-management-refresh-48caeb-staging | fix(connectors): resolve critical bugs in connecto |
| #258 | 32.84 | HOLD | wrong-base:master-staging | feat(eval): add repository development performance |
| #286 | 30.28 | HOLD | wrong-base:master-staging | feat(ops): evidence-gated autonomous staging progr |
| #350 | 27.08 | HOLD | draft | fix(ops): give ox-alpha canary DeepSeek target con |
| #354 | 26.9 | HOLD | wrong-base:feat/ox-alpha-deepseek-canary-context-v2 | fix(ops): bound all OX Alpha target context |
| #373 | 25.24 | HOLD | draft | fix(ops): contextualize OX Alpha DeepSeek canary o |
| #386 | 23.82 | HOLD | draft | feat(ops): DeepSeek/OX Alpha evidence-first canary |
| #432 | 16.04 | EXTRACT | ml-wholesale-no-go | feat(ml): observe-mode GitHub ML pipelines + Issue |
| #481 | 10.36 | EXTRACT | state:unknown, minesweeper-title | ops: make Jules PR handoffs observable |
| #549 | 4.8 | EXTRACT | ml-wholesale-no-go | feat(ml): rebase observe-mode GitHub ML pipelines  |
| #578 | 3.7 | HOLD | draft | feat(accounting): spreadsheet-first accounting/bid |
| #601 | 2.38 | EXTRACT | ml-wholesale-no-go | feat(ml): extract observe-mode GitHub ML pipelines |
| #630 | 1.73 | EXTRACT | bot-observe, minesweeper-title | fix(termux-multi-agent): add fallback rich UI clas |
| #672 | 1.0 | EXTRACT | state:unknown, minesweeper-title | feat(ops): evolve Help-Wanted Tribute dashboard |
| #682 | 0.33 | WAIT | ml-keep-alive-rebase-required | feat(ml): keep-alive pipeline DAG + operator skill |
| #47 | 46.4 | OBSERVE | ancient-no-auto-promote | feat(refTemplates): restore metadata-only skeleton |
| #67 | 45.31 | OBSERVE | ancient-no-auto-promote | docs(ops): PR scope discipline — why src/db.py is  |
| #81 | 44.15 | OBSERVE | ancient-no-auto-promote | ci: promote Gemini quota-gate + agent workflows to |
| #92 | 43.44 | OBSERVE | bot-observe | sec(workflows): harden permissions, pin SHAs, and  |
| #103 | 43.02 | OBSERVE | ancient-no-auto-promote | feat(comms): CAVEMAN-micro seed + success matrix + |
| #125 | 42.11 | OBSERVE | bot-observe | analyze agentic workflows and peer coordination ru |
| #140 | 41.75 | OBSERVE | bot-observe | 🎨 Palette: Stateful & Reactive PWA UX with Manual  |
| #143 | 41.42 | OBSERVE | bot-observe | Integrate MCP Agent Mail Coordination Layer in Git |
| #249 | 33.01 | OBSERVE | state:unknown | docs(teams): add roster, game-player, and context  |
| #263 | 32.73 | OBSERVE | state:unknown | Manus/context relationship graph |
| #311 | 29.9 | OBSERVE | state:unknown | feat(sync): govern GitLab reconciliation instead o |
| #390 | 23.79 | OBSERVE | bot-observe | docs: formalize category-theoretic notation sets a |
| #402 | 22.74 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking vulnerability o |
| #404 | 22.22 | OBSERVE | state:unknown | sec(sentinel): skip chmod when cache/db/log path i |
| #407 | 21.72 | OBSERVE | bot-observe | ⚡ Bolt: optimize Bellman-Ford graph search in arbi |
| #418 | 20.04 | OBSERVE | bot-observe | 📖 Linguist: fast-path backtick guard in CedrLang d |
| #419 | 19.75 | OBSERVE | bot-observe | 🛡️ Sentinel: [MEDIUM] Enforce symlink safety and 0 |
| #429 | 16.74 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking in nexuscli exp |
| #453 | 13.04 | OBSERVE | state:unknown | feat(issues): canonical issue observatory + simila |
| #455 | 12.95 | OBSERVE | state:unknown | ci(docs): auto-render Mermaid diagrams with mmdc ( |
| #456 | 12.83 | OBSERVE | state:unknown | feat(ci): add advisory CellCog SDK PR-review lane  |
| #466 | 12.13 | OBSERVE | bot-observe | ops(lane): audit lane consolidation SSOT and lag i |

Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote.
