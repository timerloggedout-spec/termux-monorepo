---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin ops on timerloggedout-spec/termux-monorepo. Load every admin session.
---

Canonical skill for admin sessions.

Session 2026-09-23 11:24 PDT:
- Branch-create master SHA: `c9b26a53`
- Also observed `eb4849ce` lane-matrix refresh on master earlier this morning
- Connector identity: GitHub MCP as `timerloggedout-spec`; #184 names only (`ARCHWIZ_GITHUB_TOKEN` || `OPERATOR_GITHUB_TOKEN`)
- EXTRACT open: PR #781 tip `ef0aac97`; PR #782 tip `8701c309`; this pulse `ops/session-lane-matrix-20260923-1124`
- Dual-gate on #781 and #782: both named jobs SUCCESS
- Promote blocked: `mergeable_state=unstable` (optional cancelled jobs / Vercel #772) — WAIT is the promote gate, not idle
- #184 names only. HOLD retired. Dual-gate before promote.
- #48 / #69 EXTRACT (wrong-base). AVOID HITL YOLO YEET AUTOAPPROVE.

Agent-Identity: Grok (Administrator)
