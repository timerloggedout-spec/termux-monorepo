# Collaborator Plan — All DPH-* Phases

**Plan ID:** `gantt-dependency-phases`  
**Primary entry:** [`CLAUDE.md`](../../CLAUDE.md) (not root `AGENTS.md`)  
**Canonical plan:** [`dependency-phases.json`](dependency-phases.json)  
**Lifecycle entry:** [`README.md`](README.md)  
**Credentials (names-only):** issue **#184**

Collaborators are addressed by **Role**, **Name**, and **Moniker**.

> **Authority rule:** Plan JSON + PR/check evidence + explicit approvals + Project items determine lifecycle state. This document is a Collaborator runbook, not a second control plane.

---

## Phase lattice (all DPH-*)

```text
DPH-000 Foundation          → COMPLETE (engine + views; #248 / #900 lineage)
    ↓
DPH-100 Projects sync       → code on master; approval recorded; Implements PR closes item
    ↓
DPH-200 Idempotent dispatch → workflow on master; approval recorded; Implements PR closes item
    ↓
DPH-300 Derived timeline    → render/reconcile on master; Implements PR + runbook closes item
```

| Phase | Issue | Role focus | Preferred moniker path |
|-------|------:|------------|------------------------|
| DPH-000 | #246 | Foundation already landed | N/A (complete) |
| DPH-100 | #247 | Project reconciliation | Operator token → `sync-project` |
| DPH-200 | #255 | Claim + specialist route | `dispatch` → Jules when keyed |
| DPH-300 | #259 | Derived views + runbook | evaluate/render artifacts |

---

## What already exists on master (do not rebuild)

| Surface | Location |
|---------|----------|
| Plan + policy | `docs/agentic/dependency-phases.json` |
| Approvals file | `docs/agentic/phase-approvals.json` |
| CLI | `scripts/agentic/dependency_phases.py` |
| Engine / adapter / route | `scripts/agentic/dependency_phase_*.py` |
| Validate | `.github/workflows/dependency-phase-validate.yml` |
| Evaluate | `.github/workflows/dependency-phase-evaluate.yml` |
| Project sync | `.github/workflows/dependency-phase-project-sync.yml` |
| Dispatch | `.github/workflows/dependency-phase-dispatch.yml` |
| Dual gates | `repo-gate` + `termux-smoke` |

---

## Collaborator operating procedure

### 1. Orient

```bash
# From repo root
python3 scripts/agentic/dependency_phases.py validate
python3 scripts/agentic/dependency_phases.py --live --repo timerloggedout-spec/termux-monorepo evaluate
```

Read the Actions step summary or JSON: only **`ready`** phases may be claimed.

### 2. DPH-100 — Project sync

**Acceptance (code):** dry-run default; `--apply` only mutates; Operator-token precedence; Project status derived.

```bash
# Dry-run (default)
python3 scripts/agentic/dependency_phases.py \
  --live --repo timerloggedout-spec/termux-monorepo sync-project

# Apply only after reviewing operations JSON
python3 scripts/agentic/dependency_phases.py \
  --live --apply --repo timerloggedout-spec/termux-monorepo sync-project
```

**Actions path:** Actions → *Dependency Phase Project Sync* → `workflow_dispatch` with `apply=false` first, then `apply=true` when Operator secret has Projects write (#184 names-only).

### 3. DPH-200 — Idempotent dispatch

**Acceptance:** one claim per `PHASE_ID:PLAN_SHA256`; revalidate before claim; waiting/blocked/running never dispatch.

```bash
# Dry-run claim (canonical issue required — e.g. #247 for DPH-100 work items)
python3 scripts/agentic/dependency_phases.py \
  --live --repo timerloggedout-spec/termux-monorepo \
  dispatch --phase-id DPH-100 --issue 247
```

**Actions path:** *Dependency Phase Dispatch* on **master** only:

- `phase_id` = target phase
- `issue_number` = canonical phase issue
- `apply=false` first

Applied dispatch requires manager route provenance (`dependency_phase_route.py`). Jules invokes only when `JULES_API_KEY` is present and route selects `jules`.

### 4. DPH-300 — Derived timeline

**Acceptance:** Markdown/Mermaid/report generated from evaluator only; no authority in rendered files; workflows cannot auto-merge or close proposals.

```bash
python3 scripts/agentic/dependency_phases.py \
  --live --repo timerloggedout-spec/termux-monorepo \
  render \
  --markdown-output /tmp/DEPENDENCY_PHASES.md \
  --mermaid-output /tmp/dependency-phases.mmd
```

Scheduled evaluate (`cron: 23 5 * * *`) uploads artifacts; do not treat artifacts as merge authority.

### 5. Close a phase (completion evidence)

A phase becomes **complete** only when **all** hold:

1. Merged PR to `master` with `Implements: <PHASE_ID>`
2. Required checks: `repo-gate`, `termux-smoke`
3. Project item in **Done** (after sync-apply reflects complete)

Comments, Mermaid nodes, and approvals alone are insufficient.

---

## Prohibited (policy)

From `dependency-phases.json` policy:

- automatic_merge
- automatic_proposal_closure
- automatic_submodule_update
- approval_inference

**AVOID HITL YOLO MODE YEET AUTOAPPROVE.** Dual-gate green + verified outcome required.

---

## Secret names only (#184)

| Name | Use |
|------|-----|
| `OPERATOR_GITHUB_TOKEN` / `OPERATOR_TOKEN` / `ARCHWIZ_GITHUB_TOKEN` | Live evaluate, Project sync, dispatch revalidation |
| `JULES_API_KEY` | Optional post-claim Jules invoke |
| `GITHUB_TOKEN` | Final fallback (limited Project write) |

Never paste values into issues, PRs, or this file.

---

## Post-merge operator checklist

1. Dual-gate green on the Implements PR
2. Project sync dry-run → apply (status → Done for completed phases)
3. Evaluate workflow (or wait for schedule) refreshes readiness matrix
4. Optional: dispatch remaining ready work with dry-run first
5. When all DPH-* complete: proposal MANIFEST checklist → move to `closed/` under PROCESS.md

---

**Collaborator-Identity:** Grok (Administrator)  
**Style:** BIUDL · adaptive-wait · evidence-led  
**Updated:** 2026-10-03
