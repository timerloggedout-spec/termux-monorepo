> **Non-canonical copy — retained in full (owner rule, 2026-11-01).** Canonical version: [`docs/research/FOSS-PROCUREMENT-MATRIX.md`](../research/FOSS-PROCUREMENT-MATRIX.md) — the machine-cited `procurement_contract`. The full pre-stub content of this file (blob `20d92ecaee5e2bc48d229a7b1cc419671370ca15`) is restored below; its unique material was also merged into the canonical file in PR #3259. Deletions and content-replacing stubs are prohibited — everything in this repo feeds ML pipelines; consolidation is additive pointers only.

# FOSS Research & Procurement Matrix

This matrix operationalizes FOSS-driven research/procurement for the monorepo.

## Required fields

| Field | Purpose |
|---|---|
| component | project/tool/model/runtime |
| category | agent, telemetry, runtime, benchmark, security, etc. |
| license | legal openness |
| source_repo | canonical upstream repository |
| source_type | project, paper, standard, release, dataset |
| maintenance_signal | release cadence / contributor activity |
| portability | ARM, Linux, Android, Termux, container, cloud |
| offline_capability | local/offline execution support |
| interoperability | APIs, MCP, OTEL, standard formats |
| reproducibility | pinned builds/images/data/evaluation |
| provenance | release/source/hash evidence |
| dependency_risk | critical external dependencies |
| lock_in_risk | provider/platform coupling |
| security_surface | secrets, network, permissions, execution |
| resource_cost | CPU/RAM/storage/network/energy |
| operational_fit | relationship to current monorepo workflows |
| horizon | H0/H1/H2/H3 |
| evidence_confidence | high/medium/low |
| decision | track / prototype / validate / procure / defer |

## Current research lanes

### P0 foundations

- OpenTelemetry — neutral telemetry/interoperability boundary.
- Docker — reproducible execution substrate.
- Complexity contract — explicit complexity plus structural fallback.

### P1 providers and reproduction

- Tree-sitter — language-neutral structural analysis.
- Langfuse — experiment/evaluation adapter.
- Phoenix — open-source tracing/evaluation adapter.
- Lizard — broad-language complexity features.
- Radon — Python complexity/Halstead/maintainability.
- Codespaces — interactive reproduction surface.

### P2 comparative research

- Multi-agent benchmark suites / MASEval-class research.
- Additional open benchmark and manager-tournament methods.

Vendor-specific persistence and UX remain adapters, never the canonical evidence store.

## Procurement rule

No component is selected from popularity alone. Preserve the raw evidence,
source/version, date observed, and unresolved risks so later decisions can be
recomputed without rewriting history.
