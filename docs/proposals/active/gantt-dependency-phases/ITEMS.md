# Work Items — gantt-dependency-phases

**Status refresh:** 2026-09-25 (evidence-led; master tip `37ac2dce`)

| ID | Priority | Status | Scope | Acceptance criteria | Evidence |
|---|---:|---|---|---|---|
| DPH-000 | P1 | **complete** | Canonical phase plan, deterministic lifecycle engine, validation, evidence model, Mermaid/Markdown projection, unit fixtures. | Invalid graph/identity/check configuration fails closed; evidence evaluation is deterministic; generated views contain no authoritative state. | PR #248 merged; generated `DEPENDENCY_PHASES.md` reports complete; linked PR #900 lineage; required checks + Project Done agree. |
| DPH-010 | P1 | executing | Correct the reference DAG planner's concurrent dependency-wave projection following #1459. | Every emitted node appears in exactly one sorted wave; prerequisites precede dependents; lexical topological order and cycle residuals remain deterministic; focused tests and dual gates pass. | Follow-up to #1443/#1459; offline-only planning, no execution, dispatch, or Project mutation. |
| DPH-020 | P1 | executing | Fail closed on non-boolean phase approval evidence. | Mapping-based approvals admit only literal boolean `true`, whether direct or in an `approved` field; false, missing, strings, numbers, and containers remain blocked; legacy explicit phase-ID lists retain compatibility; lifecycle tests and exact-head dual gates pass. | Reproduced `"false"`, `"pending"`, `1`, and nested non-booleans incorrectly admitting DPH-100. No approval records, dispatch, Project state, or protection settings are changed. |
| DPH-100 | P1 | **ready** | GitHub Project #1 adapter and reconciliation flow. | Live Project discovery works; phase-to-item mapping is explicit; dry run is default; `--apply` is the only mutation path; Project status is a derived view. Operator-token precedence for Project writes. | Engine + adapter on master; generated view reports **ready**; Project sync workflows present (`dependency-phase-project-sync.yml`). Claim permitted when evidence current. |
| DPH-200 | P1 | waiting | Idempotent claim and controlled agent-dispatch handoff. | A ready phase creates at most one claim per plan hash; dispatcher revalidates live state; unapproved/waiting/active phases do not dispatch. | Depends on DPH-100 claim/completion. Workflow `dependency-phase-dispatch.yml` present; Jules gated on secret. |
| DPH-300 | P2 | waiting | Actions workflows, reconciliation report, documentation, and runbooks; derived timeline adapters. | Workflows use minimal permissions and safe triggers; PR validation read-only; reconciliation cannot auto-merge, close proposals, or update submodules. | Core workflows landed with #248; further derived Gantt polish via #717/#774. Awaits DPH-200. |

## Notes

- Statuses above are **proposal-item status**, aligned to the live evaluator where evidence exists. The evaluator remains the runtime authority for dispatch eligibility.
- Do not mark a phase complete from this table alone — completion requires matching merged PR, required checks, and Project `Done` when configured.
- Next human/agent action surface: claim + apply for DPH-100 when Operator credentials have Projects write, then progress DPH-200.
