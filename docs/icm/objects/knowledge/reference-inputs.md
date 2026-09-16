# ICM Reference Inputs

| Field | Value |
|---|---|
| Type | object |
| Cluster | knowledge |
| Universe | live |
| Status | verified |
| Entity | The pinned external references that inform, but do not operate, the monorepo ICM workspace |

## What this is

The monorepo is the ICM workspace. Its own `docs/icm/` catalog, contracts, cards, process definitions, and maintenance Pipeline are the **operative** method. The four shallow submodules under `refTemplates/smods/` are read-only **reference inputs**: they supply a form-selection skill, full conventions/examples, layered-routing precedent, and an optional visual-review pattern. They do not run automatically, replace governance, or authorize code changes.

| Reference input | Use in this repository | Do not treat as |
|---|---|---|
| `icm-architect_fork` | Form selection, map audit, templates, and walk-test method | Runtime agent or source-of-truth monorepo policy |
| `interpretable-context-methodology_fork` | Full conventions, example workspaces, and workspace-builder patterns | A second live repository workspace |
| `content-agent-routing-promptbase_fork` | Precedent for Layer 0–3 routing, canonical sources, and one-way dependencies | A content-production dependency or copied documentation payload |
| `icm-cctv_fork` | Optional visual review, stage-card mirroring, and human checkpoint patterns | A mandatory renderer, a deployment target, or the primary stage-output store |

## Read when

Open this card when selecting a reference, updating a pinned fork, deciding whether a pattern belongs in `docs/icm/`, or considering an optional visual review surface.

## First-order impact

**Hits:** the custom-reference Gitlinks, the ICM map, method coverage, and the human review boundary.
**Does not hit:** application runtime, Termux MCP/device access, external service accounts, or a new deployment automatically.

## Evidence

[1] [`refTemplates/smods/icm-architect_fork/SKILL.md`](../../../../refTemplates/smods/icm-architect_fork/SKILL.md) defines the compact architecture method.
[2] [`refTemplates/smods/interpretable-context-methodology_fork/README.md`](../../../../refTemplates/smods/interpretable-context-methodology_fork/README.md) provides full conventions and example workspaces.
[3] [`refTemplates/smods/content-agent-routing-promptbase_fork/README.md`](../../../../refTemplates/smods/content-agent-routing-promptbase_fork/README.md) defines layered selective routing and canonical sources.
[4] [`refTemplates/smods/icm-cctv_fork/README.md`](../../../../refTemplates/smods/icm-cctv_fork/README.md) defines the optional visual layer and file-based checkpoint loop.
