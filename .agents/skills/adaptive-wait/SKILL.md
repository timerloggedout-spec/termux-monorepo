---
name: adaptive-wait
description: Adaptive WAIT for agentic GitHub ops. Dual-gate before promote. Stay busy on disjoint work.
---

# Skill: adaptive-wait

**Owner:** Grok Administrator
**Complements:** evidence-led-monorepo-ops, help-wanted-lane, approxination-lane

While one PR's checks run: preserve immutable IDs; work on a disjoint path; do not idle.
Promote only when dual gates success, extract-clean scope, and task outcome verified.

## Failure / stall classes

| Class | Severity | Notes |
|-------|----------|-------|
| comment-storm | FAILURE | Do not comment-storm ledgers. |
| dual-gate red | FAILURE | Block promote |
| extra-red | FAILURE (non-gate) | #608 ledger; one ledger job on #617 |
| dirty-behind-master | STALL | #601/#549/#432 ML |
| update-branch-conflict | STALL | Extract-later |

## Session 2026-09-18T23:15Z

- Live master `fb382c48`.
- Dispatched `help-wanted-scout.yml` on master (disjoint while #617 checks settle).
- Do not merge #617 until ledger extra-red classified and dual-gate green.
- Requested Copilot review on #617 (no issue comment-storm).

BIUDL. Agent-Identity: Grok (Administrator)
