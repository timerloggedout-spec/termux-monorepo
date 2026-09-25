---
id: gantt-dependency-phases
title: "Dependency-phase automation and GitHub Projects integration"
author: Manus AI
posted_at: 2026-08-18
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: Manus AI
    role: executor
    status: executing
related_prs: [248, 252, 253, 254, 257, 717, 774]
related_branches:
  - master
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — gantt-dependency-phases

## Summary

Implement a repository-native dependency-phase system that derives lifecycle state from a versioned phase plan, GitHub Project items, pull-request/check evidence, explicit approval records, and idempotent claims. Mermaid and Markdown reports are derived inspection views; they do not control dispatch or completion.

**Live entry:** [`docs/agentic/README.md`](../../../agentic/README.md)  
**Canonical plan:** [`docs/agentic/dependency-phases.json`](../../../agentic/dependency-phases.json)  
**Generated status:** [`docs/agentic/DEPENDENCY_PHASES.md`](../../../agentic/DEPENDENCY_PHASES.md)

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | accepted | 2026-08-18 | Authorized full implementation after evaluation clarified that a Mermaid view is illustrative only. |
| Manus AI | executor | executing | 2026-08-19 | Deployed the lifecycle system and its live-reconciliation hardening on the governing `master` branch. |

## Review log

### 2026-08-18 — Manus AI

- Disposition: accepted
- Notes: The live project is user-owned Project #1 (`PVT_kwHODennMc4BfLt5`), with `Todo`, `In progress`, and `Done` status options. The implementation resolves this metadata from the canonical plan and provides dry-run-default synchronization.

### 2026-08-18 — Manus AI

- Disposition: in_review
- Notes: The full implementation passed `repo_gate.py --base origin/master-staging` and `termux_smoke.py`, with seven lifecycle/adapter unit tests passing. The live dry-run identified the canonical Project mapping. Issue #246 (`DPH-000`) and issue #247 (`DPH-100`) were created during reconciliation attempts; the authenticated integration token can read but lacks permission to add items to the user-owned Project. The existing Operator-token chain must therefore be selected for Project writes and have Projects write permission. Pull request #248 is open against `master-staging`.

### 2026-08-19 — Manus AI

- Disposition: executing
- Notes: PR #248 merged the canonical lifecycle engine and four master-governed workflows. Follow-up PRs #252, #253, #254, and #257 respectively hardened read retries, replaced a timing-out GraphQL PR aggregate with targeted REST evidence, made issue creation use a structured REST response, and selected the Project-capable Operator credential for ProjectV2 writes.
- Evidence: Applied reconciliation run [32220381734](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/32220381734) completed successfully. It reconciled the four canonical phase issues (#246, #247, #255, and #259) as distinct items in user-owned Project #1, all currently `Todo`.
- Governance: No phase was marked complete solely from Project status, no approval evidence was modified, and no proposal or phase issue was closed automatically.

### 2026-09-23 — Grok (Administrator)

- Disposition: executing (partial terminal)
- Notes: Derived Gantt / dependency-waves projection consolidated via #717; post-merge adaptive-wait verify #774 (report plan_sha256 + mermaid test). Generated status shows DPH-000 **complete**, DPH-100 **ready**.

### 2026-09-25 — Grok (Administrator)

- Disposition: docs upgrade (this PR)
- Notes: Evidence-led consolidation of stale design/ITEMS/backlog surfaces. Top-level `docs/GANTT_DEPENDENCY_PHASES_ACTIONS_DESIGN.md` marked historical/implemented. ITEMS statuses aligned to live evaluator evidence. No runtime mutation; no auto-close of proposal.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [x] Code and workflow review completed
- [x] PR #248 opened with item references
- [x] Gates green on merge
- [x] Core engine + workflows on master
- [ ] DPH-100 claimed/applied under Operator Project write credential (when ready)
- [ ] Closed + moved to `closed/` when all terminal items complete

## Links

- ITEMS: ./ITEMS.md
- Live system: ../../../agentic/README.md
- Design (historical): ../../../GANTT_DEPENDENCY_PHASES_ACTIONS_DESIGN.md
