# Repository Architecture Flow Modules

Root entry: [architecture.md](../../../architecture.md). Each module pairs a detailed mapping and editable Mermaid source.

| Module | Mapping | Diagram |
|---|---|---|
| Execution and Session Plane | [execution-session.md](execution-session.md) | [execution-session.mmd](execution-session.mmd) |
| Agent Orchestration and Provider Routing | [agent-orchestration.md](agent-orchestration.md) | [agent-orchestration.mmd](agent-orchestration.mmd) |
| Evidence and Telemetry Plane | [evidence-telemetry.md](evidence-telemetry.md) | [evidence-telemetry.mmd](evidence-telemetry.mmd) |
| Context Relationship and Historical Corpus | [context-historical.md](context-historical.md) | [context-historical.mmd](context-historical.mmd) |
| Dashboard, Snapshot and Surface Consumers | [dashboard-snapshots.md](dashboard-snapshots.md) | [dashboard-snapshots.mmd](dashboard-snapshots.mmd) |
| Legacy Local Snapshot Pipeline — Gap Audit | [legacy-snapshot-audit.md](legacy-snapshot-audit.md) | [legacy-snapshot-audit.mmd](legacy-snapshot-audit.mmd) |
| Architecture Governance and Versioning | [architecture-governance.md](architecture-governance.md) | [architecture-governance.mmd](architecture-governance.mmd) · generated SVG: ../generated/flows/architecture-governance.svg |

Connection vocabulary: connected = source verified; dangling = missing verified producer or consumer; siloed = distinct product with no demonstrated join; contract-only = spec without runtime proof; optional = conditional consumer; stale = outside freshness bound; unknown = evidence unavailable.

Snapshot envelope: source_sha, tree_sha when applicable, generated_at, generator version, input/manifest digest, coverage status and unresolved count. generated_at means actual generator execution time, not audit date or source commit time.
