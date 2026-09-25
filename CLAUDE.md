# CLAUDE.md

**Primary Collaborator entry for this repository.** Load this first.

Root `AGENTS.md` is **deprecated** (Linguist / CedrLang / Jules compression stub only). Do not start from it. All hard rules and routing live here and in the governance sequence below.

Collaborators are addressed by **Role**, **Name**, and **Moniker** — not by a generic `AGENTS.md` catalog.

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

BIUDL is the repository's compounding development motion: a broad system view selects a focused lane; the lane is integrated and validated with attributable evidence; proven work is developed into production code; learning is synthesized back into the broad baseline.

Canonical chart: [`docs/architecture/AGENT-TEAM-CONTROL-PLANE.md`](docs/architecture/AGENT-TEAM-CONTROL-PLANE.md) + `.mmd`.

This is the **Fully Continuous Automated Development Evaluation Environment** posture: dual-gate before promote, evidence-led, adaptive-wait, no HITL YOLO / YEET / AUTOAPPROVE merges. Size ≠ quality; mega-PRs stay EXTRACT.

## Governance sequence (read in order)

1. **This file** — orientation + hard rules + BIUDL
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what is active
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
4. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — dual gates
5. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only edges
6. [`docs/ops/SKILLS-INVENTORY.md`](docs/ops/SKILLS-INVENTORY.md) — adaptive wait + ops skills
7. [`docs/ops/LANE-MATRIX.md`](docs/ops/LANE-MATRIX.md) — living session SSOT (rewrite every admin cycle)

Then route the task with **[`docs/icm/CLAUDE.md`](docs/icm/CLAUDE.md)** — one verified component or process card before loading deeper source.

## Hard rules

- Target **`master`** for integration work (base for small PRs may be `master-staging` when that lane is active).
- Both gates must pass before merge:
  - `python3 scripts/ci/repo_gate.py`
  - `python3 scripts/ci/termux_smoke.py`
- Do not invent work outside `docs/proposals/active/<id>/ITEMS.md` — add a row first.
- Cite `Implements: <ITEM-ID>` on PRs/commits.
- **No** wholesale merge of NO-GO mega-PRs (#2, #6) — extract-only.
- **No** Class 3/4 artifacts in git (session stores, browser profiles, tokens).
- Unposted chat is not consensus — write Review log or `DEBATE.md`.
- **AVOID HITL YOLO MODE YEET AUTOAPPROVE.** Dual-gate green + verified task outcome required.
- Credential inventory is **names-only** in issues (see #184). Never paste secret values.

## Preferred execution loop

```text
registry.yaml → pick todo item → branch from master
  → implement → PR with Implements: ID → dual gates green → merge
  → update ITEMS.md status
```

## Adaptive WAIT (ops)

After dispatch / commit / merge attempt:

1. **WAIT** is a stage — re-check jobs → steps → logs → artifacts.
2. Do concurrent non-conflicting work; do not treat `queued`/`in_progress` as terminal.
3. Stall classes: admission / queue / execution / effect / pagination / routing loop.
4. Promote only when dual gates green **and** task outcome verified.

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
| Dependency-phase system | `docs/agentic/README.md` |
| Credential names inventory | issue #184 (no values) |
| BIUDL control plane | `docs/architecture/AGENT-TEAM-CONTROL-PLANE.md` |
| Session SSOT schema | `docs/schemas/session-ssot.md` |
| Provider caps | `docs/schemas/provider-capabilities.md` |
| Linguist / CedrLang / Jules stub only | `AGENTS.md` (deprecated redirect) |

## ICM + RinDig reference pins (smods)

Shallow gitlinks under `refTemplates/smods/` — reference only, not runtime control plane:

| Pin | Role |
|-----|------|
| `content-agent-routing-promptbase_fork` | Layered `CLAUDE.md` → CONTEXT routing (one collaborator, selective load) |
| `cost-of-remembering_fork` | Filesystem-memory cost evidence (~97% fewer tokens) |
| `AuditEngine_fork` | Audit adapt surface |
| `icm-architect_fork` | ICM hierarchy / cards method |

Gitlink ops: `workflow_dispatch` on `.github/workflows/ops-gitlink-lego-fork.yml` pattern (or specialized pin workflows). Gates never init submodules.

## Security

Credential rotation and history rewrite require Operator (human) authorization. See `docs/SECURITY-REMEDIATION.md`. Inventory and last-used evidence live in issue **#184** (names only).

---

**Collaborator-Identity:** Grok (Administrator)  
**Style:** BIUDL · AVOID HITL YOLO MODE YEET AUTOAPPROVE · adaptive-wait · evidence-led  
**Status change (2026-09-21):** Root `AGENTS.md` folded into this file and marked deprecated. Jules / Linguist / CedrLang lanes: treat `AGENTS.md` as redirect-only; load `CLAUDE.md` first.  
**Status change (2026-09-25):** Collaborator / Role / Name / Moniker vocabulary affirmed; dependency-phase nav + #184 Projects note linked from `docs/agentic/`.
