# Workspace Artifact Triage

| Field | Value |
|---|---|
| Type | process |
| Universe | leftover |
| Status | verified |
| Consumes | A scoped `workspace/` artifact request, the Workspace Artifact Estate card, and the smallest relevant owner source. |
| Produces | A human-reviewed classification and a separate cleanup, retention, or map-maintenance proposal when needed. |

## Inputs

| Source | Scope | Why |
|---|---|---|
| [`../objects/knowledge/workspace-artifact-estate.md`](../objects/knowledge/workspace-artifact-estate.md) | Full card | Defines catalog, factory, product, leftover, and excluded boundaries. |
| [`../maintenance/01_inventory/CONTEXT.md`](../maintenance/01_inventory/CONTEXT.md) | Inputs and process | Gives the bounded source-inventory protocol. |
| `workspace/README.md` or the relevant workspace README | Named folder only | Establishes the owner and declared purpose. |

## Process

1. Inventory the named paths without bulk-loading their contents.
2. Classify each as catalog/contract, factory, product, leftover, or excluded.
3. Confirm whether a maintained owner source or generator exists.
4. Create a map-maintenance proposal only for durable routing facts; create a separate cleanup proposal for deletion, archival, relocation, or code changes.
5. Stop for a human decision before any cleanup, data movement, or source modification.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Classification record | `maintenance/01_inventory/output/` | Markdown source inventory |
| Durable map change, if approved | `docs/icm/` | Card or route update |
| Cleanup/change proposal, if needed | `docs/proposals/active/` | Governed proposal item |

## First-order impact

**Hits:** workspace documentation, the map-maintenance pipeline, and the owning project’s governance record.
**Does not hit:** application code, generated products, sensitive runtime state, or `master` automatically.

## Human check

Confirm that no generated product was hand-edited, no excluded runtime material was opened or copied, and no cleanup/refactor proceeded without a separate approved proposal.
