# 02_design — propose one map change

One job: convert an approved source inventory into a minimal, reviewable documentation proposal without editing source or advancing automatically.

## Inputs

| Kind | Path | Why |
|---|---|---|
| Working | `../01_inventory/output/source-inventory.md` | Defines the bounded source set and candidate card; created by the prior run stage. |
| Reference | [`../../_meta/schema.md`](../../_meta/schema.md) | Defines card types, universes, and verification status. |
| Reference | [`../../_templates/object.md`](../../_templates/object.md) and [`../../_templates/process.md`](../../_templates/process.md) | Provide the blank card shapes. |
| Reference | [`../../_shared/maintenance-rules.md`](../../_shared/maintenance-rules.md) | Keeps the proposal canonical, one-way, and documentation-only. |

## Process

1. Select one addition or revision from the inventory.
2. Write `output/map-change-proposal.md` with the proposed location, card type, source citations, first-order Hits/Does not hit, and links to update.
3. State every intended documentation file change and every explicitly excluded code/source file.
4. Do not modify the map until the proposal receives a human decision.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Map-change proposal | `output/map-change-proposal.md` | Markdown with source citations and change list |

## Human check

Approve, reject, or edit the proposal. Approval confirms the map shape and scope; it does not authorize source-code refactoring, device actions, or an automatic merge.
