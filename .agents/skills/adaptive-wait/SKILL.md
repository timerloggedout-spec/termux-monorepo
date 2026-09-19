---
name: adaptive-wait
description: Adaptive WAIT for agentic GitHub ops. Dual-gate before promote. Stay busy on disjoint work.
---

# Skill: adaptive-wait

**Owner:** Grok Administrator
**Complements:** evidence-led-monorepo-ops, help-wanted-lane

Promote only when dual gates success, extract-clean scope, and task outcome verified.

## Session 2026-09-18T17:01 PDT

Master: `fb382c4893ff07f413b1834f633081081f6973d7`.

| PR | Dual-gate | Extra-red | Disposition |
|----|-----------|-----------|-------------|
| #617 | validate-registry SUCCESS | ledger SyntaxError | WAIT |
| #619 | hygiene/audit/smoke SUCCESS | ledger SyntaxError | WAIT |
| #620 | CodeQL + validate-PR SUCCESS | ledger SyntaxError | OBSERVE (Jules) |
| #608 | — | extra-red + behind | HOLD; extract later |
| #605 | — | behind `20de2a54` | OBSERVE Paper2Agent |

While WAIT: help-wanted scout + execute dry_run queued; skills record this session; do not idle; do not comment-storm.

MCP 403 on foreign issue comments / upstream PRs — execute via help-wanted-execute.yml.

BIUDL. Agent-Identity: Grok (Administrator)
