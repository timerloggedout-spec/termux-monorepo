# Work Items — gantt-dependency-phases

**Status refresh:** 2026-10-03 (Operator-directed ALL DPH-*; Collaborator plan)

| ID | Priority | Status | Scope | Acceptance criteria | Evidence |
|---|---:|---|---|---|---|
| DPH-000 | P1 | **complete** | Canonical phase plan, lifecycle engine, validation, evidence model, Mermaid/Markdown projection, fixtures. | Invalid config fails closed; evaluation deterministic; generated views non-authoritative. | PR #248; `DEPENDENCY_PHASES.md` complete; #900 lineage; Project Done. |
| DPH-100 | P1 | **executing** | GitHub Project #1 adapter + reconciliation. | Live discovery; dry-run default; `--apply` only mutates; Operator-token precedence; status derived. | Engine + `dependency-phase-project-sync.yml` on master; approval in `phase-approvals.json`; Implements PR `feat/dph-all-collaborator-plan-20261003`; issue #247. |
| DPH-200 | P1 | **executing** | Idempotent claim + controlled dispatch handoff. | ≤1 claim per plan hash; revalidate live; no dispatch when not ready. | `dependency-phase-dispatch.yml` + route on master; approval recorded; Implements PR same branch; issue #255. |
| DPH-300 | P2 | **executing** | Workflows, reconciliation report, Collaborator runbook, derived timeline. | Minimal permissions; PR validate read-only; no auto-merge/close/submodule. | Workflows + #717/#774 on master; `COLLABORATOR-DPH-PLAN.md`; Implements PR same branch; issue #259. |

## Notes

- **executing** means implementation evidence is on master or in the open Implements PR; terminal **complete** requires merged PR + dual-gate + Project Done agreement.
- Collaborator runbook: [`docs/agentic/COLLABORATOR-DPH-PLAN.md`](../../../agentic/COLLABORATOR-DPH-PLAN.md)
- Do not mark complete from this table alone.
