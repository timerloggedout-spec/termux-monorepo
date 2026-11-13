# CLAUDE.md

**Primary Collaborator entry for this repository.** Load this first.

Root `AGENTS.md` routes to [`moniker.md`](moniker.md), then this file. Read the moniker route for identity; use this file and the governance sequence below for operational rules.

Collaborators are addressed by **Role**, **Name**, and **Moniker** through the canonical moniker route.

## Authoring style — DO statements + Siglary

Apply [`docs/ops/DO-STATEMENT-MANDATE.md`](docs/ops/DO-STATEMENT-MANDATE.md) to new docs, skills, code comments, commit subjects/bodies, PR descriptions/comments, workflow prompts, and chat relays. Lead with the intended action, keep the signal dense, and attach receipts to state changes.

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
  └──────────────→ BROAD (improved baseline)
```

BIUDL is the compounding development motion: a broad system view selects a focused lane; the lane is integrated and validated with attributable evidence; proven work is developed into production; learning returns to the baseline.

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
- Add each work item to `docs/proposals/active/<id>/ITEMS.md` before implementation.
- Cite `Implements: <ITEM-ID>` on PRs/commits.
- Keep NO-GO mega-PRs (#2, #6) in EXTRACT-only state.
- Keep Class 3/4 artifacts outside git; route session stores, browser profiles, and tokens through approved private storage.
- Record consensus in the Review log or `DEBATE.md`; treat chat as source input until recorded.
- **Recon before relay/build** (owner order, 2026-10-27): do recon so you know what you're touching & building. Verify decisive claims against the live record (repo contents, API, run/issue records) before relaying a report or amending a mission from it — a lane's report is an input, not evidence.
- **Agent auto-promote** when dual-gate green **and** task outcome verified. Keep the loop moving through Actions, Codespaces, and self-host surfaces for work they can run.
- Keep credential inventory **names-only** in issues (see #184); route secret values through approved secret stores.

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
2. **Do concurrent non-conflicting work** until COMPLETE; keep `queued`/`in_progress` in WAIT and advance on terminal evidence.
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
| Dependency-phase system | `docs/agentic/README.md` |
| Credential names inventory | issue #184 (no values) |
| BIUDL control plane | `docs/architecture/AGENT-TEAM-CONTROL-PLANE.md` |
| Continuous capability discovery / DoE | `docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md` |
| FA-ADE / auto-promote | `docs/ops/REFTEMPLATES-CONSOLIDATION.md` |
| Session SSOT schema | `docs/schemas/session-ssot.md` |
| Provider caps | `docs/schemas/provider-capabilities.md` |
| Agent identity route | `AGENTS.md` → `moniker.md` → `docs/ops/AGENT-MONIKERS.md` |

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
**Style:** BIUDL · Continuous Fully Automated Agentic Development (FA-ADE) · agent auto-promote on dual-gate + task outcome · adaptive-wait · evidence-led
**Status change (2026-09-24):** FA-ADE realign — agents execute to completion; dual-gate is automated evidence; HITL only on AGENTIC-PERMISSIONS edges.
**Status change (2026-09-25):** Collaborator / Role / Name / Moniker vocabulary affirmed; dependency-phase nav + #184 Projects note linked from `docs/agentic/`.
**Prior (2026-09-21):** Root `AGENTS.md` folded into this file as a historical redirect record.

## Tool acquisition routes (owner, 2026-11-01)

Full text: `docs/ops/TOOL-ACQUISITION-ROUTES.md`. Summary for every install/download task:
① Exec network calls ride an approval system — "Site always allowed" is decided per host by card (precedents: api.github.com, api.mistral.ai, mcp.deepwiki.com). ② Silent failure mode: downloads from non-whitelisted hosts (storage.googleapis.com, googlechromelabs.github.io) die at write (curl rc23/EPERM, 0-byte) with ∅ card generated — never report "platform-impossible"; correct report = "host not whitelisted ∧ no card engaged; route via ③/④". ③ Browser-channel downloads persist (~/workspace/browser_downloads). ④ GitHub-artifact route via api.github.com (precedent dd04486c). ⑤ Precedent: go.tgz 66.9MB + Go tree landed 2026-10-27.


## Superpowers engineering workflow

Repository-local skill: `.agents/skills/superpowers/SKILL.md`. Load it for feature work, bug fixes, refactors, and non-trivial engineering changes. The upstream Superpowers methodology supplements this file; it does not override proposal authorization, ICM source ownership, `AGENTIC-PERMISSIONS.md`, dual gates, or adaptive WAIT.

Integration catalog and event contract: `docs/integrations/README.md`. Design and execution plan: `docs/superpowers/specs/2026-11-02-integration-intelligence-design.md` and `docs/superpowers/plans/2026-11-02-integration-intelligence.md`.


## Continuous Capability Evolution Laboratory (CEEL)

Start at docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md and follow its proposal work ledger. CEEL is the event-driven discovery and comparison lane across FOSS, external platforms and internal capabilities. It reuses the Integration Intelligence registry/event contract, DoE family/experiment schema, ATES, Delphi Oracle/EGM and proposal/dual-gate lifecycle. It creates no parallel scheduler, telemetry ledger, registry or merge authority. The initial platform cohort is Langfuse, PromptLayer, PostHog and Braintrust plus the native repository baseline; external capability claims remain unverified until pinned evidence exists. GitHub-native events are primary; bounded reconciliation is fallback. Weekly reporting is not the sensing mechanism.
