# Integration Intelligence

Integration Intelligence is the governed catalog and evidence boundary for external tools and research platforms used by `termux-monorepo`.

## Canonical files

- [Integration portfolio](INTEGRATION-PORTFOLIO.md) — dated readiness audit, evidence, blockers, and adoption roadmap.

- [Integration registry](INTEGRATION-REGISTRY.md) — human-readable capabilities, priorities, and adoption states.
- [Machine-readable registry](registry.json) — structured inventory for automation and cockpit consumers.
- [Adapter contract](ADAPTER-CONTRACT.md) — read/write boundaries, event normalization, provenance, and validation.
- [Event JSON Schema](schemas/integration-event.schema.json) — canonical normalized event envelope.
- [Superpowers design](../superpowers/specs/2026-11-02-integration-intelligence-design.md) and [implementation plan](../superpowers/plans/2026-11-02-integration-intelligence.md).
- [CEEL architecture](../superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md), [platform comparison](PLATFORM-COMPARISON.md), [event contract](CEEL-EVENT-CONTRACT.md), and [capability opportunity graph](capability-opportunity-graph.json).\n- [Capability discovery and activation](../ops/CAPABILITY-DISCOVERY-AND-ACTIVATION.md) — nested source discovery, hierarchical tagging, metadata-first loading, trust classification and DoE routing.\n- [Capability source registry](../../ops/capability_discovery/sources.json) and [taxonomy](../../ops/capability_discovery/taxonomy.json) — machine-readable discovery sources and classification.\n- [Session plugin skill catalog](session-plugin-skill-catalog.json) — 545 skill references across 74 packages, captured 2026-11-19.\n- [Session tool action catalog](session-tool-action-catalog.json) — 4,716 actions, including 4,706 MCP actions across 123 MCP namespaces, captured 2026-11-19.

## Authority model

Repository files, Git history, CI results, and approved proposal records remain authoritative for repository state. External services are providers of bounded observations or operations. A connector visible in one ChatGPT session is not evidence of availability to Termux, GitHub Actions, another collaborator, or production. The session catalogs are compact, dated discovery snapshots; full live schemas, permissions and output contracts must be read from the active tool host at invocation.

The registry intentionally separates:\n- local canonical definitions;\n- external vendor/community candidates;\n- session-observed plugin skills and tool actions;\n- repository adapter implementation and authorization;
- discovery evidence;
- current-session tool/skill availability;
- repository adapter implementation;
- end-to-end validation;
- production promotion.

## Operating loop

`RECON → PLAN → IMPLEMENT → TEST → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → RECORD → REPEAT`

No provider adapter may bypass the repository's proposal lifecycle, permission model, secret handling, or dual gates.
