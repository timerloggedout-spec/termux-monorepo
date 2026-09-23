---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin ops on timerloggedout-spec/termux-monorepo. Load every admin session.
---

Local mirror. Canonical is master `.agents/skills/evidence-led-monorepo-ops/SKILL.md`.

Session 2026-09-23 10:37 PDT:
- Live master: `eb4849ce`
- Connector identity: `timerloggedout-spec` (GitHub MCP write path available)
- #184 names only: ARCHWIZ_GITHUB_TOKEN || OPERATOR_GITHUB_TOKEN live in Actions secrets. Never commit values.
- HOLD retired. Dual-gate + rebase before promote. AVOID HITL YOLO YEET AUTOAPPROVE.
- #175 north star. #48 / #69 remain EXTRACT (wrong-base / feature-base).
- #772: Vercel rate-limit is non-gate; mergeable_state may flap.
- Promote slimmest extract only after `hygiene + portability gate` and `agentic termux smoke` SUCCESS.

Agent-Identity: Grok (Administrator)
