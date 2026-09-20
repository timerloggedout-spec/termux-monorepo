---
name: recon-cycle
description: RECON → implement → WAIT → VALIDATE → RE-FETCH loop for operator sessions. Use with evidence-led-monorepo-ops and adaptive-wait. Triggers on recon, matrix pulse, continue, KEEP GOING.
---

# Skill: recon-cycle

## Loop

1. **RECON** — master SHA, open issues/PRs, Actions conclusions, Linear freshness, dirty vs unstable vs clean.
2. **IMPLEMENT** — smallest green extract; cite `Implements: <ITEM-ID>`.
3. **WAIT** — jobs are not terminal while queued/in_progress. Do disjoint work.
4. **VALIDATE** — dual-gate jobs + task outcome, not a green check badge alone.
5. **RE-FETCH** — never promote on a stale base SHA.
6. **REPEAT**.

## Stall classes

admission / queue / execution / effect / pagination / routing loop / minesweeper overlap.

## Comment hygiene

One matrix pulse on #175 per session. No comment-storm. No secret values.
