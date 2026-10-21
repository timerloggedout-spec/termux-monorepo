# 01_inventory — classify sources for one map update

One job: turn a requested ICM-map update into a small inventory of authoritative sources, candidate cards, and explicit exclusions.

## Inputs

| Kind | Path | Why |
|---|---|---|
| Working | `output/request.md` | Captures the user’s map-update request in plain text before analysis. |
| Reference | [`../../_shared/source-inventory-template.md`](../../_shared/source-inventory-template.md) | Gives the inventory shape and file-role vocabulary. |
| Reference | [`../../_shared/maintenance-rules.md`](../../_shared/maintenance-rules.md) | Enforces the documentation-only and canonical-source boundaries. |
| Reference | [`../../CONTEXT.md`](../../CONTEXT.md) | Defines the System map’s universes and reading protocol. |

## Process

1. Write the requested scope into `output/request.md` if it is not already present.
2. Copy the source-inventory template to `output/source-inventory.md`.
3. Classify only the minimum relevant sources as catalog, contract, factory, product, or dead.
4. Mark each source as live, leftover, or ghost; name the source of truth and exclusions.
5. Identify the noun, process, or effect card that needs to be added, updated, or left as a stub.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Request record | `output/request.md` | Markdown |
| Source inventory | `output/source-inventory.md` | Markdown table |

## Human check

Read the inventory and confirm that its sources are sufficient, its exclusions are explicit, and no code, generated index, device state, or sensitive artifact has been pulled into scope.
