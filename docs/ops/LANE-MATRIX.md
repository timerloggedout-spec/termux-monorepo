# LANE-MATRIX (living SSOT)

**Session:** 2026-09-20 18:05 PDT
**Agent-Identity:** Grok (Administrator)
**Live master:** `21034ef7` — BIFROST-006 codespace path (#671)
**Open PRs:** 76  |  **Open issues:** 109

Rewrite this file every admin session. Copilot is optional peer, not a promote gate. Size ≠ quality. Promote when dual-gate is green. Vercel rate-limit is non-gate.

## Age audit (as of 2026-09-21 ~01:04 UTC)

Oldest open PR is **#47** (2026-08-05) — **46 days**. Issue **#175** opened 2026-08-11 — **40 days** as the operator hub.

| Bucket | Days open | Count (approx) | Pattern |
|--------|-----------|----------------|---------|
| Ancient | ≥40d | ~12 | Pre-#175 backlog; non-master bases; Jules early |
| Stale | 20–39d | ~15 | Manus graph, OX-Alpha canaries, Sentinel v1, docs |
| Mid | 7–19d | ~20 | ML wholesale family, Grafana, Mermaid, skills records |
| Fresh | ≤6d | ~29 | Session records, #682 keep-alive, cadence, Jules tip |

### Ancient (≥40d) — first open PRs still waiting

| PR | Opened | Days | Title | Lane |
|----|--------|------|-------|------|
| #47 | 2026-08-05 | 46 | refTemplates metadata-only skeleton | OBSERVE / SUPERSEDED by later refTemplates work |
| #48 | 2026-08-05 | 46 | llm-api-hub + TER-71 (base: master-staging) | HOLD — wrong base |
| #65 | 2026-08-06 | 45 | Jules Palette telemetry | OBSERVE |
| #67 | 2026-08-06 | 45 | docs PR scope discipline CE-22 | OBSERVE |
| #69 | 2026-08-06 | 45 | DEBATE dock (base: feature branch) | HOLD — wrong base |
| #73 | 2026-08-07 | 44 | connectors bugs (non-master base) | HOLD |
| #81 | 2026-08-07 | 44 | Gemini quota-gate promote | OBSERVE |
| #92 | 2026-08-08 | 43 | sec workflows harden (Jules) | EXTRACT security slice |
| #103 | 2026-08-09 | 43 | CAVEMAN-micro seed | OBSERVE |
| #125 | 2026-08-09 | 42 | Jules agentic workflow analysis | OBSERVE |
| #140 | 2026-08-10 | 41 | Jules Palette PWA | OBSERVE |
| #143 | 2026-08-10 | 41 | MCP Agent Mail GHA (Jules) | OBSERVE → issue #117 |

### Tip-first active lanes

| PR | Days | Title | Lane | Why |
|----|------|-------|------|-----|
| #696/#697 | <1 | session skills records | WAIT | dual-gate; may supersede each other |
| #695 | <1 | AlphaEvolve + Dream-RSI Paper2Agent | OBSERVE | fresh |
| #693 | 1 | Linguist CedrLang alloc | OBSERVE | Jules |
| #685 | 1 | arrhythmic-zero-token-search | OBSERVE | proposal |
| #684 | 1 | unify Actions cadence | HOLD | dirty/stale |
| #682 | 1 | ML keep-alive DAG (#175) | WAIT / EXTRACT | rebase onto `21034ef7` |
| #680 | 1 | Bolt live_catalog_feed | OBSERVE | Jules |
| #679 | 1 | Sentinel telemetry symlink | WAIT | security extract |
| #630 | 2 | Jules dashboard rich UI (89-file) | EXTRACT | minesweeper |
| #608 | 2 | pr-production-ledger SyntaxError | WAIT | small fix if dual-gate |
| #601 | 3 | ML extract observe-mode | EXTRACT | superseded by #682 path |
| #549 | 5 | ML rebase observe-mode | EXTRACT | #175 family |
| #432 | 16 | ML observe-mode wholesale | EXTRACT | #175 family; do not merge |
| #263 | 32 | Manus context relationship graph | EXTRACT | mega; component slices only |

## Issue → PR map (priority hubs)

| Issue | Opened | Days | Role | Linked / implied PRs |
|-------|--------|------|------|----------------------|
| **#175** | 2026-08-11 | 40 | OPERATOR priority matrix + dual-gate | #432 #549 #601 #682 (ML); minesweeper #630 |
| #184 | 2026-08-12 | 39 | Credential inventory (notes only) | secrets hygiene PRs |
| #117 | 2026-08-09 | 42 | Agent2Agent / MCP Agent Mail | #143 |
| #88/#91/#94 | 2026-08-08 | 43 | OpenRouter / OmniRoute / routing | hub work #48 family |
| #21 | 2026-08-04 | 47 | Production backlog (oldest issue) | pre-matrix backlog |
| #50 | 2026-08-05 | 46 | termux-smoke / master-staging gate | dual-gate ancestry |
| TER-71 (Linear) | — | — | llm-api-hub | #48 |

## Dual-gate contract

1. `repo_gate` / hygiene+portability SUCCESS
2. `termux_smoke` SUCCESS
3. Vercel rate-limits are non-gate
4. Copilot / CodeRabbit / Qodo / Devin = advisory
5. GitLab / Mintlify = non-gate
6. Age alone does not promote; dual-gate + rebase does

## Operator rules on age

- **≥40d + wrong base** → HOLD or close-as-superseded after extract lands.
- **ML wholesale (#432/#549/#601)** → EXTRACT only; #682 is keep-alive.
- **Jules 40+ file dirty** → EXTRACT / minesweeper, never wholesale.
- **Session-record PRs** → WAIT dual-gate; close superseded siblings.
- Do not merge for file-count or age sympathy.

## Next cycle

1. Rebase #682 onto `21034ef7` → dual-gate → promote if green.
2. Close or supersede #47 if refTemplates path fully covered by #688/#692 lineage.
3. Leave #48/#69/#73 HOLD until retargeted to master.
4. Security EXTRACT from #92/#679 family when dual-gate green on a tip branch.
5. One pulse comment on #175 per session (this rewrite is the pulse).
