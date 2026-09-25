# Dependency-Phase Implementation Backlog

**Status:** HISTORICAL (post-land). Retained for provenance.

The original ordered backlog below guided PR #248 and follow-ups. The live system is documented in [`README.md`](README.md). New work should be registered via `docs/proposals/` rather than extending this file as authority.

| Order | Item | Outcome |
|---:|---|---|
| 1–3 | Canonical contract, pure validator, read-only evaluator | Delivered (PR #248) |
| 4–5 | Controlled dispatcher + recovery report | Delivered (workflows + claim path) |
| 6 | Derived projection (JSON/Markdown/Mermaid) | Delivered; waves + Gantt polish #717/#774 |
| 7 | Camshaft / GanttML adapter portability | Deferred — inspiration only; no unpinned path dep |
| 8 | Optional local visual board (ICM CCTV / GanTTY patterns) | Deferred — local-only; no CI/network exposure |

## Authority reminder

- Canonical plan: `dependency-phases.json`
- Generated views: `DEPENDENCY_PHASES.md`, `dependency-phases.mmd`, report artifacts — **not** authority
- Dispatch: re-evaluate live evidence; claim key `PHASE_ID:PLAN_SHA256`
- Prohibited: automatic merge, automatic proposal closure, automatic submodule update, approval inference

See also: [`docs/GANTT_DEPENDENCY_PHASES_ACTIONS_DESIGN.md`](../GANTT_DEPENDENCY_PHASES_ACTIONS_DESIGN.md) (historical design).
