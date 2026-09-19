---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin ops on timerloggedout-spec/termux-monorepo. Load every admin session.
---

# Skill: evidence-led-monorepo-ops

**Canonical:** `.agents/skills/evidence-led-monorepo-ops/SKILL.md` on **master** (collaborator parity).  
Local `.grok/skills/` mirrors are convenience only.

**Load with:** `adaptive-wait` · `help-wanted-lane` · inventory `docs/ops/SKILLS-INVENTORY.md` · root `SKILLS.md`.

## Session anchors (2026-09-19 16:06 PDT)

- Master live: `1715f2f2124095779c8faa9223b8032ef1b7a8ea`.
- Dual-gate required for monorepo merges; external PRs follow target norms.
- #648 dirty HOLD (github-issue-pr-graph + AGENTS.md fold) — do not merge.
- #647 Vercel preview rate-limited (not a repo CI fail) — observe.
- #649 Jules 1-file audit — observe until dual-gate clean.
- #641 dirty HOLD. #639 unstable WAIT. #608/#630 dirty observe.
- Skills SSOT in-repo: `.agents/skills/*` + `.github/skills/*`.
- #175 priority matrix remains open P0 ops gate.

## Admin loop

1. Recon master HEAD + dual-gate + open PRs.
2. Prefer extract/promote over mega force-merge.
3. Help-wanted: claim once, skip closed, respect maintainer routing.
4. Record durable facts; no comment-storm.
5. Stay busy on disjoint work while WAIT lanes settle.

Agent-Identity: Grok (Administrator)
