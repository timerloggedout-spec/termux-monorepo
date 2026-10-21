# Interpretable Context Methodology Reference

| Field | Value |
|---|---|
| Type | object |
| Cluster | knowledge |
| Universe | live |
| Status | verified |
| Entity | The user-owned, pinned full ICM reference library at `refTemplates/smods/interpretable-context-methodology_fork` |

## What this is

The full methodology reference complements, rather than replaces, ICM Architect. **ICM Architect** supplies the compact skill, form-selection method, restructure audit, templates, and System-map walk test. **Interpretable Context Methodology** supplies the complete conventions, example workspaces, and workspace-builder that demonstrate how a repeatable, human-gated Pipeline is assembled.[1] [2]

Both submodules are reviewed references. Neither runs automatically, defines the monorepo’s application runtime, or authorizes source-code changes.

## Read when

Open this card when an editor needs to design a new recurring, human-reviewable workspace; evaluate a nested ICM Pipeline; compare the monorepo map to the full convention set; or customize a user-owned methodology reference before pinning its Gitlink.

## Integration rule

Use ICM Architect first to select the **smallest form that carries the work**. Use the full methodology reference only for detailed Pipeline conventions, example workspace structures, workspace-builder patterns, and validation expectations. Keep monorepo-specific rules in `docs/icm/`; do not copy third-party reference payload into the System map.

## First-order impact

**Hits:** ICM form selection, `docs/icm/maintenance/`, method coverage, and the custom-reference submodule manifest.
**Does not hit:** `workspace/` artifacts, application/runtime code, CI logic, or branch authority automatically.

## Evidence

[1] [`refTemplates/smods/icm-architect_fork/SKILL.md`](../../../../refTemplates/smods/icm-architect_fork/SKILL.md) defines the six forms and System-map method.
[2] [`refTemplates/smods/interpretable-context-methodology_fork/README.md`](../../../../refTemplates/smods/interpretable-context-methodology_fork/README.md) defines the five-layer structure, stage contracts, human-editable outputs, and workspace-builder.
