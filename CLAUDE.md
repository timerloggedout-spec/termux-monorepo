# CLAUDE.md

**Primary Collaborator entry for this repository.** Load this first.

Use this file as the primary collaborator entry. `AGENTS.md` remains a Linguist / CedrLang / Jules compression projection; all hard rules and routing live here and in the governance sequence below.

Address collaborators by **Role**, **Name**, and **Moniker** through the repository role catalog.

## Posture — Fully Automated Agentic Development Environment (FA-ADE)

This repository is a **Continuous Fully Automated Agentic Development Environment**.

- Agents **execute to completion** on authorized lanes: implement, push, open/update PR, re-fetch checks, and **auto-promote when all required scope gates are green and the task outcome is verified**.
- **Adaptive-wait is concurrent work**: keep non-conflicting progress active while jobs run and route operator CLI actions through automation.
- **Scope-aware validation is automated evidence.** Promote on required-gate success and verified outcome (see `docs/ops/REFTEMPLATES-CONSOLIDATION.md`).
- **HITL** handles human-only edges in `docs/proposals/AGENTIC-PERMISSIONS.md` (credentials, history rewrite, Class 3/4 material); automated execution is the default development loop.
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
1a. [`architecture.md`](architecture.md) — repository-wide system taxonomy, directory map, and data-flow entry
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what is active
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
4. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repository and scope-specific gates
5. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only edges
6. [`docs/ops/SKILLS-INVENTORY.md`](docs/ops/SKILLS-INVENTORY.md) — adaptive wait + ops skills
7. [`docs/ops/LANE-MATRIX.md`](docs/ops/LANE-MATRIX.md) — living session SSOT (rewrite every admin cycle)

Then route the task with **[`docs/icm/CLAUDE.md`](docs/icm/CLAUDE.md)** — one verified component or process card before loading deeper source.

## Hard rules

- Target **`master`** for integration work. Use `master-staging` as a source reference for bounded extraction.
- Run `python3 scripts/ci/repo_gate.py` for every repository integration change.
- Run `python3 scripts/ci/termux_smoke.py` for Termux runtime, Android device, and Termux operational changes.
- Select additional domain gates from the owning proposal and changed subsystem.
- Register every work item in `docs/proposals/active/<id>/ITEMS.md` before execution.
- Cite `Implements: <ITEM-ID>` on PRs/commits.
- Extract NO-GO mega-PR work into independently reviewable slices.
- Store Class 3/4 artifacts in approved secure storage; keep git limited to reviewed source and metadata.
- Record consensus in the proposal Review log or `DEBATE.md`.
- **Recon before relay/build** (owner order, 2026-10-27): inspect the live repository, API, run, and issue records before relaying decisive claims or amending a mission. Use lane reports as leads for verification.
- **Agent auto-promote** when all required scope gates are green and the task outcome is verified. Route executable operator work through Actions / Codespaces / self-host surfaces.
- Record credential names only in issues (see #184); route secret values through approved secret stores.

## Preferred execution loop

```text
registry.yaml → pick todo item → branch from master
  → implement (automate surfaces: GHA, Codespaces, Docker, Render where applicable)
  → PR with Implements: ID → required scope gates green → auto-promote
  → update ITEMS.md status
```

## Adaptive WAIT (ops)

After dispatch / commit / merge attempt:

1. **WAIT** is a stage — re-check jobs → steps → logs → artifacts.
2. **Do concurrent non-conflicting work** until COMPLETE; classify `queued`/`in_progress` as pending and route human shell actions through approved automation.
3. Stall classes: admission / queue / execution / effect / pagination / routing loop.
4. Promote when all required scope gates are green **and** the task outcome is verified (FA-ADE auto-promote).

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
| Repository architecture | `architecture.md` |
| ICM task routing | `docs/icm/CLAUDE.md` |
| Skills + adaptive wait | `docs/ops/SKILLS-INVENTORY.md` |
| Session / lane SSOT | `docs/ops/LANE-MATRIX.md` |
| Dependency-phase system | `docs/agentic/README.md` |
| Credential names inventory | issue #184 (names-only) |
| BIUDL control plane | `docs/architecture/AGENT-TEAM-CONTROL-PLANE.md` |
| Continuous capability discovery / DoE | `docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md` |
| FA-ADE / auto-promote | `docs/ops/REFTEMPLATES-CONSOLIDATION.md` |
| Session SSOT schema | `docs/schemas/session-ssot.md` |
| Provider caps | `docs/schemas/provider-capabilities.md` |
| Linguist / CedrLang / Jules stub only | `AGENTS.md` (deprecated redirect) |

## ICM + RinDig reference pins (smods)

Shallow gitlinks under `refTemplates/smods/` — reference inputs; runtime control remains in the owning integration layer:

| Pin | Role |
|-----|------|
| `content-agent-routing-promptbase_fork` | Layered `CLAUDE.md` → CONTEXT routing (one collaborator, selective load) |
| `cost-of-remembering_fork` | Filesystem-memory cost evidence (~97% fewer tokens) |
| `AuditEngine_fork` | Audit adapt surface |
| `icm-architect_fork` | ICM hierarchy / cards method |

Gitlink ops: `workflow_dispatch` on `.github/workflows/ops-gitlink-lego-fork.yml` pattern (or specialized pin workflows). Gate workflows leave submodules uninitialized.

## Security

Credential rotation and history rewrite require Operator (human) authorization. See `docs/SECURITY-REMEDIATION.md`. Inventory and last-used evidence live in issue **#184** (names only).

---

**Collaborator-Identity:** Grok (Administrator)
**Style:** BIUDL · Continuous Fully Automated Agentic Development (FA-ADE) · agent auto-promote on dual-gate + task outcome · adaptive-wait · evidence-led
**Status change (2026-09-24):** FA-ADE realign — agents execute to completion; scope-aware gates provide automated evidence; HITL only on AGENTIC-PERMISSIONS edges.
**Status change (2026-09-25):** Collaborator / Role / Name / Moniker vocabulary affirmed; dependency-phase nav + #184 Projects note linked from `docs/agentic/`.
**Prior (2026-09-21):** Root `AGENTS.md` folded into this file and marked deprecated.

## Tool acquisition routes (owner, 2026-11-01)

Full text: `docs/ops/TOOL-ACQUISITION-ROUTES.md`. Summary for every install/download task:
① Route exec network calls through the approval system; evaluate each host through its access card (precedents: api.github.com, api.mistral.ai, mcp.deepwiki.com). ② For a blocked download, record the host and approval-card state, then select the browser-channel or GitHub-artifact route. ③ Browser-channel downloads persist (~/workspace/browser_downloads). ④ GitHub-artifact downloads use api.github.com (precedent dd04486c). ⑤ Precedent: go.tgz 66.9MB + Go tree landed 2026-10-27.


## Superpowers engineering workflow

Repository-local skill: `.agents/skills/superpowers/SKILL.md`. Load it for feature work, bug fixes, refactors, and non-trivial engineering changes. Apply upstream Superpowers methodology within proposal authorization, ICM source ownership, `AGENTIC-PERMISSIONS.md`, scope-aware gates, and adaptive WAIT.

Integration catalog and event contract: `docs/integrations/README.md`. Design and execution plan: `docs/superpowers/specs/2026-11-02-integration-intelligence-design.md` and `docs/superpowers/plans/2026-11-02-integration-intelligence.md`.


## Continuous Capability Evolution Laboratory (CEEL)

Start at docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md and follow its proposal work ledger. CEEL is the event-driven discovery and comparison lane across FOSS, external platforms and internal capabilities. It reuses the Integration Intelligence registry/event contract, DoE family/experiment schema, ATES, Delphi Oracle/EGM and proposal/scope-gate lifecycle. Use the existing scheduler, telemetry ledger, registry, and merge authority across the integrated lane. The initial platform cohort is Langfuse, PromptLayer, PostHog and Braintrust plus the native repository baseline; verify external capability claims through pinned evidence. GitHub-native events are primary; bounded reconciliation is fallback. Event-driven sensing supplies observations, and weekly reporting supplies a summary.


## Linguist / Siglary communication contract

Load `docs/ops/REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md` for repo-wide DO-first writing, CAVEMAN-6, and the registered operator set. Keep OPERATORS / GLYPHS / CHORDS distinct and preserve `N∅` as chat-only.
