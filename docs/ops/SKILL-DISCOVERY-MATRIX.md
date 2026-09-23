# Skill Discovery Matrix — adaptive wait + evidence-led repo ops

**Discovery basis:** current `master` plus the 2026-09-23 supplied skill packages and Wingman fork adoption.

| Cluster | Skill | Path | Role |
|---|---|---|---|
| Wait/control | adaptive-wait | `.agents/skills/adaptive-wait/SKILL.md` | asynchronous cadence, stall detection, promotion boundary |
| Feedback | adaptive-feedback-cycle | `.agents/skills/adaptive-feedback-cycle/SKILL.md` | continuous observation and feed-forward learning |
| Evidence/admin | evidence-led-monorepo-ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` | current-state reconstruction and provenance |
| Stewardship | termux-mcp-project-steward | `.agents/skills/termux-mcp-project-steward/SKILL.md` | constrained Termux/GitHub stewardship |
| Relationships | context-relationship-graph | `.agents/skills/context-relationship-graph/SKILL.md` | verified/candidate relationship evidence |
| Wingman | wingman-project-integration | `.agents/skills/wingman-project-integration/SKILL.md` | pinned fork reference, customization, and learnings |
| Reconciliation | production-reconciliation | `.github/skills/production-reconciliation/SKILL.md` | ref alignment and WAIT/VALIDATE/RE-FETCH |
| Measurement | action-effectiveness-ledger | `.github/skills/action-effectiveness-ledger/SKILL.md` | action-to-outcome measurement |
| Provenance | evidence-envelope / evidence-provenance | `.github/skills/evidence-envelope/SKILL.md` / `.github/skills/evidence-provenance/SKILL.md` | normalized evidence identity |
| Orchestration | workflow-orchestration | `.github/skills/workflow-orchestration/SKILL.md` | modular Actions and retry discipline |

## Adoption decisions

- `termux-mcp-project-steward.skill` → adopted as a repository-native `SKILL.md`.
- `context-relationship-graph_2.skill` → the current repository relationship-graph contract.
- The older duplicate `context-relationship-graph.skill` remains reference-only.
- Loopy bounded Observe → Choose → Act → Verify → Record → Repeat semantics are adapted into the repository loop; no external runtime is required.
- `timerloggedout-spec/Wingman_fork` is pinned at `a6d5cea2d48009b5555e138c8d6b8f620388fb1b` as a reference/customization/template resource.

Promotion remains downstream of current-SHA task-outcome verification and the repository dual gates.
