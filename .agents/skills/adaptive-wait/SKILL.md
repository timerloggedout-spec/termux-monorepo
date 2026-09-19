---
name: adaptive-wait
description: Adaptive WAIT for agentic GitHub ops. Dual-gate before promote. Stay busy on disjoint work.
---

# Skill: adaptive-wait

**Canonical:** `.agents/skills/adaptive-wait/SKILL.md` on master.

## Dual-gate

Promote only when **both**:
1. mergeable_state is `clean` (not dirty / behind / blocked).
2. Required / hygiene checks are green (ignore Vercel hobby rate-limit + expired Devin trial as non-gates).

Otherwise HOLD / WAIT / observe. Do not force-merge dirty PRs.

## Session (2026-09-19 16:06 PDT)

- Master HEAD: `1715f2f2`.
- #648 dirty HOLD.
- #649 Jules observe (1-line quota doc).
- #641 dirty HOLD. #639 unstable WAIT. #608/#630 dirty observe.
- help-wanted-execute LIVE `Kilo-Org/agentic-path#25` dispatched this session.
- Prior execute GlassHaven/Haven#273 — do not double-claim same cycle.
- DioNanos/codex-termux#14 CLOSED — skip.
- Vercel hobby rate-limit 24h — not a merge blocker.
- Stay busy: session record + live external execute + no comment-storm.

Agent-Identity: Grok (Administrator)
