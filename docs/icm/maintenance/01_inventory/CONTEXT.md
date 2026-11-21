# 01_inventory — classify sources for one map update

One job: turn a requested ICM-map update into a small inventory of authoritative sources, candidate cards, and explicit exclusions.

## Inputs

| Kind | Path | Why |
|---|---|---|
| Working | `output/request.md` | Captures the scoped map-update request before analysis. |
| Reference | [`../../_shared/source-inventory-template.md`](../../_shared/source-inventory-template.md) | Gives the inventory shape and file-role vocabulary. |
| Reference | [`../../_shared/maintenance-rules.md`](../../_shared/maintenance-rules.md) | Enforces the documentation-only and canonical-source boundaries. |
| Reference | [`../../CONTEXT.md`](../../CONTEXT.md) | Defines the System map's universes and reading protocol. |
| Governance | [`../../../../CLAUDE.md`](../../../../CLAUDE.md) and [`../../../../docs/proposals/registry.yaml`](../../../../docs/proposals/registry.yaml) | Establishes the authorized item, FA-ADE posture, and scope boundary. |

## Process

1. Record the requested scope in `output/request.md` when the request record is absent.
2. Copy the source-inventory template to `output/source-inventory.md`.
3. Classify only the minimum relevant sources as catalog, contract, factory, product, or dead.
4. Mark each source as live, leftover, or ghost; identify the canonical owner and cite the exact source location.
5. Identify the noun, process, or effect card to add, update, or leave as a stub.
6. Record exclusions, missing evidence, and unresolved source conflicts explicitly; mark source authority unknown until canonical evidence resolves it.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Request record | `output/request.md` | Markdown |
| Source inventory | `output/source-inventory.md` | Markdown table |

## Automated acceptance

- The request maps to an active/authorized proposal item or an explicitly permitted maintenance task.
- Every proposed fact has a canonical source or is labeled unknown/candidate.
- Roles, universes, owners, and exclusions are populated; keep sensitive/device/generated artifacts outside the live source set until evidence establishes their canonical role.
- The inventory is internally consistent and ready for design under automated acceptance criteria.

When authorization is missing, the requested scope exceeds the registered item, or source authority remains unresolved, record `BLOCKED` and the exact reason. Request human input for an actual authorization or policy boundary; use routine automated evaluation for other cases.
