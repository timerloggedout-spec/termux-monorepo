# Dependency-Phase Automation

This directory contains a **repository-native lifecycle system** for dependency-ordered work. It integrates the canonical phase plan with GitHub Project #1, pull-request/check evidence, explicit approvals, idempotent claims, and GitHub Actions workflows.

> **Authority rule:** `dependency-phases.json`, current pull-request/check evidence, explicit approval evidence, and GitHub Project items jointly determine lifecycle state. Mermaid, Markdown, DeepWiki, dashboards, issue prose, and collaborator-generated summaries are derived views only.

## Navigation SSOT (start here)

| Need | Path |
|---|---|
| **This README** | Operator / Collaborator entry for the phase system |
| **All DPH-* Collaborator plan** | [`COLLABORATOR-DPH-PLAN.md`](COLLABORATOR-DPH-PLAN.md) |
| Canonical plan | [`dependency-phases.json`](dependency-phases.json) |
| Approvals | [`phase-approvals.json`](phase-approvals.json) |
| Generated status (do not edit) | [`DEPENDENCY_PHASES.md`](DEPENDENCY_PHASES.md) · [`dependency-phases.mmd`](dependency-phases.mmd) |
| Proposal + ITEMS | [`../proposals/active/gantt-dependency-phases/`](../proposals/active/gantt-dependency-phases/) |
| Historical design | [`../GANTT_DEPENDENCY_PHASES_ACTIONS_DESIGN.md`](../GANTT_DEPENDENCY_PHASES_ACTIONS_DESIGN.md) |
| Primary repo entry | [`../../CLAUDE.md`](../../CLAUDE.md) — **not** root `AGENTS.md` (deprecated) |

## Automations (live)

| Workflow | Role |
|---|---|
| `dependency-phase-validate.yml` | Schema / DAG / fixture validation (read-only; PR + dispatch) |
| `dependency-phase-evaluate.yml` | Read-only evaluation + artifact upload (schedule + dispatch) |
| `dependency-phase-project-sync.yml` | Dry-run default Project reconciliation; `--apply` only with Operator token |
| `dependency-phase-dispatch.yml` | Controlled claim + optional Jules handoff (`repository_dispatch` / manual) |

## Lifecycle rules (short)

| State | Permitted behavior |
|---|---|
| `waiting` / `blocked` | Report only |
| `ready` | One controlled claim allowed |
| `running` / `awaiting_review` | Observe; no duplicate launch |
| `complete` | Unlock dependents only when merged PR + checks + Project Done agree |

Full command reference, Project mapping, and dispatch contract: **[`COLLABORATOR-DPH-PLAN.md`](COLLABORATOR-DPH-PLAN.md)** and the remainder of this README's historical sections in git history / prior revisions. Prefer the Collaborator plan for day-to-day execution.

## Required checks before merge

```bash
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
python3 scripts/agentic/dependency_phases.py validate
python3 -m unittest discover -s tests -p 'test_*phase*.py'
```

## Naming

Collaborators = **Role** + **Name** + **Moniker**. Root `AGENTS.md` is deprecated redirect only.

## Credential routing (#184 names-only)

`OPERATOR_GITHUB_TOKEN` → `OPERATOR_TOKEN` → `ARCHWIZ_GITHUB_TOKEN` → `GITHUB_TOKEN` for Project-capable paths (project-sync prefers Operator first). Never paste secret values.

**Updated:** 2026-10-03 — ALL DPH-* Collaborator plan + approvals lane.
