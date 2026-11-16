# Integration Intelligence

Integration Intelligence is the governed catalog and evidence boundary for external tools and research platforms used by `termux-monorepo`.

## Canonical files

- [Integration portfolio](INTEGRATION-PORTFOLIO.md) — dated readiness audit, evidence, blockers, and adoption roadmap.

- [Integration registry](INTEGRATION-REGISTRY.md) — human-readable capabilities, priorities, and adoption states.
- [Machine-readable registry](registry.json) — structured inventory for automation and cockpit consumers.
- [Adapter contract](ADAPTER-CONTRACT.md) — read/write boundaries, event normalization, provenance, and validation.
- [Event JSON Schema](schemas/integration-event.schema.json) — canonical normalized event envelope.
- [Superpowers design](../superpowers/specs/2026-11-02-integration-intelligence-design.md) and [implementation plan](../superpowers/plans/2026-11-02-integration-intelligence.md).
- [CEEL architecture](../superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md), [platform comparison](PLATFORM-COMPARISON.md), [event contract](CEEL-EVENT-CONTRACT.md), and [capability opportunity graph](capability-opportunity-graph.json).

## L3VERAGE Department\n\n[`../leverage/README.md`](../leverage/README.md) defines the intervention/mechanism discipline that consumes CEEL opportunities and submits bounded experiments to the existing DoE family. Integration Intelligence remains the authority for integration identity and events; L3VERAGE stores only mechanism definitions and lifecycle references, not provider records or run telemetry.\n\n## Authority model

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
