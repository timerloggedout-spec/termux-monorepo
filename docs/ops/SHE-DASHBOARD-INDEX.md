# SHE Dashboard Index

This is the navigation entry point for the SHE dashboard contract and its surrounding evidence/visualization surfaces.

## Product contracts

- SHE-DASHBOARD-PRD.md — product, evidence hierarchy, information architecture, deployment and acceptance contract.
- SHE-DASHBOARD-SNAPSHOT-CONTRACT.md — machine-facing snapshot schema and provenance rules.
- SHE-DASHBOARD-UI-UX-CONTROL-PLANE.md — implementation-ready interactive UI/UX, responsive behavior, accessibility, surface matrix, and promotion gates.
- SHE-DASHBOARD-ARCHITECTURE.mmd — authoritative architecture source.
- TOROIDAL-DOMAIN-RELATIONSHIP-LAYER.md — optional cyclic/mirrored relationship projection, interaction model, evidence semantics, and acceptance gates.
- TOROIDAL-DOMAIN-RELATIONSHIP.schema.json — machine contract for toroidal relationship projection payloads.

## Visual pipeline

```text
.mmd
 ↓
deterministic renderer
 ↓
.png
 ↓
source/render hash manifest
 ↓
human review / UI architecture viewer
```

The existing automation-docs-continuous-refresh.yml + scripts/ci/automation_docs.py lane owns deterministic Mermaid rendering and generated-asset freshness.

The optional toroidal relationship explorer has its own source diagram at `diagrams/she-toroidal-domain-explorer.mmd`; it uses the existing rendering pipeline.

## Evidence pipeline

```text
GitHub truth
 ↓
Actions / collectors
 ↓
historical corpus + evidence
 ↓
SHE reducers
 ↓
versioned snapshot
 ↓
relationship projection adapter
 ↓
conventional graph OR toroidal explorer
 ↓
Vercel / Pages / Hex
```

## Runtime adapter boundary

```text
GitHub truth → Actions → SHE ───────► optional n8n
                                      │
                                      └─ visual/operator workflows
```

n8n is an adapter. It does not replace GitHub, Actions, SHE reducers, or the snapshot contract.

## UI surface map

| Surface | Primary user | Authority |
|---|---|---|
| Overview | Operator | SHE snapshot |
| Operations | Operator | GitHub/Actions evidence |
| Effectiveness | Operator/Researcher | derived metrics + evidence |
| Moneyball / 3L0 | Researcher | cohort snapshots |
| Experiments | Researcher | experiment records |
| Relationships | Researcher/Forensic | corpus + temporal snapshots; conventional and toroidal projections |
| Provenance | Forensic reviewer | exact evidence chain |
| Architecture | All | .mmd source + generated assets |
| Research | Researcher | explicitly classified research evidence |
| Settings / Surface Health | Operator | build/snapshot/adapter state |

## Non-negotiables

- Read-only projection; no dashboard-as-database.
- Missing evidence is not zero.
- Partial corpus is visible.
- COMMITTED, EXECUTED, VALIDATED, and PROMOTED remain distinct.
- Exact source SHA and snapshot identity are always recoverable.
- Hex is optional.
- n8n is optional.
- Render is not a free-scope dependency.
- Toroidal layout is optional and never changes canonical node/edge identity.
