# SHE Dashboard Index

This is the navigation entry point for the SHE dashboard contract and its surrounding evidence/visualization surfaces.

## Product contracts

- SHE-DASHBOARD-PRD.md — product, evidence hierarchy, information architecture, deployment and acceptance contract.
- SHE-DASHBOARD-SNAPSHOT-CONTRACT.md — machine-facing snapshot schema and provenance rules.
- SHE-DASHBOARD-UI-UX-CONTROL-PLANE.md — implementation-ready interactive UI/UX, responsive behavior, accessibility, surface matrix, and promotion gates.
- SHE-DASHBOARD-ARCHITECTURE.mmd — authoritative architecture source.

## Trigger and workflow registry

- TRIGGER-WORKFLOW-REGISTRY.md — human-readable entry-method, trigger, selector, QUE admission, workflow, and feed map.
- TRIGGER-WORKFLOW-REGISTRY.json — machine-readable registry (`trigger-workflow-registry/v1`).
- ISSUE-TEMPLATE-CENSUS.md — source-derived census of all 14 YAML issue forms.
- `generated/issue-template-census.json` — machine-readable template census with source blob SHAs.
- WORKFLOW-TRIGGER-CENSUS.md — source-verified selected workflow event/selector examples.
- `generated/workflow-trigger-census.json` — machine-readable workflow trigger exemplars with source blob SHAs.
- LABEL-CONSUMER-CENSUS.md — source-backed label producers, selectors, queue states, and consumers.
- `generated/label-consumer-census.json` — machine-readable label relationship records and coverage limits.
- The registry indexes (and does not duplicate) the generated 331-workflow catalog at `docs/ops/generated/automation-workflow-catalog.json`.

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
| Relationships | Researcher/Forensic | corpus + temporal snapshots |
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