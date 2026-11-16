---
id: model-selection-market
title: "Model selection market — equal-weight bootstrap, 3L0 performance, DSPy-DoE, bets/trading-cards"
author: grok
posted_at: 2026-10-01
source: operator-session-BIUDL-2026-09-30
status: posted
priority: P1
reviewers:
  - id: grok
    role: author+executor
    status: executing
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_prs: []
related_branches:
  - docs/model-selection-market-3l0-20261001
related_proposals:
  - approxination-integration
  - ml-keep-alive
  - rate-limit-rotation
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — model-selection-market

## Summary

Unify free-tier model selection under an **equal-weight bootstrap → evidence-weighted** path.
Public leaderboards remain **features**; repository-local 3L0 / ELO++ success matrix remains **labels**.
Add explicit **series | parallel | concurrent** selection modes, a **DSPy DoE-MVT consideration lane**
(under Approxination affinity, not default router), and an observational **Bets|Wagers|Bids**
market (Itself|Others|Job) with **trading-card** code/meta sharing and a total role×model×job graph.

## Boundary

- Free-tier only. Never paid routes on exhaustion path.
- Observe-first: two controlled observe cycles + Issue #192-class ledger decision before active weight mutation.
- DSPy is **consideration / DoE only** — not model-router primary.
- Bets are ledgered and observational until policy promotes; no silent quota spend.
- Trading cards hold no secrets (#184 names-only).
- Thin extracts only. No mega-PR. Dual-gate before promote. AVOID HITL YOLO YEET AUTOAPPROVE.

## Authority chain (unchanged)

1. Hard eligibility (capability, free rule, quota, SHA when required)
2. Soft budgets (`model-rotation.yaml` + model-router action)
3. Success matrix / 3L0 labels (`model-success-matrix.yaml`)
4. MoneyBall / lane short-circuit (decision support, not sole gate)
5. Dual-gate + Canny facts-only hard-block

## Evidence

- `docs/schemas/model-rotation.yaml`
- `docs/schemas/llm-leaderboard-matrix.yaml`
- `docs/schemas/model-success-matrix.yaml`
- `docs/ops/DECISION-ENGINES.md` + `DECISION-CRITERIA-MATRIX.md`
- `docs/ops/ROUTING-LOGIC-CHAIN.md`
- `docs/ops/APPROXINATION-LANE.md`
- CLAUDE.md FA-ADE + BIUDL

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges of runtime code
- [ ] PRs cite `Implements: <ITEM-ID>`
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Design SSOT: ./DESIGN.md
- Schemas sketch: ./schemas/
