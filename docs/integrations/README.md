# Integration Intelligence

Integration Intelligence is the governed catalog and evidence boundary for external tools and research platforms used by `termux-monorepo`.

## Canonical files

- [Integration portfolio](INTEGRATION-PORTFOLIO.md) — dated readiness audit, evidence, blockers, and adoption roadmap.

- [Integration registry](INTEGRATION-REGISTRY.md) — human-readable capabilities, priorities, and adoption states.
- [Machine-readable registry](registry.json) — structured inventory for automation and cockpit consumers.
- [Adapter contract](ADAPTER-CONTRACT.md) — read/write boundaries, event normalization, provenance, and validation.
- [Event JSON Schema](schemas/integration-event.schema.json) — canonical normalized event envelope.
- [Superpowers design](../superpowers/specs/2026-11-02-integration-intelligence-design.md) and [implementation plan](../superpowers/plans/2026-11-02-integration-intelligence.md).

## Authority model

Repository files, Git history, CI results, and approved proposal records remain authoritative for repository state. External services are providers of bounded observations or operations. A connector visible in one ChatGPT session is not evidence of availability to Termux, GitHub Actions, another collaborator, or production.

The registry intentionally separates:
- discovery evidence;
- current-session tool/skill availability;
- repository adapter implementation;
- end-to-end validation;
- production promotion.

## Operating loop

`RECON → PLAN → IMPLEMENT → TEST → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → RECORD → REPEAT`

No provider adapter may bypass the repository's proposal lifecycle, permission model, secret handling, or dual gates.
