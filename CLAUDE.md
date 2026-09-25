# CLAUDE.md

**Primary agent entry for this repository.** Load this first.

Root `AGENTS.md` is **deprecated** (Linguist / CedrLang / Jules compression stub only). Do not start from it. All hard rules and routing live here and in the governance sequence below.

## Posture — Fully Automated Agentic Development Environment (FA-ADE)

This repository is a **Continuous Fully Automated Agentic Development Environment**.

- Agents **execute to completion** on authorized lanes: implement, push, open/update PR, re-fetch checks, and **auto-promote when dual gates are green and the task outcome is verified**.
- **Adaptive-wait is concurrent work**, not idle handoff. While jobs run, do non-conflicting progress; do not emit operator CLI homework as a substitute for automation.
- **Dual-gate is automated evidence**, not a human gatekeeping ritual. Promote on green + verified outcome (see `docs/ops/REFTEMPLATES-CONSOLIDATION.md`).
- **HITL** is reserved for human-only edges in `docs/proposals/AGENTIC-PERMISSIONS.md` (credentials, history rewrite, Class 3/4 material). It is not the default development loop.
- Size ≠ quality; mega-PRs stay **EXTRACT**.

Canonical chart: [`docs/architecture/AGENT-TEAM-CONTROL-PLANE.md`](docs/architecture/AGENT-TEAM-CONTROL-PLANE.md) + `.mmd`.

Regression guard: `.github/workflows/orchestration-regression-guard.yml` asserts FA-ADE markers in this file remain aligned.

## BIUDL — operating motion

**BIUDL = Broad → Integrate → Validate → Develop → Learn.**

```text
BROAD
  ↓
INTEGRATE
  ↓
VALIDATE
  ↓
DEVELOP
  ↓
LEARN
  └────────────────→ BROAD (improved baseline)
```

BIUDL is the compounding development motion: broad system view selects a focused lane; the lane is integrated and validated with attributable evidence; proven work is developed into production; learning returns to the baseline.

## Governance sequence (read in order)

1. **This file** — orientation + hard rules + BIUDL + FA-ADE
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what is active
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
4. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — dual gates (automated)
5. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only edges
6. [`docs/ops/SKILLS-INVENTORY.md`](docs/ops/SKILLS-INVENTORY.md) — adaptive wait + ops skills
7. [`docs/ops/LANE-MATRIX.md`](docs/ops/LANE-MATRIX.md) — living session SSOT (rewrite every admin cycle)

Then route the task with **[`docs/icm/CLAUDE.md`](docs/icm/CLAUDE.md)** — one verified component or process card before loading deeper source.

## Hard rules

- Target **`master`** for integration work (base for small PRs may be `master-staging` when that lane is active).
- Both gates must pass before promote (automated CI + local parity):
  - `python3 scripts/ci/repo_gate.py`
  - `python3 scripts/ci/termux_smoke.py`
- Do not invent work outside `docs/proposals/active/<id>/ITEMS.md` — add a row first.
- Cite `Implements: <ITEM-ID>` on PRs/commits.
- **No** wholesale merge of NO-GO mega-PRs (#2, #6) — extract-only.
- **No** Class 3/4 artifacts in git (session stores, browser profiles, tokens).
- Unposted chat is not consensus — write Review log or `DEBATE.md`.
- **Agent auto-promote** when dual-gate green **and** task outcome verified. Do not block the loop on operator CLI steps that Actions / Codespaces / self-host surfaces can run.

## Preferred execution loop

```text
registry.yaml → pick todo item → branch from master
  → implement (automate surfaces: GHA, Codespaces, Docker, Render where applicable)
  → PR with Implements: ID → dual gates green → auto-promote
  → update ITEMS.md status
```

## Adaptive WAIT (ops)

After dispatch / commit / merge attempt:

1. **WAIT** is a stage — re-check jobs → steps → logs → artifacts.
2. **Do concurrent non-conflicting work** until COMPLETE; do not treat `queued`/`in_progress` as terminal and do not park the lane on human shell commands.
3. Stall classes: admission / queue / execution / effect / pagination / routing loop.
4. Promote when dual gates green **and** task outcome verified (FA-ADE auto-promote).

Canonical skill: `.agents/skills/adaptive-feedback-cycle/SKILL.md`  
Companion: `.github/skills/production-reconciliation/SKILL.md` (WAIT → VALIDATE → RE-FETCH)  
Inventory: [`docs/ops/SKILLS-INVENTORY.md`](docs/ops/SKILLS-INVENTORY.md)

## Quick pointers

| Need | Path |
|------|------|
| Active work | `docs/proposals/registry.yaml` |
| How to review / close | `docs/proposals/PROCESS.md` |
| Gates | `docs/ARCHW1Z-GATE.md` |
| Status | `docs/ARCHW1Z-STATUS.md` |
| Permissions / human edges | `docs/proposals/AGENTIC-PERMISSIONS.md` |
| ICM task routing | `docs/icm/CLAUDE.md` |
| Skills + adaptive wait | `docs/ops/SKILLS-INVENTORY.md` |
| Session / lane SSOT | `docs/ops/LANE-MATRIX.md` |
| BIUDL control plane | `docs/architecture/AGENT-TEAM-CONTROL-PLANE.md` |
| FA-ADE / auto-promote | `docs/ops/REFTEMPLATES-CONSOLIDATION.md` |
| Session SSOT schema | `docs/schemas/session-ssot.md` |
| Provider caps | `docs/schemas/provider-capabilities.md` |
| Linguist / CedrLang / Jules stub only | `AGENTS.md` (deprecated redirect) |

## ICM + RinDig reference pins (smods)

Shallow gitlinks under `refTemplates/smods/` — reference only, not runtime control plane:

| Pin | Role |
|-----|------|
| `content-agent-routing-promptbase_fork` | Layered `CLAUDE.md` → CONTEXT routing (one agent, selective load) |
| `cost-of-remembering_fork` | Filesystem-memory cost evidence (~97% fewer tokens) |
| `AuditEngine_fork` | Audit adapt surface |
| `icm-architect_fork` | ICM hierarchy / cards method |

Gitlink ops: `workflow_dispatch` on `.github/workflows/ops-gitlink-lego-fork.yml` pattern (or specialized pin workflows). Gates never init submodules.

## Security

Credential rotation and history rewrite require Operator (human) authorization. See `docs/SECURITY-REMEDIATION.md`.

---

**Agent-Identity:** Grok (Administrator)  
**Style:** BIUDL · Continuous Fully Automated Agentic Development (FA-ADE) · agent auto-promote on dual-gate + task outcome · adaptive-wait · evidence-led  
**Status change (2026-09-24):** FA-ADE realign — agents execute to completion; dual-gate is automated evidence; HITL only on AGENTIC-PERMISSIONS edges.  
**Prior (2026-09-21):** Root `AGENTS.md` folded into this file and marked deprecated.
