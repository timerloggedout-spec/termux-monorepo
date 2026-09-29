# Gantt Dependency Phases and GitHub Actions–First Agentic Flow Design

**Status:** IMPLEMENTED (historical design record)
**Author (original):** Manus AI
**Upgrade note (2026-09-25):** This document is retained for provenance. The live system lives under [`docs/agentic/`](agentic/README.md). Do not treat this file as operational authority.

**Live SSOT**

| Artifact | Role |
|---|---|
| [`docs/agentic/README.md`](agentic/README.md) | Operator / agent entry for the dependency-phase system |
| [`docs/agentic/dependency-phases.json`](agentic/dependency-phases.json) | Canonical phase plan |
| [`docs/agentic/DEPENDENCY_PHASES.md`](agentic/DEPENDENCY_PHASES.md) | Generated status view (derived only) |
| [`docs/proposals/active/gantt-dependency-phases/`](proposals/active/gantt-dependency-phases/) | Proposal lifecycle |
| `.github/workflows/dependency-phase-*.yml` | Validate · evaluate · project-sync · dispatch |

**Original executive position (preserved)**

The monorepo introduced a **repository-native, declarative dependency-phase plan** as the authoritative state, with GitHub Actions as deterministic evaluator and dispatcher. Gantt / Mermaid / Markdown views are generated from that plan; they are never the source of truth.

> **Design rule (still in force):** Stable phase identities belong in version-controlled JSON/YAML. The Gantt representation is a derived view, never the authority that decides whether an agent may start work.

## Implementation evidence (post-design)

| Delivery | Evidence |
|---|---|
| Core engine + 4 workflows | PR #248 (merged) — Implements DPH-000..DPH-300 |
| Project reconciliation hardening | Follow-ups #252–#257 |
| Derived Gantt / waves projection | #717 + post-merge verify #774 |
| Live status (generated) | `docs/agentic/DEPENDENCY_PHASES.md` — DPH-000 **complete**, DPH-100 **ready** |

## What remains advisory

- Fork adapters (`gantt-cli_fork_agentic`, `GanTTY_fork`, Camshaft/GanttML) remain **inspiration / optional exporters** only. They are not control-plane authority.
- Terminal TUIs and renumbering ID schemes must not become stable phase keys.
- Any future visual board is local/ICM-CCTV style; network exposure is out of scope for the phase dispatcher.

## References (original + live)

- Live entry: [`docs/agentic/README.md`](agentic/README.md)
- Proposal: [`docs/proposals/active/gantt-dependency-phases/MANIFEST.md`](proposals/active/gantt-dependency-phases/MANIFEST.md)
- Process: [`docs/proposals/PROCESS.md`](proposals/PROCESS.md)
- CLAUDE.md primary entry + BIUDL / dual-gate rules

---

*Historical design body retained below for audit. Operational agents should load `docs/agentic/` first.*

<!-- BEGIN HISTORICAL DESIGN BODY (do not edit as authority) -->

The original design recommended a repository-native YAML/JSON plan, pure validator, read-only evaluator, controlled `repository_dispatch` agent launch, and derived Gantt export. That sequence was delivered via PR #248 and subsequent hardening. The status header and Live SSOT table above supersede any "no repository changes" language that previously appeared in this file.
