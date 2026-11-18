# ADE-SYNAPSE — Architecture Index

**ADE-SYNAPSE** is the proposed synthetic cognitive architecture for the Agentic Development Environment. It maps existing repository systems to brain-inspired functional roles, records incomplete coverage, and isolates new research and experiment lanes.

Start here: [Brain Architecture README](brain-architecture/README.md)

| Surface | Purpose |
|---|---|
| [Brain-region registry](brain-architecture/registry/brain-region-registry.json) | Machine-readable mapping, status, evidence paths, and gaps |
| [System model](brain-architecture/models/ade-synapse-model.md) | Six-plane architecture, signal flow, contracts, and safety |
| [Evolution roadmap](brain-architecture/roadmap/evolution-roadmap.md) | Staged implementation path and acceptance criteria |
| [Neuro-inspired research](brain-architecture/research/neuro-inspired-patterns.md) | Expansion hypotheses, candidate subsystems, and research guardrails |
| [Experiment lane](brain-architecture/experiments/README.md) | Controlled, reproducible evaluations |
| [Proposal lane](brain-architecture/proposals/README.md) | New subsystem proposals and review requirements |
| [Canonical Mermaid diagram](diagrams/ade-synapse-brain.mmd) | Editable source diagram |

## Naming

**ADE-SYNAPSE** = **Synthetic Neuro-Architecture for Planning, Adaptation, Navigation, Sensing, and Evolution**.

The name describes an engineering architecture, not consciousness or biological equivalence.

## Relationship to existing systems

SYNAPSE organizes and references existing manager orchestration, ICM/provider routing, Context Relationship Graph, GitHub Actions execution, SHE, ATES, and 3L0. It does not replace their source-of-truth contracts or introduce a second execution/telemetry authority.

## Status

This is a documentation-first architecture proposal. A registry entry marked `proposed` or `research` is not implemented. A `partial` entry means the existing system covers only part of the mapped function. Promotion requires evidence and explicit governance.
