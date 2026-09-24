# Lane matrix status (2026-09-24T21:28:24Z)

- Master: `03ffb33b54b86b52cf8a11cc2f7db6d2d8061772`
- Open PRs: **90**
- Oldest: #47 (50.24d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| EXTRACT | 9 |
| HOLD | 15 |
| OBSERVE | 65 |
| WAIT | 1 |

| Age bucket | Count |
|------------|------:|
| ancient | 11 |
| fresh | 45 |
| mid | 18 |
| stale | 16 |

## Tip lanes (non-OBSERVE first)

| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #48 | 50.2 | HOLD | wrong-base:master-staging | feat(llm-api-hub): OpenAI hub + standalone server  |
| #65 | 49.6 | EXTRACT | bot-observe, minesweeper-title | 🎨 Palette: Add pulsing heartbeat and color-blind a |
| #73 | 48.76 | HOLD | wrong-base:vibe/project-management-refresh-48caeb-staging | fix(connectors): resolve critical bugs in connecto |
| #258 | 36.68 | HOLD | wrong-base:master-staging | feat(eval): add repository development performance |
| #286 | 34.11 | HOLD | wrong-base:master-staging | feat(ops): evidence-gated autonomous staging progr |
| #350 | 30.91 | HOLD | draft | fix(ops): give ox-alpha canary DeepSeek target con |
| #354 | 30.74 | HOLD | wrong-base:feat/ox-alpha-deepseek-canary-context-v2 | fix(ops): bound all OX Alpha target context |
| #373 | 29.08 | HOLD | draft | fix(ops): contextualize OX Alpha DeepSeek canary o |
| #386 | 27.66 | HOLD | draft | feat(ops): DeepSeek/OX Alpha evidence-first canary |
| #432 | 19.88 | EXTRACT | ml-wholesale-no-go | feat(ml): observe-mode GitHub ML pipelines + Issue |
| #481 | 14.19 | EXTRACT | state:unknown, minesweeper-title | ops: make Jules PR handoffs observable |
| #549 | 8.64 | EXTRACT | ml-wholesale-no-go | feat(ml): rebase observe-mode GitHub ML pipelines  |
| #578 | 7.54 | HOLD | draft | feat(accounting): spreadsheet-first accounting/bid |
| #601 | 6.22 | EXTRACT | ml-wholesale-no-go | feat(ml): extract observe-mode GitHub ML pipelines |
| #630 | 5.56 | EXTRACT | bot-observe, minesweeper-title | fix(termux-multi-agent): add fallback rich UI clas |
| #672 | 4.84 | EXTRACT | state:unknown, minesweeper-title | feat(ops): evolve Help-Wanted Tribute dashboard |
| #682 | 4.17 | WAIT | ml-keep-alive-rebase-required | feat(ml): keep-alive pipeline DAG + operator skill |
| #740 | 2.35 | HOLD | draft | feat: operationalize Laya runtime, CADENCE sweeps, |
| #750 | 1.97 | EXTRACT | bot-observe, minesweeper-title | fix(core, dashboard): add fallback imports for req |
| #752 | 1.96 | HOLD | draft | feat(ops): Termux MCP endpoint status workflow + P |
| #761 | 1.75 | HOLD | draft | lane: Desktop Commander fork + Android execution a |
| #762 | 1.75 | HOLD | draft | ops: map live plugin connector surface and parity  |
| #764 | 1.74 | HOLD | draft | lane: connect Termux hub over Tailscale + repeatab |
| #788 | 1.01 | HOLD | wrong-base:master-staging | test(archwiz): Linear client/sync coverage + Triag |
| #816 | 0.02 | EXTRACT | state:unknown, minesweeper-title | fix(dashboard): Tribute XSS escape + /matrix nav a |
| #47 | 50.24 | OBSERVE | ancient-no-auto-promote | feat(refTemplates): restore metadata-only skeleton |
| #67 | 49.14 | OBSERVE | ancient-no-auto-promote | docs(ops): PR scope discipline — why src/db.py is  |
| #81 | 47.98 | OBSERVE | ancient-no-auto-promote | ci: promote Gemini quota-gate + agent workflows to |
| #92 | 47.28 | OBSERVE | bot-observe | sec(workflows): harden permissions, pin SHAs, and  |
| #103 | 46.85 | OBSERVE | ancient-no-auto-promote | feat(comms): CAVEMAN-micro seed + success matrix + |
| #125 | 45.95 | OBSERVE | bot-observe | analyze agentic workflows and peer coordination ru |
| #140 | 45.59 | OBSERVE | bot-observe | 🎨 Palette: Stateful & Reactive PWA UX with Manual  |
| #143 | 45.25 | OBSERVE | bot-observe | Integrate MCP Agent Mail Coordination Layer in Git |
| #249 | 36.85 | OBSERVE | state:unknown | docs(teams): add roster, game-player, and context  |
| #263 | 36.56 | OBSERVE | state:unknown | Manus/context relationship graph |
| #311 | 33.74 | OBSERVE | state:unknown | feat(sync): govern GitLab reconciliation instead o |
| #390 | 27.63 | OBSERVE | bot-observe | docs: formalize category-theoretic notation sets a |
| #402 | 26.58 | OBSERVE | bot-observe | 🛡️ Sentinel: Fix symlink hijacking vulnerability o |
| #404 | 26.05 | OBSERVE | state:unknown | sec(sentinel): skip chmod when cache/db/log path i |
| #407 | 25.56 | OBSERVE | bot-observe | ⚡ Bolt: optimize Bellman-Ford graph search in arbi |

Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote.
