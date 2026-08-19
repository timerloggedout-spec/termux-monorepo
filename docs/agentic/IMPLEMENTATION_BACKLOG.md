# Dependency-Phase Implementation Backlog

**Status:** Proposed backlog. It is not registered as an active proposal, does not authorize work, and does not change existing workflow behavior.

The items are deliberately ordered so that policy and deterministic validation are reviewable before any agent-launch capability exists. Each implementation item should become a separate PR against `master-staging`, cite its item ID, use the repository’s agent identity conventions where applicable, and pass `git diff --check`, `repo-gate`, `termux-smoke`, and the smallest relevant test.

| Order | Proposed item | Dependency | Deliverable | Explicit exclusion |
|---:|---|---|---|---|
| 1 | **DPH-00-01 — Adopt canonical phase contract** | Human approval | Promote/revise the draft example into a reviewed canonical YAML plan and freeze schema version 1. | Workflow changes, submodule changes, agent launch. |
| 2 | **DPH-00-02 — Implement pure validator** | DPH-00-01 | Parser, schema validation, duplicate/unknown/cycle checks, topological output, and fixtures. | GitHub writes or external service calls. |
| 3 | **DPH-10-01 — Add read-only evaluator** | DPH-00-02 | A deterministic report that combines plan state with PR/check/item evidence. | Labels, comments, dispatches, merge/close actions. |
| 4 | **DPH-20-01 — Add controlled phase-ready dispatcher** | DPH-10-01 plus human approval | Revalidation, plan-hash idempotency, one phase claim, and approved agent-launch adapter. | Automatic merge, proposal closure, submodule pointer updates. |
| 5 | **DPH-20-02 — Add recovery/reconciliation report** | DPH-20-01 | Bounded report for stale claims, failed checks, and missed event diagnosis. | Automatic retries or high-frequency polling. |
| 6 | **DPH-30-01 — Add derived projection** | DPH-10-01 | Deterministic JSON/Markdown/Mermaid or ASCII view generated only from canonical plan/evaluator output. | Rendering as authority; mutable terminal UI in CI. |
| 7 | **DPH-40-01 — Evaluate Camshaft adapter portability** | DPH-30-01 | Pinned GanttML provenance, isolated build evidence, and fixture-parity comparison. | Importing an unpinned local path dependency. |
| 8 | **DPH-50-01 — Evaluate optional local visual board** | DPH-30-01 | Local-only status board proposal derived from ICM CCTV/GanTTY patterns. | Network exposure or GitHub Actions runtime requirement. |

## Required approval gates

No item may pass from design to implementation merely because a preceding item is marked complete in this document. The implementation PR must have an approved proposal/item context, applicable human approval evidence, and current required repository gates. The phase plan and GitHub Actions evaluator are expected to **report** such evidence, not replace the existing governance process.
